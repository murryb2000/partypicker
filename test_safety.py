"""Regression checks for the 2.1.8 robustness fixes."""
import threading
import time
import unittest
from unittest.mock import patch
import numpy as np
import soundfile as sf
from PySide6.QtCore import QTimer
import test_party_picker as fixture
from party_picker import Analyze, Probe
from core import save_playlist, read_playlist, path_key

APP, wait_for = fixture.APP, fixture.wait_for


class SafetyTests(unittest.TestCase):
    setUp = fixture.PartyPickerTests.setUp
    tearDown = fixture.PartyPickerTests.tearDown
    stub = fixture.PartyPickerTests.stub

    def delayed_save(self, navigate):
        self.stub(self.a)
        self.w.tracks.append(self.root/'third.flac')
        self.w.sources.addItem('third')
        self.w.playlist = self.root/'party.m3u'
        started, release = threading.Event(), threading.Event()
        def delayed(path, entries):
            started.set(); release.wait(4); save_playlist(path, entries)
        def play(path, folder_track=False):
            self.w.play_token += 1
            self.w.player.path = path
        try:
            with patch('party_picker.save_playlist', side_effect=delayed), patch.object(self.w, 'play_path', play):
                self.w.duplicates_checked(self.a, [], None, True, {})
                wait_for(started.is_set)
                if navigate:
                    self.w.step(1)
                release.set()
                wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
                self.assertEqual(self.w.index, 1)
                self.assertEqual(read_playlist(self.w.playlist), [self.a])
        finally:
            release.set()

    def test_save_completion_does_not_advance_again_after_navigation(self):
        self.delayed_save(True)

    def test_save_completion_still_advances_without_navigation(self):
        self.delayed_save(False)

    def test_blocked_probes_are_bounded_and_only_latest_waits(self):
        release = threading.Event()
        started = []
        def blocked(job):
            started.append(job.token)
            release.wait(4)
        try:
            with patch.object(Probe, 'run', blocked):
                for i in range(20):
                    self.w.play_path(self.root/f'{i}.flac', True)
                wait_for(lambda: len(started) == 2)
                self.assertEqual(len(self.w.jobs), 2)
                self.assertEqual(len(self.w.pending_reads), 1)
                latest = self.w.play_token
                release.set()
                wait_for(lambda: not self.w.jobs and not self.w.pending_reads)
                self.assertEqual(sorted(started[:2]), [1, 2])
                self.assertEqual(started[2:], [latest])
        finally:
            release.set()

    def test_slow_import_keeps_gui_alive_and_ignores_stale_result(self):
        started, release = threading.Event(), threading.Event()
        old = self.root/'old.m3u'
        new = self.root/'new.m3u'
        save_playlist(new, [self.b])
        def delayed(path):
            if path == old:
                started.set(); release.wait(4)
                return [self.a]
            return read_playlist(path)
        completed = []
        try:
            with patch('party_picker.read_playlist', side_effect=delayed):
                self.assertTrue(self.w.load_playlist(old, on_success=lambda: completed.append('old')))
                wait_for(started.is_set)
                heartbeat = []
                QTimer.singleShot(0, lambda: heartbeat.append(True))
                wait_for(lambda: heartbeat)
                self.assertTrue(self.w.loading_playlist)
                self.assertFalse(self.w.commit([]))
                self.assertTrue(self.w.load_playlist(new, on_success=lambda: completed.append('new')))
                wait_for(lambda: not self.w.loading_playlist)
                release.set()
                wait_for(lambda: not self.w.jobs)
                self.assertEqual(self.w.selected, [self.b])
                self.assertEqual(completed, ['new'])
        finally:
            release.set()

    def test_import_error_retains_playlist_and_restores_buttons(self):
        self.w.playlist = self.root/'original.m3u'
        self.w.selected = [self.a]
        self.w.load_playlist(self.root/'missing.m3u')
        wait_for(lambda: not self.w.loading_playlist and not self.w.jobs)
        self.assertEqual(self.w.selected, [self.a])
        self.assertTrue(self.w.open_playlist_button.isEnabled())
        self.assertTrue(self.w.manager.isEnabled())
        self.assertTrue(self.errors)

    def test_txt_session_import_is_checked_in_background(self):
        target = self.root/'party.txt'
        target.write_text('Artist - Song\n', encoding='utf-8')
        session = {'entries':[str(self.a)], 'labels':{path_key(self.a):'Artist - Song'}}
        self.w.load_playlist(target, session)
        wait_for(lambda: not self.w.loading_playlist and not self.w.jobs)
        self.assertEqual(self.w.selected, [self.a])
        target.write_text('changed\n', encoding='utf-8')
        self.w.load_playlist(target, session)
        wait_for(lambda: not self.w.loading_playlist and not self.w.jobs)
        self.assertEqual(self.w.selected, [self.a])
        self.assertIn('TXT', self.errors[-1])

    def test_forged_flac_header_cannot_control_read_buffer(self):
        path = self.root/'forged.flac'
        sf.write(path, np.zeros(4410), 44100)
        raw = bytearray(path.read_bytes())
        value = int.from_bytes(raw[18:26], 'big')
        raw[18:26] = ((value & ~((1 << 36)-1)) | ((1 << 36)-1)).to_bytes(8, 'big')
        path.write_bytes(raw)
        sizes = []
        real_read = sf.SoundFile.read
        def read(audio, frames=-1, *args, **kwargs):
            sizes.append(frames)
            if not 0 < frames <= 4096:
                raise AssertionError('Unbounded audio buffer')
            return real_read(audio, frames, *args, **kwargs)
        result = []
        job = Analyze(1, path, self.w)
        job.result.connect(lambda *args: result.append(args))
        with patch.object(sf.SoundFile, 'read', read):
            job.run()
        self.assertTrue(sizes)
        self.assertLessEqual(len(sizes), 4)
        # Some libsndfile versions reject the forged header during seeking;
        # others reach EOF. Both must return safely without a large buffer.
        self.assertEqual(len(result), 1)
        self.assertNotIn('Unbounded audio buffer', result[0][-1])
        self.assertLessEqual(len(result[0][2]), 1600)


if __name__ == '__main__':
    unittest.main()
