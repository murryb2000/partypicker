"""Regression checks for 1.2.0; run with QT_QPA_PLATFORM=offscreen."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
import soundfile as sf
from PySide6.QtCore import QSettings, QUrl
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtMultimedia import QMediaPlayer
from core import path_key, read_playlist, track_identity, preview_position, normalization_gain
from party_picker import Window, Analyze, Probe, Duplicates, TEXTS

APP = QApplication.instance() or QApplication([])


def wait_for(predicate, timeout=8):
    deadline = time.monotonic() + timeout
    while not predicate():
        APP.processEvents()
        if time.monotonic() > deadline:
            raise AssertionError('Background work timed out')
        time.sleep(.005)
    APP.processEvents()


class PlayerStub:
    def __init__(self, path, duration=60000):
        self.path, self.duration_ms, self.pos = path, duration, 0
    def source(self): return QUrl.fromLocalFile(str(self.path))
    def playbackState(self): return QMediaPlayer.PlayingState
    def duration(self): return self.duration_ms
    def position(self): return self.pos
    def isSeekable(self): return True
    def setPosition(self, value): self.pos = value
    def stop(self): pass
    def play(self): pass
    def mediaStatus(self): return QMediaPlayer.LoadedMedia


class PartyPickerTests(unittest.TestCase):
    def test_real_backend_preview_start_on_two_successive_tracks(self):
        for path in (self.a, self.b):
            sf.write(path, np.zeros(45 * 22050, dtype='float32'), 22050)
        self.w.preview_seconds.setValue(30)
        self.w.tracks = [self.a, self.b]
        for index, path in enumerate(self.w.tracks):
            self.w.play_track(index)
            wait_for(lambda: self.w.current_path() == path and self.w.pending_seek is None
                     and self.w.player.position() >= 29750, timeout=12)
            self.assertFalse(self.w.preview_muted)
            self.assertEqual(self.errors, [])


    def test_preview_waits_for_loaded_media_and_retries_reset_seek(self):
        self.stub(self.a)
        player = self.w.player
        state = {'status': QMediaPlayer.LoadingMedia, 'seekable': False}
        player.mediaStatus = lambda: state['status']
        player.isSeekable = lambda: state['seekable']
        self.w.pending_seek = 30000
        self.w.apply_preview_start()
        self.assertEqual(player.pos, 0)
        self.assertFalse(self.w.preview_started)
        state['status'] = QMediaPlayer.LoadedMedia
        self.w.apply_preview_start()
        self.assertFalse(self.w.preview_started)
        state['seekable'] = True
        self.w.apply_preview_start()
        self.assertEqual(player.pos, 30000)
        self.assertTrue(self.w.preview_muted)
        player.pos = 0  # Windows backend resets the first seek on startup.
        self.w.preview_seek_at -= 1
        self.w.apply_preview_start()
        self.assertEqual(player.pos, 30000)
        self.assertIsNotNone(self.w.pending_seek)
        self.w.preview_seek_at -= 1
        self.w.apply_preview_start()
        self.assertIsNone(self.w.pending_seek)
        self.assertFalse(self.w.preview_muted)
        self.assertGreater(self.w.audio.volume(), 0)

    def test_preview_zero_and_short_track(self):
        for duration, requested, expected in [(60000, 0, 0), (18000, 30000, 8000), (8000, 30000, 0)]:
            self.w.player = PlayerStub(self.a, duration)
            self.w.pending_seek = requested
            self.w.preview_started = False
            self.w.apply_preview_start()
            self.assertEqual(self.w.player.pos, expected)
            if expected:
                self.w.preview_seek_at -= 1
                self.w.apply_preview_start()
            self.assertIsNone(self.w.pending_seek)
            self.assertFalse(self.w.preview_muted)


    def test_manager_undo_restores_saved_order(self):
        self.w.playlist = self.root / 'manager.m3u'
        self.save([self.a, self.b])
        self.w.manager.reload()
        self.w.manager.reorder([self.b, self.a])
        wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        self.assertEqual(self.w.manager.model.entries, [self.b, self.a])
        self.assertTrue(self.w.manager.undo_button.isEnabled())
        self.w.manager.undo()
        wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        self.assertEqual(self.w.manager.model.entries, [self.a, self.b])
        self.assertEqual(read_playlist(self.w.playlist), [self.a, self.b])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.settings_patch = patch('party_picker.QSettings', lambda *_: QSettings(str(self.root/'settings.ini'), QSettings.IniFormat))
        self.settings_patch.start()
        self.w = Window()
        self.w.error = lambda message: self.errors.append(message)
        self.errors = []
        self.a, self.b = self.root/'Artist - Song.flac', self.root/'02. Artist - Song.flac'
        sf.write(self.a, np.sin(np.arange(22050) * .05).astype('float32') * .2, 22050)
        sf.write(self.b, np.zeros(22050, dtype='float32'), 22050)
    def tearDown(self):
        self.w.close()
        for player in self.w.findChildren(QMediaPlayer):
            player.stop()
            player.setSource(QUrl())
        APP.processEvents()
        self.settings_patch.stop()
        self.tmp.cleanup()
    def stub(self, path):
        self.w.player = PlayerStub(path)
        self.w.requested_folder_track = True
        self.w.tracks = [self.a, self.b]
        self.w.source_rows = {path_key(p): i for i,p in enumerate(self.w.tracks)}
        self.w.sources.addItems([p.stem for p in self.w.tracks])
        self.w.index = 0
    def save(self, entries, **kw):
        self.assertTrue(self.w.commit(entries, **kw))
        wait_for(lambda: self.w.pending_save is None)
        wait_for(lambda: not self.w.jobs)
    def test_preview_and_normalization(self):
        self.assertEqual(preview_position(30000, 60000), 30000)
        self.assertEqual(preview_position(30000, 18000), 8000)
        self.assertEqual(preview_position(30000, 8000), 0)
        self.assertEqual(normalization_gain(0, 0), 1)
        self.assertAlmostEqual(normalization_gain(.5, .8), .2)
        self.assertLessEqual(normalization_gain(.01, .99)*.99, .98)
        self.stub(self.a)
        self.w.pending_seek = 30000
        self.w.apply_preview_start()
        self.assertEqual(self.w.player.pos, 30000)
        self.w.preview_seek_at -= 1
        self.w.apply_preview_start()
        self.assertIsNone(self.w.pending_seek)
        self.w.track_gain = .5
        self.w.normalize.setChecked(True)
        self.assertAlmostEqual(self.w.audio.volume(), .325, places=5)
        self.w.volume_changed(50)
        self.assertAlmostEqual(self.w.audio.volume(), .25, places=5)
        self.w.normalize.setChecked(False)
        self.assertAlmostEqual(self.w.audio.volume(), .5, places=5)
    def test_artist_title_identity_and_duplicate_worker(self):
        with patch('core.TinyTag.get', return_value=SimpleNamespace(artist='  ARTIST ', title='Ｓｏｎｇ')):
            self.assertEqual(track_identity(self.a), ('artist', 'song'))
        self.assertEqual(track_identity(self.a), track_identity(self.b))
        self.assertIsNone(track_identity(self.root/'ambiguous.flac'))
        received = []
        job = Duplicates(self.b, [self.a], {}, True, self.w)
        job.result.connect(lambda *args: received.append(args))
        self.w.launch(job)
        wait_for(lambda: received)
        self.assertEqual(received[0][2], self.a)
        wait_for(lambda: not self.w.jobs)
    def test_history_colors_and_persistence(self):
        self.stub(self.a)
        self.w.update_source_colors()
        self.assertEqual(self.w.sources.item(1).foreground().color().name(), '#8c97a5')
        for v in (1000, 2000, 3000): self.w.position(v)
        self.assertEqual(self.w.sources.item(0).foreground().color().name(), '#8c97a5')
        self.w.play_track = lambda index: None
        self.w.step(1)
        self.assertEqual(self.w.sources.item(0).foreground().color().name(), '#ffb454')
        self.w.selected_keys.add(path_key(self.a))
        self.w.update_source_colors()
        self.assertEqual(self.w.sources.item(0).foreground().color().name(), '#36dab5')
        self.w.flush_history()
        other = Window()
        self.assertEqual(other.history[path_key(self.a)], 'skipped')
        other.close()
    def test_resume_missing_track_does_not_silently_play_first(self):
        files = [self.root / '01 - first.flac', self.root / '02 - second.flac']
        started = []
        self.w.play_track = lambda index: started.append(index)
        self.w.scanned(files, '', 0, str(self.root / 'other-folder' / '02 - second.flac'))
        self.assertEqual(started, [1])  # unique filename survives a changed drive root
        started.clear()
        self.w.scanned(files, '', 0, str(self.root / 'other-folder' / '03 - missing.flac'))
        self.assertEqual(started, [])
        self.assertIn('nicht gefunden', self.w.statusBar().currentMessage())
    def test_last_played_track_is_saved_before_async_probe(self):
        self.w.tracks = [self.a, self.b]
        self.w.sources.addItems([self.a.name, self.b.name])
        with patch.object(self.w, 'play_path') as play_path:
            self.w.play_track(1)
        self.assertEqual(self.w.settings.value('last_music_track'), str(self.b))
        play_path.assert_called_once_with(self.b, folder_track=True)
    def test_atomic_undo_add_remove_reorder_and_failure(self):
        target = self.root/'party.m3u8'
        self.save([], target=target)
        self.save([self.a], ui_change=('append', self.a))
        self.save([self.a, self.b], ui_change=('append', self.b))
        self.save([self.b, self.a], ui_change=('move', 1, 0))
        self.w.undo()
        wait_for(lambda: self.w.pending_save is None)
        wait_for(lambda: not self.w.jobs)
        self.assertEqual(read_playlist(target), [self.a, self.b])
        self.save([self.a], ui_change=('remove', 1))
        self.w.undo()
        wait_for(lambda: self.w.pending_save is None)
        wait_for(lambda: not self.w.jobs)
        self.assertEqual(read_playlist(target), [self.a, self.b])
        with patch('party_picker.save_playlist', side_effect=OSError('NAS offline')):
            self.w.undo()
            wait_for(lambda: self.w.pending_save is None)
            wait_for(lambda: not self.w.jobs)
        self.assertEqual(self.w.selected, [self.a, self.b])
        self.assertEqual(read_playlist(target), [self.a, self.b])
        self.assertTrue(self.errors)
        self.assertTrue(self.w.undo_stack)
        self.w.undo()
        wait_for(lambda: self.w.pending_save is None)
        wait_for(lambda: not self.w.jobs)
        self.assertEqual(read_playlist(target), [self.a])
        self.assertEqual(self.w.picks.count(), 1)
    def test_txt_undo_and_new_playlist_reset(self):
        target = self.root/'party.txt'
        self.w.text_cache[path_key(self.a)] = 'Artist - Song'
        self.save([], target=target)
        self.save([self.a], ui_change=('append', self.a))
        self.assertEqual(target.read_text().strip(), 'Artist - Song')
        self.w.undo()
        wait_for(lambda: self.w.pending_save is None)
        wait_for(lambda: not self.w.jobs)
        self.assertEqual(target.read_text(), '\n')
        self.save([self.a])
        self.save([], target=self.root/'other.txt')
        self.assertFalse(self.w.undo_stack)
    def test_probe_error_stale_and_worker_cleanup(self):
        messages = []
        self.w.show_playback_error = lambda *args: messages.append(args)
        missing = self.root/'missing.flac'
        self.w.play_path(missing, folder_track=True)
        wait_for(lambda: messages)
        self.assertEqual(messages[0][1], missing)
        wait_for(lambda: not self.w.jobs)
        token = self.w.play_token
        self.w.play_token += 1
        self.w.probed(token, self.a, None, '')
        self.assertIsNone(self.w.current_path())
        result = []
        job = Analyze(self.w.play_token, self.a, self.w)
        job.result.connect(lambda *args: result.append(args))
        self.w.analyzer = job
        self.w.launch(job)
        wait_for(lambda: result)
        wait_for(lambda: not self.w.jobs)
        self.assertIsNone(self.w.analyzer)
        self.assertGreater(len(result[0][2]), 0)
        self.assertEqual(result[0][-1], '')
    def test_rapid_song_changes_and_saved_resume(self):
        self.w.play_path(self.a, folder_track=True)
        self.w.play_path(self.b, folder_track=True)
        wait_for(lambda: not self.w.jobs)
        self.assertEqual(self.w.current_path(), self.b)
        self.assertEqual(self.w.settings.value('last_music_track'), str(self.b))
        for _ in range(3):
            self.w.play_path(self.a, folder_track=True)
            wait_for(lambda: not self.w.jobs)
            self.w.play_path(self.b, folder_track=True)
            wait_for(lambda: not self.w.jobs)
        self.assertIsNone(self.w.analyzer)
        self.assertFalse(self.w.findChildren(Analyze))
    def test_resume_last_folder_track_selects_and_scrolls_to_it(self):
        files = [self.root / f'{i:02d} - Artist - Song.flac' for i in range(40)]
        last_track = files[-3]
        self.w.tracks = files
        self.w.sources.resize(400, 200)
        self.w.show()
        APP.processEvents()
        with patch.object(self.w, 'play_path') as play_path:
            self.w.scanned(files, '', 0, str(last_track))
            APP.processEvents()
        expected_row = len(files) - 3
        self.assertEqual(self.w.index, expected_row)
        self.assertEqual(self.w.sources.currentRow(), expected_row)
        self.assertGreater(self.w.sources.verticalScrollBar().value(), 0)
        play_path.assert_called_once_with(last_track, folder_track=True)
    def test_duplicate_dialog_choices_and_network_retry(self):
        class AutoDialog(QMessageBox):
            choice = 'Trotzdem aufnehmen'
            def exec(self):
                self.chosen = next(b for b in self.buttons() if b.text() == self.choice)
                return 0
            def clickedButton(self): return self.chosen
        self.stub(self.b)
        self.w.playlist = self.root/'party.m3u8'
        self.w.selected = [self.a]
        self.w.selected_keys = {path_key(self.a)}
        self.w.refresh()
        # First button added by duplicate dialog is Add anyway.
        with patch('party_picker.QMessageBox', AutoDialog):
            self.w.duplicates_checked(self.b, [self.a], self.a, False, {})
        wait_for(lambda: self.w.pending_save is None)
        wait_for(lambda: not self.w.jobs)
        self.assertEqual(read_playlist(self.w.playlist), [self.a, self.b])
        self.w.selected = [self.a]
        self.w.selected_keys = {path_key(self.a)}
        AutoDialog.choice = 'Nicht aufnehmen'
        moves = []
        self.w.play_track = lambda i: moves.append(i)
        with patch('party_picker.QMessageBox', AutoDialog):
            self.w.duplicates_checked(self.b, [self.a], self.a, True, {})
        self.assertEqual(moves, [1])
        self.assertEqual(self.w.selected, [self.a])
        self.w.error_pending = self.w.play_token
        retries = []
        self.w.play_path = lambda path, folder: retries.append((path, folder))
        AutoDialog.choice = 'Erneut versuchen'
        with patch('party_picker.QMessageBox', AutoDialog):
            self.w.show_playback_error(self.w.play_token, self.b, 'NAS offline')
        self.assertEqual(retries, [(self.b, True)])
        AutoDialog.choice = 'Titel überspringen'
        with patch('party_picker.QMessageBox', AutoDialog):
            self.w.show_playback_error(self.w.play_token, self.b, 'NAS offline')
        self.assertEqual(moves, [1, 1])
        self.assertEqual(self.w.history[path_key(self.b)], 'skipped')

    def test_auto_advance_does_not_leave_playlist_preview(self):
        self.stub(self.a)
        self.w.requested_folder_track = False
        calls = []
        self.w.play_track = lambda index: calls.append(index)
        self.w.media_status(QMediaPlayer.EndOfMedia)
        APP.processEvents()
        self.assertEqual(calls, [])
        self.w.requested_folder_track = True
        self.w.media_status(QMediaPlayer.EndOfMedia)
        APP.processEvents()
        self.assertEqual(calls, [1])
        self.assertEqual(self.w.history[path_key(self.a)], 'skipped')

    def test_fullscreen_default_and_remembered_choice(self):
        self.w.show_startup_window(); APP.processEvents()
        self.assertTrue(self.w.isFullScreen())
        self.w.leave_fullscreen(); APP.processEvents()
        self.assertFalse(self.w.isFullScreen())
        self.assertTrue(self.w.isMaximized())
        self.assertFalse(self.w.settings.value('fullscreen', True, type=bool))
        other = Window()
        try:
            other.show_startup_window(); APP.processEvents()
            self.assertFalse(other.isFullScreen())
            self.assertTrue(other.isMaximized())
        finally:
            other.close(); APP.processEvents()
        self.w.toggle_fullscreen(); APP.processEvents()
        other = Window()
        try:
            other.show_startup_window(); APP.processEvents()
            self.assertTrue(other.isFullScreen())
        finally:
            other.close(); APP.processEvents()

    def test_fullscreen_shortcuts_in_picker_and_manager(self):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        self.w.show_startup_window()
        self.w.activateWindow(); APP.processEvents(); QTest.qWait(30)
        for manager in (False, True):
            if manager:
                self.w.show_manager()
            APP.processEvents()
            QTest.keyClick(self.w, Qt.Key_F11)
            wait_for(lambda: not self.w.isFullScreen(), timeout=2)
            QTest.keyClick(self.w, Qt.Key_F11)
            wait_for(self.w.isFullScreen, timeout=2)
            QTest.keyClick(self.w, Qt.Key_Escape)
            wait_for(lambda: not self.w.isFullScreen(), timeout=2)
            self.assertEqual(self.w.pages.currentIndex(), 1 if manager else 0)
            QTest.keyClick(self.w, Qt.Key_Escape); APP.processEvents()
            self.assertTrue(self.w.isVisible())
            self.w.toggle_fullscreen(); APP.processEvents()

    def test_translations_and_shortcuts(self):
        self.assertEqual(set(TEXTS['de']), set(TEXTS['en']))
        self.w.language_box.setCurrentIndex(1)
        self.assertEqual(self.w.undo_button.text(), 'Undo [Ctrl+Z]')
        self.assertEqual(self.w.normalize.text(), 'Match listening volume')
        self.assertTrue(any(s.key().toString() == 'Ctrl+Z' for s in self.w.keyboard_shortcuts))

if __name__ == '__main__': unittest.main()

