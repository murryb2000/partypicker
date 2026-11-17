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

class DragFeedbackTests(unittest.TestCase):
    def test_speed_steps(self):
        from playlist_manager import edge_speed
        self.assertEqual(edge_speed(1.49), 4)
        self.assertAlmostEqual(edge_speed(3), 16)
        self.assertAlmostEqual(edge_speed(6), 44)
        self.assertEqual(edge_speed(1.5), 8)
        self.assertEqual(edge_speed(4.5), 28)
        self.assertEqual(edge_speed(7.5), 60)
        self.assertEqual(edge_speed(120), 60)

    def test_line_and_drop_use_same_boundary(self):
        from PySide6.QtCore import QPoint
        window = SimpleNamespace(lang='de', user_volume=.5, show_picker=lambda: None)
        manager = PlaylistManager(window)
        manager.resize(1000,700)
        manager.model.reset_entries([Path(f'/track-{i}.mp3') for i in range(80)])
        manager.show(); app.processEvents(); manager.update_pages()
        view = manager.views[0]
        rect = view.visualRect(manager.model.index(2,0))
        self.assertEqual(view.insertion_at(QPoint(rect.center().x(),rect.top()+2))[0],2)
        self.assertEqual(view.insertion_at(QPoint(rect.center().x(),rect.bottom()-2))[0],3)
        received=[]
        view.scroll_requested.connect(received.append)
        edge = view.viewport().mapToGlobal(QPoint(20, view.viewport().height()-1))
        with patch('playlist_manager.QCursor.pos', return_value=edge):
            with patch('playlist_manager.time.monotonic',return_value=100): view.poll_drag_edge()
            with patch('playlist_manager.time.monotonic',return_value=101): view.poll_drag_edge()
        self.assertEqual(received[-1],4)
        with patch('playlist_manager.QCursor.pos', return_value=edge):
            for tick in range(2, 32):
                with patch('playlist_manager.time.monotonic', return_value=100+tick):
                    view.poll_drag_edge()
        self.assertGreater(received[-1], received[0] * 2)
        self.assertIn('1500', manager.scroll_feedback.text())
        middle=view.viewport().mapToGlobal(QPoint(20,100))
        with patch('playlist_manager.QCursor.pos',return_value=middle): view.poll_drag_edge()
        self.assertEqual(view.edge_direction,0)
        self.assertEqual(view.edge_remainder,0)
        manager.stop(); manager.close()
