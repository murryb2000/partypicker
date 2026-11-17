import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PySide6.QtCore import Qt, QMimeData, QItemSelectionModel
from PySide6.QtWidgets import QApplication
from playlist_manager import PlaylistModel, Metadata, MIME, moved_entries, PlaylistManager

app = QApplication.instance() or QApplication([])

class ManagerTests(unittest.TestCase):
    def test_move_multiple_rows_preserves_order(self):
        self.assertEqual(moved_entries(list('abcdef'), [1, 3], 6), list('acefbd'))
        self.assertEqual(moved_entries(list('abcdef'), [3, 4], 1), list('adebcf'))
        self.assertEqual(moved_entries(list('abc'), [1], 2), list('abc'))

    def test_drag_proposes_reorder_without_mutating_before_save(self):
        model = PlaylistModel()
        model.reset_entries(list('abcd'))
        received = []
        model.reordered.connect(received.append)
        mime = QMimeData()
        mime.setData(MIME, json.dumps([0, 2]).encode())
        self.assertTrue(model.dropMimeData(mime, Qt.MoveAction, 4, 0, model.index(-1, 0)))
        self.assertEqual(received, [list('bdac')])
        self.assertEqual(model.entries, list('abcd'))

    def test_bpm_from_tinytag_other(self):
        tags = SimpleNamespace(artist='Artist', title='Title', other={'bpm':['128']})
        job = Metadata([Path('song.flac')])
        received = []
        job.found.connect(lambda path, label: received.append(label))
        with patch('playlist_manager.TinyTag.get', return_value=tags):
            job.run()
        self.assertEqual(received, ['Artist - Title  ·  128 BPM'])

    def test_two_views_share_selection_and_single_track_preview(self):
        w = SimpleNamespace(lang='de', user_volume=.5, show_picker=lambda:None)
        manager = PlaylistManager(w)
        manager.model.reset_entries([Path('/a.mp3'), Path('/b.mp3')])
        self.assertIs(manager.views[0].selectionModel(), manager.views[1].selectionModel())
        manager.selection.select(manager.model.index(1, 0), QItemSelectionModel.Select)
        manager.preview()
        self.assertEqual(manager.player.source().toLocalFile(), '/b.mp3')
        manager.stop()

# Continuous columns and shared scrolling regression.
class ContinuousColumnsTests(unittest.TestCase):
    def test_columns_scroll_and_edge_buttons(self):
        window = SimpleNamespace(lang='de', user_volume=.5, show_picker=lambda: None)
        manager = PlaylistManager(window)
        manager.resize(1000, 700)
        entries = [Path(f'/track-{i}.mp3') for i in range(120)]
        manager.model.reset_entries(entries)
        manager.show()
        app.processEvents()
        manager.update_pages()
        c = manager.capacity
        self.assertEqual(manager.views[1].visible_start, c)
        manager.scroll.setValue(15)
        self.assertEqual(manager.views[0].visible_start, 15)
        self.assertEqual(manager.views[1].visible_start, 15 + c)
        manager.scroll.setValue(manager.scroll.maximum())
        self.assertEqual(manager.views[1].visible_end, len(entries))
        self.assertEqual(manager.views[0].visible_end, manager.views[1].visible_start)
        changes = []
        manager.reorder = changes.append
        for row in (11, 19):
            manager.selection.select(manager.model.index(row, 0), QItemSelectionModel.Select)
        manager.move_to_edge(False)
        self.assertEqual(changes[-1][:2], [entries[11], entries[19]])
        manager.move_to_edge(True)
        self.assertEqual(changes[-1][-2:], [entries[11], entries[19]])
        manager.stop()
        manager.close()

if __name__ == '__main__': unittest.main()
