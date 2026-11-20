import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
import time
from unittest.mock import patch
from PySide6.QtCore import QPoint
from PySide6.QtMultimedia import QMediaPlayer
import test_party_picker as fixture
from core import path_key, read_playlist

APP, wait_for = fixture.APP, fixture.wait_for


class StatusFilterTests(unittest.TestCase):
    setUp = fixture.PartyPickerTests.setUp
    tearDown = fixture.PartyPickerTests.tearDown

    def prepare(self):
        w = self.w
        files = [self.a, self.b] + [self.root/f'{i}.flac' for i in range(2, 6)]
        w.tracks = files
        w.sources.addItems([p.name for p in files])
        w.source_rows = {path_key(p): i for i, p in enumerate(files)}
        w.selected = [files[2]]
        w.selected_keys = {path_key(files[2])}
        w.history = {path_key(files[1]): 'skipped', path_key(files[4]): 'heard'}
        w.playlist = self.root/'party.m3u'
        w.player = fixture.PlayerStub(files[0])
        w.requested_folder_track = True
        def play(path, folder_track=False):
            w.play_token += 1
            w.player.path = path
            w.requested_folder_track = folder_track
        w.play_path = play
        w.index = 0
        w.update_source_colors(animate=False)
        return files

    def choose(self, mode):
        self.w.status_filter.setCurrentIndex(self.w.status_filter.findData(mode))

    def shown(self):
        return [row for row in range(self.w.sources.count()) if not self.w.sources.item(row).isHidden()]

    def test_all_four_choices_and_green_precedence(self):
        files = self.prepare()
        for mode, expected in [('none', [0,1,2,3,4,5]), ('unheard', [0,3,5]),
                               ('skipped', [1,4]), ('both', [0,1,3,4,5])]:
            self.choose(mode)
            self.assertEqual(self.shown(), expected)
        self.w.selected_keys.add(path_key(files[1]))
        self.w.update_source_colors()
        self.assertEqual(self.shown(), [0,3,4,5])
        self.assertEqual(self.w.sources.item(1).foreground().color().name(), '#36dab5')
        self.w.selected_keys.remove(path_key(files[1]))
        self.w.update_source_colors()
        self.assertIn(1, self.shown())

    def test_manual_navigation_and_end_of_filtered_queue(self):
        files = self.prepare()
        self.choose('unheard')
        self.w.step(1)
        self.assertEqual(self.w.index, 3)
        self.assertEqual(self.w.current_path(), files[3])
        self.assertEqual(self.shown(), [3,5])
        self.w.play_track(5)
        self.w.step(-1)
        self.assertEqual(self.w.index, 3)
        self.assertEqual(self.shown(), [3])
        self.w.step(1)
        self.assertEqual(self.shown(), [])
        self.assertIn('Keine weiteren Titel', self.w.statusBar().currentMessage())

    def test_automatic_end_and_add_advance_use_filter(self):
        files = self.prepare()
        self.choose('unheard')
        self.w.media_status(QMediaPlayer.EndOfMedia)
        APP.processEvents()
        self.assertEqual(self.w.index, 3)
        snapshot = list(self.w.selected)
        self.w.duplicates_checked(files[3], snapshot, None, True, {})
        wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        self.assertEqual(self.w.index, 5)
        self.assertEqual(read_playlist(self.w.playlist), [files[2], files[3]])
        self.assertEqual(self.shown(), [5])

    def test_filter_change_keeps_playback_and_persists_in_both_languages(self):
        files = self.prepare()
        token = self.w.play_token
        self.choose('skipped')
        self.assertEqual(self.w.current_path(), files[0])
        self.assertEqual(self.w.play_token, token)
        self.choose('both')
        self.w.language_box.setCurrentIndex(1)
        self.assertEqual(self.w.status_filter.currentData(), 'both')
        self.assertEqual([self.w.status_filter.itemText(i) for i in range(4)], ['None','Unheard','Skipped','Both'])
        self.w.settings.sync()
        other = fixture.Window()
        try:
            self.assertEqual(other.status_filter.currentData(), 'both')
        finally:
            other.close(); APP.processEvents()

    def test_scan_skips_filtered_resume_and_does_not_start_if_no_matches(self):
        files = self.prepare()
        self.choose('unheard')
        self.w.scanned(files, '', 0, str(files[1]))
        self.assertEqual(self.w.index, 3)
        self.w.selected_keys = {path_key(p) for p in files}
        with patch.object(self.w, 'play_path') as play:
            self.w.scanned(files, '', 0)
            play.assert_not_called()
        self.assertEqual(self.shown(), [])
        self.assertIn('Keine weiteren Titel', self.w.statusBar().currentMessage())

    def test_position_uses_three_visible_preceding_tracks(self):
        self.w.show(); APP.processEvents()
        files = [self.root/f'{i:02}.flac' for i in range(60)]
        self.w.tracks = files
        self.w.sources.addItems([p.name for p in files])
        self.w.source_rows = {path_key(p): i for i,p in enumerate(files)}
        self.w.history = {path_key(p):'skipped' for i,p in enumerate(files) if i % 2}
        self.choose('unheard')
        with patch.object(self.w, 'play_path'):
            self.w.play_track(20)
        APP.processEvents()
        self.assertEqual(self.w.sources.indexAt(QPoint(2,2)).row(), 14)
        self.assertEqual(self.w.sources.currentRow(), 20)

    def test_large_folder_filter_changes_remain_responsive(self):
        files = [self.root/f'{i:04}.flac' for i in range(6000)]
        self.w.tracks = files
        self.w.sources.addItems([p.name for p in files])
        self.w.history = {path_key(p):'skipped' for i,p in enumerate(files) if i % 2}
        self.w.show(); APP.processEvents()
        start = time.monotonic()
        self.choose('unheard')
        self.assertLess(time.monotonic() - start, 5)
        self.assertEqual(len(self.shown()), 3000)


if __name__ == '__main__':
    unittest.main()
