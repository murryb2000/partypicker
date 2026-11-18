"""Presentation changes must not change save/undo/drag semantics."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import json
from pathlib import Path
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QColor
from unittest.mock import patch
import unittest
import test_party_picker as fixture
APP, wait_for = fixture.APP, fixture.wait_for
from core import read_playlist
from playlist_manager import MIME


class VisualTests(unittest.TestCase):
    setUp = fixture.PartyPickerTests.setUp
    tearDown = fixture.PartyPickerTests.tearDown
    save = fixture.PartyPickerTests.save
    stub = fixture.PartyPickerTests.stub
    def test_drag_cancel_does_not_save_and_restores_selection(self):
        self.w.playlist = self.root / 'drag.m3u'
        entries = [self.a, self.b, self.root/'C.mp3', self.root/'D.mp3']
        self.save(entries)
        self.w.show(); APP.processEvents(); self.w.show_manager(); APP.processEvents()
        manager = self.w.manager
        manager.begin_drag([0, 2])
        self.assertEqual(manager.model.entries, entries)
        self.assertIsNone(manager.model.source_row(0))
        manager.model.collapse_drag()
        self.assertEqual(manager.model.rowCount(), 2)
        manager.model.show_gap(1)
        self.assertEqual(manager.model.rowCount(), 4)
        self.assertEqual(read_playlist(self.w.playlist), entries)
        self.assertIsNone(self.w.save_job)
        manager.end_drag([0, 2])
        self.assertIsNone(manager.model.projection)
        self.assertEqual(sorted(i.row() for i in manager.selection.selectedRows()), [0, 2])
        self.assertEqual(read_playlist(self.w.playlist), entries)
        wait_for(lambda: not manager.motion.isVisible())

    def test_drag_drop_saves_only_final_order_and_undo(self):
        self.w.playlist = self.root / 'drag.m3u'
        entries = [self.a, self.b, self.root/'C.mp3', self.root/'D.mp3']
        self.save(entries)
        self.w.manager.reload()
        manager = self.w.manager
        manager.begin_drag([0, 2])
        manager.model.collapse_drag()
        manager.model.show_gap(2)
        self.assertEqual(read_playlist(self.w.playlist), entries)
        mime = QMimeData(); mime.setData(MIME, json.dumps([0, 2]).encode())
        self.assertTrue(manager.model.dropMimeData(mime, Qt.MoveAction, 2, 0, manager.model.index(-1, 0)))
        manager.end_drag([0, 2])
        wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        expected = [entries[1], entries[3], entries[0], entries[2]]
        self.assertEqual(self.w.selected, expected)
        self.assertEqual(manager.model.entries, expected)
        self.assertEqual(read_playlist(self.w.playlist), expected)
        manager.undo()
        wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        self.assertEqual(read_playlist(self.w.playlist), entries)

    def test_failed_drag_save_rolls_back_projection(self):
        self.w.playlist = self.root / 'drag.m3u'
        self.save([self.a, self.b])
        manager = self.w.manager; manager.reload()
        manager.begin_drag([0]); manager.model.collapse_drag(); manager.model.show_gap(1)
        mime = QMimeData(); mime.setData(MIME, b'[0]')
        with patch('party_picker.save_playlist', side_effect=OSError('NAS offline')):
            manager.model.dropMimeData(mime, Qt.MoveAction, 2, 0, manager.model.index(-1, 0))
            manager.end_drag([0])
            wait_for(lambda: self.w.pending_save is None and not self.w.jobs)
        self.assertIsNone(manager.model.projection)
        self.assertEqual(manager.model.entries, [self.a, self.b])
        self.assertEqual(read_playlist(self.w.playlist), [self.a, self.b])
        self.assertTrue(self.errors)

    def test_visible_color_fades_retarget_without_changing_model_state(self):
        self.stub(self.a)
        self.w.show(); APP.processEvents()
        item = self.w.sources.item(0)
        item.setForeground(QColor('#8c97a5'))
        self.w.source_fade.change(item, '#36dab5')
        index = self.w.sources.indexFromItem(item)
        self.assertEqual(item.foreground().color().name(), '#36dab5')
        self.assertNotEqual(self.w.source_fade.color_at(index).name(), '#36dab5')
        self.w.source_fade.change(item, '#ffb454')
        self.assertEqual(item.foreground().color().name(), '#ffb454')
        wait_for(lambda: not self.w.source_fade.timer.isActive())
        self.assertEqual(self.w.source_fade.color_at(index).name(), '#ffb454')

    def test_visible_insert_remove_and_waveform_fades(self):
        self.w.show(); APP.processEvents()
        self.w.playlist = self.root/'fade.m3u'
        self.save([self.a], ui_change=('append', self.a))
        self.assertEqual(self.w.picks.count(), 1)
        self.assertTrue(self.w.pick_motion.frames)
        self.save([], ui_change=('remove', 0))
        self.assertEqual(self.w.picks.count(), 0)
        self.assertEqual(read_playlist(self.w.playlist), [])
        wait_for(lambda: not self.w.pick_motion.isVisible())
        old = self.w.wave_fade.capture()
        self.w.wave.peaks = [.4] * 200
        self.w.wave_fade.start(old)
        self.assertTrue(self.w.wave_fade.isVisible())
        self.w.wave.seek.emit(.5) # The overlay must not consume seeking.
        wait_for(lambda: not self.w.wave_fade.isVisible())

