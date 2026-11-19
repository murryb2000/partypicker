"""Duration summaries and bounded, recoverable playlist snapshots."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QItemSelectionModel, QTimer
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


if __name__ == '__main__':
    unittest.main()
