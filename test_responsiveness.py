import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import threading
import time
from pathlib import Path
from unittest.mock import patch
import unittest
from PySide6.QtCore import QTimer
import test_party_picker as fixture
from core import read_playlist, save_playlist

APP, wait_for = fixture.APP, fixture.wait_for


class ResponsivenessTests(unittest.TestCase):
    setUp = fixture.PartyPickerTests.setUp
    tearDown = fixture.PartyPickerTests.tearDown
    save = fixture.PartyPickerTests.save

    def test_large_folder_display_does_not_repeatedly_relayout(self):
        self.w.show(); APP.processEvents()
        self.w.play_track = lambda *_: None
        files = [Path('/music/album') / f'{i:05d} - Artist - Song.flac' for i in range(6000)]
        start = time.monotonic()
        self.w.scanned(files, '', 0)
        self.assertLess(time.monotonic() - start, 5)
        self.assertEqual(self.w.sources.count(), 6000)
        self.assertEqual(self.w.sources.item(5999).foreground().color().name(), '#8c97a5')
        heartbeat = []
        QTimer.singleShot(0, lambda: heartbeat.append(True))
        APP.processEvents()
        self.assertTrue(heartbeat)

    def test_blocked_metadata_does_not_block_navigation_or_close(self):
        started, release = threading.Event(), threading.Event()
        def blocked_tag(*args, **kwargs):
            started.set(); release.wait(2)
            raise OSError('NAS unavailable')
        self.w.selected = [self.a]
        self.w.show(); APP.processEvents()
        try:
            with patch('playlist_manager.TinyTag.get', side_effect=blocked_tag):
                self.w.show_manager()
                wait_for(started.is_set)
                start = time.monotonic()
                self.w.show_picker()
                self.assertLess(time.monotonic() - start, 1)
                self.assertFalse(self.w.manager.metadata_active)
                start = time.monotonic()
                self.w.close()
                self.assertLess(time.monotonic() - start, 1)
                self.assertFalse(self.w.isVisible())
                release.set()
                wait_for(lambda: not self.w.manager.metadata_jobs)
                self.assertNotIn(str(self.a), self.w.manager.model.labels)
        finally:
            release.set()

    def test_close_allows_save_to_finish_without_blocking_event_loop(self):
        self.w.playlist = self.root / 'closing.m3u'
        started, release = threading.Event(), threading.Event()
        def blocked_save(path, entries):
            started.set(); release.wait(2); save_playlist(path, entries)
        self.w.show(); APP.processEvents()
        try:
            with patch('party_picker.save_playlist', side_effect=blocked_save):
                self.assertTrue(self.w.commit([self.a]))
                wait_for(started.is_set)
                start = time.monotonic()
                self.w.close()
                self.assertLess(time.monotonic() - start, 1)
                self.assertTrue(self.w._closing)
                self.assertTrue(self.w.isVisible())
                heartbeat = []
                QTimer.singleShot(0, lambda: heartbeat.append(True))
                APP.processEvents()
                self.assertTrue(heartbeat)
                release.set()
                wait_for(lambda: not self.w.isVisible())
                self.assertEqual(read_playlist(self.w.playlist), [self.a])
        finally:
            release.set()
            wait_for(lambda: not self.w.jobs)

    def test_failed_save_cancels_shutdown_and_keeps_window_usable(self):
        self.w.playlist = self.root / 'closing.m3u'
        started, release = threading.Event(), threading.Event()
        def fail_save(*args):
            started.set(); release.wait(2); raise OSError('NAS unavailable')
        self.w.show(); APP.processEvents()
        try:
            with patch('party_picker.save_playlist', side_effect=fail_save):
                self.assertTrue(self.w.commit([self.a]))
                wait_for(started.is_set)
                self.w.close()
                release.set()
                wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
                self.assertFalse(self.w._closing)
                self.assertTrue(self.w.isVisible())
                self.assertTrue(self.w.isEnabled())
                self.assertTrue(self.errors)
        finally:
            release.set()

    def test_process_can_exit_with_blocked_read_after_window_destruction(self):
        import subprocess
        import sys
        script = r'''
import os, threading, tempfile, time
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from unittest.mock import patch
from PySide6.QtCore import QSettings, QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication
from background_jobs import ReadJob
from party_picker import Window
app = QApplication([])
started = threading.Event()
class Blocked(ReadJob):
    def run(self):
        started.set()
        threading.Event().wait(60)
with tempfile.TemporaryDirectory() as tmp:
    with patch('party_picker.QSettings', lambda *_: QSettings(tmp+'/settings.ini', QSettings.IniFormat)):
        window = Window()
        job = Blocked(window)
        window.launch(job)
        deadline = time.monotonic() + 4
        while not started.is_set():
            app.processEvents()
            if time.monotonic() > deadline: raise RuntimeError('Read worker did not start')
        window.close()
        window.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        app.processEvents()
'''
        result = subprocess.run([sys.executable, '-c', script], cwd=Path(__file__).parent,
                                capture_output=True, text=True, timeout=12)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('QThread: Destroyed', result.stderr)
