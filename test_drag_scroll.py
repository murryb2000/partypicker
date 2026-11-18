"""Internal drag regression, physical screen edges and stationary scrolling."""
import os
import sys
import subprocess
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from drag_scroll import EdgePosition

APP = QApplication.instance() or QApplication([])


class DragScrollTests(unittest.TestCase):
    def test_physical_sample_scrolls_and_stops_at_exactly_ten_pixels(self):
        from playlist_manager import PlaylistManager
        manager = PlaylistManager(SimpleNamespace(lang='de', user_volume=.5, show_picker=lambda: None))
        self.addCleanup(manager.close)
        self.addCleanup(manager.stop)
        manager.model.reset_entries([Path(f'/track-{i}.mp3') for i in range(250)])
        manager.resize(1000, 700); manager.show(); APP.processEvents()
        manager.scroll.setValue(20)
        view = manager.views[0]
        key = ('win32', 1)
        def poll(y, seconds, monitor=key):
            with patch('playlist_manager.edge_position', return_value=EdgePosition(monitor, y, -1504, -1)), \
                 patch('playlist_manager.time.monotonic', return_value=seconds):
                view.poll_drag_edge()
        poll(-1, 100); poll(-1, 101)
        self.assertEqual(manager.scroll.value(), 24)
        poll(-10, 101.5)  # Nine physical pixels away, still latched.
        self.assertEqual(view.edge_direction, 1)
        poll(-11, 102)  # Ten pixels: stop and reset acceleration.
        stopped = manager.scroll.value()
        poll(-11, 103)
        self.assertEqual(view.edge_direction, 0)
        self.assertEqual(manager.scroll.value(), stopped)
        poll(-2, 104)  # Merely near the edge must not start it.
        self.assertEqual(view.edge_direction, 0)
        poll(-1504, 105); poll(-1504, 106)
        self.assertEqual(manager.scroll.value(), stopped - 4)
        poll(-1495, 106.5, ('win32', 2))  # Changing monitor clears the latch.
        self.assertEqual(view.edge_direction, 0)

    @unittest.skipUnless(sys.platform == 'win32', 'Windows input and physical screen edges')
    def test_internal_windows_drag_at_200_percent_with_stationary_cursor(self):
        script = r'''
import ctypes
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from PySide6.QtCore import Qt, QItemSelectionModel, QPoint
from PySide6.QtGui import QCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from playlist_manager import PlaylistManager
from drag_scroll import WINDOWS, edge_position

app = QApplication([]); app.setStyle('Fusion')
app.setStyleSheet('QWidget { font-size:13px; }')
manager = PlaylistManager(SimpleNamespace(lang='de', user_volume=.5, show_picker=lambda: None))
manager.resize(900, 600); manager.show(); app.processEvents()
entries = [Path(f'/track-{i}.mp3') for i in range(300)]
manager.model.reset_entries(entries); app.processEvents()
manager.scroll.setValue(50)
view = manager.views[0]
manager.selection.select(manager.model.index(50, 0), QItemSelectionModel.ClearAndSelect)
user = WINDOWS.user32
original = WINDOWS.POINT(); user.GetCursorPos(ctypes.byref(original))
info = WINDOWS.MonitorInfo(); info.cbSize = ctypes.sizeof(info)
monitor = user.MonitorFromPoint(original, 2)
assert user.GetMonitorInfoW(monitor, ctypes.byref(info))
rect = info.monitor
x = (rect.left + rect.right)//2
middle = (rect.top + rect.bottom)//2
user.SetCursorPos(x, middle)
assert manager.devicePixelRatioF() >= 1.99
phase = {'name': 'start'}
samples = []
view.scroll_requested.connect(lambda delta: samples.append((phase['name'], delta, time.monotonic())))
errors = []
stop_at = []
def controller():
    try:
        time.sleep(.4)
        user.SetCursorPos(x, rect.bottom-1); phase['name'] = 'bottom'
        time.sleep(2.2)  # No mouse movement: heartbeat and acceleration must continue.
        user.SetCursorPos(x, rect.bottom-10); phase['name'] = 'nine'
        time.sleep(.5)
        user.SetCursorPos(x, rect.bottom-11); phase['name'] = 'ten'
        stop_at.append(time.monotonic())
        time.sleep(.5)
        user.SetCursorPos(x, rect.top); phase['name'] = 'top'
        time.sleep(1.1)
        user.SetCursorPos(x, rect.top+20); phase['name'] = 'middle'
        time.sleep(.2)
    except BaseException as exc:
        errors.append(repr(exc))
    finally:
        user.keybd_event(0x1B, 0, 0, 0)  # Escape cancels instead of saving a drop.
        user.keybd_event(0x1B, 0, 2, 0)
        user.mouse_event(0x0004, 0, 0, 0, 0)

QCursor.setPos(view.viewport().mapToGlobal(QPoint(12, 12)))
app.processEvents()
user.mouse_event(0x0002, 0, 0, 0, 0)
app.processEvents()
# CI native input delivery is asynchronous; seed Qt's button state through
# its window-system test API while the real Windows button is also held.
QTest.mousePress(manager.windowHandle(), Qt.LeftButton, Qt.NoModifier,
                 manager.mapFromGlobal(view.viewport().mapToGlobal(QPoint(12, 12))))
manager.selection.select(manager.model.index(50, 0), QItemSelectionModel.ClearAndSelect)
thread = threading.Thread(target=controller, daemon=True)
thread.start()
held = user.GetAsyncKeyState(1)
started = time.monotonic()
try:
    view.startDrag(Qt.MoveAction)
    elapsed = time.monotonic()-started
finally:
    user.mouse_event(0x0004, 0, 0, 0, 0)
    thread.join(timeout=8)
    user.SetCursorPos(original.x, original.y)
assert not thread.is_alive() and not errors, errors
assert sum(delta for name, delta, _ in samples if name == 'bottom') >= 8, (samples, elapsed, held)
assert any(name == 'nine' and delta > 0 for name, delta, _ in samples), samples
assert not any(name == 'ten' and t > stop_at[0]+.1 for name, delta, t in samples), samples
assert any(name == 'top' and delta < 0 for name, delta, _ in samples), samples
assert not view.edge_timer.isActive()
assert manager.model.entries == entries and manager.model.projection is None
manager.stop(); manager.close(); app.processEvents()
print('Internal stationary Windows drag: bottom, nine-pixel latch, ten-pixel stop, top and cleanup OK')
'''
        result = subprocess.run([sys.executable, '-c', script], cwd=Path(__file__).parent,
            env=dict(os.environ, QT_QPA_PLATFORM='windows', QT_SCALE_FACTOR='2'),
            text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


import test_party_picker as fixture
from PySide6.QtCore import Qt, QPoint, QItemSelectionModel
from PySide6.QtTest import QTest


class InternalDragTests(unittest.TestCase):
    setUp = fixture.PartyPickerTests.setUp
    tearDown = fixture.PartyPickerTests.tearDown
    save = fixture.PartyPickerTests.save
    stub = fixture.PartyPickerTests.stub

    def prepare(self):
        self.w.playlist = self.root / 'internal-drag.m3u'
        entries = [self.a, self.b] + [self.root/f'{i}.mp3' for i in range(6)]
        self.save(entries)
        self.w.show(); APP.processEvents(); self.w.show_manager(); APP.processEvents()
        manager = self.w.manager
        for row in (0, 2):
            manager.selection.select(manager.model.index(row, 0), QItemSelectionModel.Select)
        return manager, entries

    def test_escape_cancels_internal_drag_and_restores_selection(self):
        manager, entries = self.prepare()
        QTimer.singleShot(60, lambda: QTest.keyClick(manager, Qt.Key_Escape))
        manager.views[0].startDrag(Qt.MoveAction)
        self.assertEqual(manager.model.entries, entries)
        self.assertIsNone(manager.model.projection)
        self.assertEqual(sorted(i.row() for i in manager.selection.selectedRows()), [0, 2])
        self.assertFalse(manager.views[0].edge_timer.isActive())

    def test_release_in_other_column_saves_once_and_undo_restores(self):
        from core import read_playlist
        manager, entries = self.prepare()
        target = manager.views[1].viewport()
        QTimer.singleShot(60, lambda: QTest.mouseRelease(target, Qt.LeftButton, Qt.NoModifier,
                                                        QPoint(20, target.height()-5)))
        manager.views[0].startDrag(Qt.MoveAction)
        fixture.wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        expected = [entry for i, entry in enumerate(entries) if i not in (0, 2)] + [entries[0], entries[2]]
        self.assertEqual(read_playlist(self.w.playlist), expected)
        self.assertEqual(manager.model.entries, expected)
        self.assertFalse(manager.views[0].edge_timer.isActive())
        manager.undo()
        fixture.wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        self.assertEqual(read_playlist(self.w.playlist), entries)
