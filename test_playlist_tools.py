"""Duration summaries and bounded, recoverable playlist snapshots."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QItemSelectionModel, QTimer
from PySide6.QtWidgets import QMessageBox
import test_party_picker as fixture
from core import (save_playlist, save_text_playlist, read_playlist, playlist_backups,
                  path_key, format_duration, track_duration)

APP, wait_for = fixture.APP, fixture.wait_for


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.target = self.root/'Party.m3u'

    def tearDown(self):
        self.tmp.cleanup()

    def test_keeps_three_previous_states_and_ignores_unchanged_save(self):
        save_playlist(self.target, [])
        self.assertEqual(playlist_backups(self.target), [])
        unrelated = self.root/'Party.m3u.backup-user.m3u'
        unrelated.write_text('keep me')
        for i in range(1, 6):
            save_playlist(self.target, [self.root/f'{i}.flac'])
        copies = playlist_backups(self.target)
        self.assertEqual(len(copies), 3)
        self.assertEqual([read_playlist(p) for p in copies], [[self.root/f'{i}.flac'] for i in (2, 3, 4)])
        save_playlist(self.target, [self.root/'5.flac'])
        self.assertEqual(playlist_backups(self.target), copies)
        self.assertEqual(unrelated.read_text(), 'keep me')

    def test_relative_paths_keep_their_meaning_in_backups(self):
        self.target.write_text('#EXTM3U\nalbum/song.flac\n', encoding='utf-8')
        save_playlist(self.target, [self.root/'new.flac'])
        backup = playlist_backups(self.target)[0]
        self.assertEqual(read_playlist(backup), [self.root/'album'/'song.flac'])

    def test_backup_failure_does_not_overwrite_existing_playlist(self):
        save_playlist(self.target, [self.root/'old.flac'])
        old = self.target.read_bytes()
        with patch('core.shutil.copyfileobj', side_effect=OSError('backup disk full')):
            with self.assertRaises(OSError):
                save_playlist(self.target, [self.root/'new.flac'])
        self.assertEqual(self.target.read_bytes(), old)
        self.assertEqual(list(self.root.glob('*.tmp')), [])
        self.assertEqual(playlist_backups(self.target), [])

    def test_failed_final_replace_preserves_original_and_backup(self):
        save_playlist(self.target, [self.root/'old.flac'])
        original = os.replace
        def fail(source, target):
            if Path(target) == self.target:
                raise OSError('replace failed')
            original(source, target)
        with patch('core.os.replace', side_effect=fail):
            with self.assertRaises(OSError):
                save_playlist(self.target, [self.root/'new.flac'])
        self.assertEqual(read_playlist(self.target), [self.root/'old.flac'])
        self.assertEqual(read_playlist(playlist_backups(self.target)[0]), [self.root/'old.flac'])

    def test_txt_backups_keep_original_text(self):
        target = self.root/'Titles.txt'
        entry = self.root/'song.flac'
        for i in range(5):
            save_text_playlist(target, [entry], {path_key(entry):f'Artist - Title {i}'})
        copies = playlist_backups(target)
        self.assertEqual(len(copies), 3)
        self.assertEqual([p.read_text().strip() for p in copies], [f'Artist - Title {i}' for i in (1, 2, 3)])


class DurationTests(unittest.TestCase):
    setUp = fixture.PartyPickerTests.setUp
    tearDown = fixture.PartyPickerTests.tearDown
    save = fixture.PartyPickerTests.save

    def test_real_audio_total_selection_and_translation(self):
        self.w.playlist = self.root/'party.m3u'
        self.save([self.a, self.b])
        wait_for(lambda: len(self.w.duration_cache) == 2)
        self.assertEqual(self.w.duration_display(self.w.selected), '00:00:02')
        self.assertIn('00:00:02', self.w.playlist_duration_label.text())
        self.w.manager.reload()
        manager = self.w.manager
        manager.selection.select(manager.model.index(0), QItemSelectionModel.Select)
        self.assertIn('1 markiert', manager.selection_duration.text())
        self.assertIn('00:00:01', manager.selection_duration.text())
        manager.selection.select(manager.model.index(1), QItemSelectionModel.Select)
        self.assertIn('00:00:02', manager.selection_duration.text())
        self.w.language_box.setCurrentIndex(1)
        self.assertIn('Playlist duration', self.w.playlist_duration_label.text())
        self.assertIn('2 selected', manager.selection_duration.text())
        self.w.picks.setCurrentRow(1)
        self.w.remove_pick()
        wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        self.assertIn('00:00:01', self.w.playlist_duration_label.text())

    def test_slow_duration_reads_leave_gui_responsive_and_unknown_explicit(self):
        entered, release = threading.Event(), threading.Event()
        def slow(path):
            entered.set(); release.wait(4)
            return 65 if path == self.a else None
        try:
            with patch('party_picker.track_duration', side_effect=slow):
                self.w.selected = [self.a, self.b]
                self.w.refresh_count()
                wait_for(entered.is_set)
                heartbeat = []
                QTimer.singleShot(0, lambda: heartbeat.append(True))
                wait_for(lambda: heartbeat)
                self.assertIn('werden ermittelt', self.w.playlist_duration_label.text())
                release.set()
                wait_for(lambda: not self.w.jobs)
                text = self.w.playlist_duration_label.text()
                self.assertIn('≥ 00:01:05', text)
                self.assertIn('1 unbekannt', text)
        finally:
            release.set()

    def test_invalid_durations_and_long_totals(self):
        for value in (None, -1, float('inf'), float('nan')):
            with patch('core.TinyTag.get') as get:
                get.return_value.duration = value
                self.assertIsNone(track_duration(self.a))
        self.assertEqual(format_duration(16*3600 + 35*60), '16:35:00')
        self.assertEqual(format_duration(100*3600), '100:00:00')


class ManagerRemovalTests(unittest.TestCase):
    setUp = fixture.PartyPickerTests.setUp
    tearDown = fixture.PartyPickerTests.tearDown
    save = fixture.PartyPickerTests.save

    def prepare(self, entries):
        self.w.playlist = self.root/'party.m3u'
        self.save(entries)
        self.w.manager.reload()
        return self.w.manager

    def select(self, manager, rows):
        manager.selection.clearSelection()
        for row in rows:
            manager.selection.select(manager.model.index(row), QItemSelectionModel.Select)

    def answer(self, yes, messages):
        def click():
            dialog = APP.activeModalWidget()
            messages.append(dialog.text())
            role = QMessageBox.AcceptRole if yes else QMessageBox.RejectRole
            for button in dialog.buttons():
                if dialog.buttonRole(button) == role:
                    button.click()
                    return
            raise AssertionError('Confirmation button missing')
        QTimer.singleShot(0, click)

    def test_group_remove_confirmation_backup_and_undo(self):
        third = self.root/'third.flac'
        third.write_bytes(self.a.read_bytes())
        entries = [self.a, self.b, third]
        manager = self.prepare(entries)
        self.assertFalse(manager.skip_remove_confirmation.isChecked())
        self.assertFalse(manager.remove_button.isEnabled())
        self.select(manager, [0, 2])
        self.assertTrue(manager.remove_button.isEnabled())
        messages = []
        self.answer(False, messages)
        manager.remove_selected()
        self.assertEqual(self.w.selected, entries)
        self.answer(True, messages)
        manager.remove_selected()
        wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        self.assertIn('2 markierten Titel', messages[-1])
        self.assertEqual(read_playlist(self.w.playlist), [self.b])
        self.assertEqual(manager.model.entries, [self.b])
        self.assertTrue(all(p.is_file() for p in entries))
        self.assertEqual(read_playlist(playlist_backups(self.w.playlist)[-1]), entries)
        manager.undo()
        wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        self.assertEqual(manager.model.entries, entries)
        self.assertEqual(read_playlist(self.w.playlist), entries)

    def test_single_remove_without_warning_and_persisted_option(self):
        manager = self.prepare([self.a, self.b])
        self.select(manager, [1])
        manager.skip_remove_confirmation.setChecked(True)
        with patch('playlist_manager.QMessageBox', side_effect=AssertionError('Unexpected warning')):
            manager.remove_button.click()
        wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        self.assertEqual(manager.model.entries, [self.a])
        self.assertTrue(self.b.is_file())
        self.w.settings.sync()
        other = fixture.Window()
        try:
            self.assertTrue(other.manager.skip_remove_confirmation.isChecked())
            other.language_box.setCurrentIndex(1)
            self.assertEqual(other.manager.remove_button.text(), 'Remove selected tracks')
            self.assertIn('Do not ask', other.manager.skip_remove_confirmation.text())
        finally:
            other.close(); APP.processEvents()

    def test_remove_all_and_reenable_confirmation(self):
        manager = self.prepare([self.a, self.b])
        manager.skip_remove_confirmation.setChecked(True)
        manager.skip_remove_confirmation.setChecked(False)
        self.select(manager, [0, 1])
        messages = []
        self.answer(True, messages)
        manager.remove_selected()
        wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        self.assertEqual(len(messages), 1)
        self.assertEqual(read_playlist(self.w.playlist), [])
        self.assertEqual(manager.model.entries, [])
        self.assertFalse(manager.remove_button.isEnabled())

    def test_failed_removal_preserves_entries_and_selection(self):
        manager = self.prepare([self.a, self.b])
        manager.skip_remove_confirmation.setChecked(True)
        self.select(manager, [0])
        with patch('party_picker.save_playlist', side_effect=OSError('NAS offline')):
            manager.remove_selected()
            wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        self.assertEqual(manager.model.entries, [self.a, self.b])
        self.assertEqual(read_playlist(self.w.playlist), [self.a, self.b])
        self.assertEqual([i.row() for i in manager.selection.selectedRows()], [0])
        self.assertTrue(manager.isEnabled())
        self.assertTrue(self.errors)


class ManagerPreviewTests(unittest.TestCase):
    setUp = fixture.PartyPickerTests.setUp
    tearDown = fixture.PartyPickerTests.tearDown

    def test_seek_pause_and_caps_lock_follow_on_real_audio(self):
        import numpy as np
        import soundfile as sf
        from PySide6.QtCore import Qt
        from PySide6.QtMultimedia import QMediaPlayer
        from PySide6.QtTest import QTest

        for path in (self.a, self.b):
            sf.write(path, np.zeros(40 * 22050, dtype='float32'), 22050)
        manager = self.w.manager
        self.w.selected = [self.a, self.b]
        self.w.show()
        self.w.show_manager()
        self.w.activateWindow()
        APP.processEvents()
        QTest.qWait(30)
        manager.preview_seconds.setValue(15)
        QTest.keyClick(manager.views[0], Qt.Key_CapsLock)
        wait_for(manager.preview_auto.isChecked)
        first, second = (manager.model.index(row) for row in (0, 1))
        selection = manager.selection
        selection.select(first, QItemSelectionModel.ClearAndSelect)
        QTest.qWait(150)
        self.assertTrue(manager.player.source().isEmpty())  # Still waiting for Play.
        manager.preview_button.click()

        def playing_at_offset(path):
            return (manager.player.source().toLocalFile() == str(path)
                    and manager.preview_seek is None
                    and manager.player.playbackState() == QMediaPlayer.PlayingState
                    and manager.player.position() >= 14900
                    and manager.audio.volume() > 0)

        wait_for(lambda: playing_at_offset(self.a), timeout=12)
        selection.select(second, QItemSelectionModel.ClearAndSelect)
        wait_for(lambda: playing_at_offset(self.b), timeout=12)
        selection.select(first, QItemSelectionModel.Select)
        wait_for(lambda: manager.player.playbackState() == QMediaPlayer.PausedState)
        self.assertEqual(manager.player.source().toLocalFile(), str(self.b))
        selection.select(second, QItemSelectionModel.ClearAndSelect)
        wait_for(lambda: playing_at_offset(self.b), timeout=12)
        manager.preview_button.click()
        wait_for(lambda: manager.player.playbackState() == QMediaPlayer.PausedState)
        selection.select(first, QItemSelectionModel.ClearAndSelect)
        QTest.qWait(200)
        self.assertEqual(manager.player.source().toLocalFile(), str(self.b))
        self.assertFalse(manager.preview_armed)
        self.w.language_box.setCurrentIndex(1)
        self.assertEqual(manager.preview_start_label.text(), 'Preview from:')
        self.assertIn('Caps Lock', manager.preview_auto.text())
        self.w.show_picker()
        self.assertTrue(manager.player.source().isEmpty())
        self.assertFalse(manager.preview_auto.isChecked())
        self.assertEqual(self.w.settings.value('manager_preview_seconds', type=int), 15)


if __name__ == '__main__':
    unittest.main()
