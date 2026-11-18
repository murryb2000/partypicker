import json
import time
from pathlib import Path
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QMimeData, QItemSelectionModel, QThread, Signal, QUrl, QSize, QTimer
from PySide6.QtGui import QDrag, QKeySequence, QShortcut, QPixmap, QPainter, QColor, QPen, QCursor, QGuiApplication
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                               QListView, QAbstractItemView, QFileDialog, QScrollBar, QStyledItemDelegate)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from tinytag import TinyTag
from animations import RowMotion

MIME = 'application/x-partypicker-rows'


def edge_speed(seconds):
    # Predictable acceleration every 1.5 seconds, capped at 60 rows/second.
    speeds = (4.0, 8.0, 16.0, 28.0, 44.0, 60.0)
    return speeds[min(len(speeds) - 1, int(max(0, seconds) // 1.5))]


def screen_edge_direction(y, top, bottom, previous, scale=1.0):
    """Start only on contact; retain an active edge until 10 physical pixels away."""
    if y <= top:
        return -1
    if y >= bottom:
        return 1
    if previous == -1 and (y - top) * scale < 10:
        return -1
    if previous == 1 and (bottom - y) * scale < 10:
        return 1
    return 0


def moved_entries(entries, rows, destination):
    rows = sorted(set(r for r in rows if 0 <= r < len(entries)))
    destination = max(0, min(destination, len(entries)))
    chosen = [entries[i] for i in rows]
    remaining = [x for i, x in enumerate(entries) if i not in rows]
    target = destination - sum(i < destination for i in rows)
    return remaining[:target] + chosen + remaining[target:]


class Metadata(QThread):
    found = Signal(str, str)

    def __init__(self, entries, parent=None):
        super().__init__(parent)
        self.entries = list(entries)

    def run(self):
        for path in self.entries:
            if self.isInterruptionRequested():
                break
            label = Path(path).stem
            try:
                tag = TinyTag.get(str(path))
                artist = (tag.artist or '').strip()
                title = (tag.title or '').strip()
                if artist and title:
                    label = f'{artist} - {title}'
                bpm = getattr(tag, 'bpm', None) or (getattr(tag, 'other', {}) or {}).get('bpm')
                if isinstance(bpm, (list, tuple)):
                    bpm = bpm[0] if bpm else None
                if bpm:
                    label += f'  ·  {bpm} BPM'
            except Exception:
                pass
            self.found.emit(str(path), label)


class PlaylistModel(QAbstractListModel):
    reordered = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries = []
        self.labels = {}
        self.projection = None
        self.drag_rows = None
        self.drag_remaining = []
        self.drag_target = None
        self.drag_dropped = False

    def reset_entries(self, entries):
        self.beginResetModel()
        self.entries = list(entries)
        self.projection = None
        self.drag_rows = None
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.projection) if self.projection is not None else len(self.entries)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= self.rowCount():
            return None
        row = self.source_row(index.row())
        if row is None:
            return QSize(150, 28) if role == Qt.SizeHintRole else None
        path = self.entries[row]
        if role == Qt.UserRole:
            return str(path)
        if role == Qt.SizeHintRole:
            return QSize(150, 28)
        if role == Qt.DisplayRole:
            return f'{row + 1}. ' + self.labels.get(str(path), Path(path).stem)
        if role == Qt.ToolTipRole:
            return str(path)
        return None

    def flags(self, index):
        if index.isValid() and self.source_row(index.row()) is None:
            return Qt.ItemIsDropEnabled
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return Qt.ItemIsDropEnabled

    def mimeTypes(self):
        return [MIME]

    def supportedDropActions(self):
        return Qt.MoveAction

    def dropMimeData(self, data, action, row, column, parent):
        if action == Qt.IgnoreAction:
            return True
        if action != Qt.MoveAction or not data.hasFormat(MIME):
            return False
        try:
            rows = json.loads(bytes(data.data(MIME)).decode('utf-8'))
            if not isinstance(rows, list) or not all(isinstance(x, int) for x in rows):
                return False
            destination = row if row >= 0 else (parent.row() if parent.isValid() else len(self.entries))
            if self.drag_rows is not None:
                if sorted(rows) != self.drag_rows:
                    return False
                target = self.remaining_destination(destination)
                order = self.drag_remaining[:target] + self.drag_rows + self.drag_remaining[target:]
                updated = [self.entries[i] for i in order]
                self.drag_dropped = True
                self.drag_rows = None
                self.set_projection(order)
            else:
                updated = moved_entries(self.entries, rows, destination)
        except (ValueError, TypeError):
            return False
        if updated != self.entries:
            self.reordered.emit(updated)
        return True

    def source_row(self, display_row):
        return self.projection[display_row] if self.projection is not None else display_row

    def set_projection(self, projection):
        self.beginResetModel()
        self.projection = projection
        self.endResetModel()

    def begin_drag(self, rows):
        self.drag_rows = sorted(set(rows))
        self.drag_dropped = False
        self.drag_target = None
        selected = set(self.drag_rows)
        self.drag_remaining = [i for i in range(len(self.entries)) if i not in selected]
        self.set_projection([None if i in selected else i for i in range(len(self.entries))])

    def collapse_drag(self):
        if self.drag_rows is not None and self.drag_target is None:
            self.set_projection(list(self.drag_remaining))

    def remaining_destination(self, display_row):
        if self.projection is None:
            return max(0, min(display_row, len(self.entries)))
        return sum(i is not None for i in self.projection[:max(0, display_row)])

    def show_gap(self, target):
        if self.drag_rows is None or target == self.drag_target:
            return False
        self.drag_target = max(0, min(target, len(self.drag_remaining)))
        self.set_projection(self.drag_remaining[:self.drag_target] + [None] * len(self.drag_rows)
                            + self.drag_remaining[self.drag_target:])
        return True

    def cancel_drag(self):
        self.drag_rows = None
        self.drag_target = None
        self.drag_dropped = False
        self.set_projection(None)

    def set_label(self, path, label):
        self.labels[path] = label
        for row in range(self.rowCount()):
            source = self.source_row(row)
            if source is not None and str(self.entries[source]) == path:
                index = self.index(row, 0)
                self.dataChanged.emit(index, index, [Qt.DisplayRole])


class GapDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.data(Qt.UserRole) is None:
            painter.fillRect(option.rect.adjusted(2, 1, -2, -1), QColor('#14362f'))
            return
        super().paint(painter, option, index)


class PlaylistView(QListView):
    scroll_requested = Signal(int)
    resized = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(GapDelegate(self))
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(False)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAutoScroll(False)
        self.setAutoScrollMargin(50)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setUniformItemSizes(True)
        self.setSpacing(0)
        self.setStyleSheet("QListView { background:#101827; border:1px solid #425970; } QListView::item { margin:1px 2px; padding-left:7px; background:#293d53; border:1px solid #425970; border-radius:4px; } QListView::item:selected { background:#176c62; border:1px solid #32d1b0; } QListView::item:hover { border:1px solid #92b5d0; }")
        self.visible_start, self.visible_end = 0, 0
        self.shown_rows = None
        self.edge_direction = 0
        self.edge_screen_key = None
        self.edge_timer = QTimer(self)
        self.edge_timer.setInterval(30)
        self.edge_timer.timeout.connect(self.poll_drag_edge)
        self.edge_since = self.edge_last = 0.0
        self.edge_remainder = 0.0
        self.drop_point = None
        self.sweeping = False
        self.swept = set()
        self.sweep_last = None

    def wheelEvent(self, event):
        delta = event.angleDelta().y() or event.pixelDelta().y()
        if delta:
            self.scroll_requested.emit(-3 if delta > 0 else 3)
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(MIME):
            event.setDropAction(Qt.MoveAction)
            event.accept()

    def insertion_at(self, point):
        idx = self.indexAt(point)
        if idx.isValid():
            rect = self.visualRect(idx)
            after = point.y() > rect.center().y()
            return idx.row() + int(after), rect.bottom() + 1 if after else rect.top()
        return self.visible_end, min(self.viewport().height() - 2, max(1, (self.visible_end - self.visible_start) * 28))

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.drop_point is not None:
            _, y = self.insertion_at(self.drop_point)
            painter = QPainter(self.viewport())
            painter.setPen(QPen(QColor('#32e69b'), 2))
            painter.drawLine(3, y, self.viewport().width() - 4, y)
            painter.end()

    def poll_drag_edge(self):
        cursor = QCursor.pos()
        owner = getattr(self, 'manager', None)
        screen = QGuiApplication.screenAt(cursor)
        screen_rect = screen.geometry() if screen else None
        key = (screen.name(), screen_rect.x(), screen_rect.y(),
               screen_rect.width(), screen_rect.height(), screen.devicePixelRatio()) if screen else None
        previous = self.edge_direction if key == self.edge_screen_key else 0
        direction = screen_edge_direction(cursor.y(), screen_rect.top(), screen_rect.bottom(),
                                          previous, screen.devicePixelRatio()) if screen else 0
        now = time.monotonic()
        if direction != self.edge_direction or key != self.edge_screen_key:
            self.edge_screen_key = key
            self.edge_direction = direction
            self.edge_since = self.edge_last = now
            self.edge_remainder = 0.0
        if direction:
            self.edge_remainder += (now - self.edge_last) * edge_speed(now - self.edge_since)
            rows = int(self.edge_remainder)
            self.edge_remainder -= rows
            if rows:
                self.scroll_requested.emit(direction * rows)
        self.edge_last = now
        if owner:
            if direction:
                percent = round(edge_speed(now - self.edge_since) / 4 * 100)
                owner.scroll_feedback.setText(('↑' if direction < 0 else '↓') + f' {percent} %')
            else:
                owner.scroll_feedback.clear()
        if owner:
            for view in owner.views:
                if view.drop_point is not None:
                    view.drop_point = view.viewport().mapFromGlobal(cursor)
                    if not direction:
                        owner.preview_drop(view, view.drop_point)
                    view.viewport().update()

    def dragMoveEvent(self, event):
        if not event.mimeData().hasFormat(MIME):
            event.ignore()
            return
        self.drop_point = event.position().toPoint()
        if getattr(self, 'manager', None):
            self.manager.preview_drop(self, self.drop_point)
        self.viewport().update()
        event.setDropAction(Qt.MoveAction)
        event.accept()

    def dragLeaveEvent(self, event):
        self.drop_point = None
        self.viewport().update()
        event.accept()

    def dropEvent(self, event):
        destination, _ = self.insertion_at(event.position().toPoint())
        self.drop_point = None
        before = self.manager.motion.capture() if getattr(self, 'manager', None) else None
        self.viewport().update()
        if self.model().dropMimeData(event.mimeData(), Qt.MoveAction, destination, 0, QModelIndex()):
            if before is not None:
                self.manager.motion.animate(before)
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        idx = self.indexAt(event.position().toPoint())
        if event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier and idx.isValid():
            self.sweeping = True
            self.swept = {idx.row()}
            self.sweep_last = idx.row()
            self.selectionModel().select(idx, QItemSelectionModel.Toggle | QItemSelectionModel.Rows)
            self.selectionModel().setCurrentIndex(idx, QItemSelectionModel.NoUpdate)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.sweeping:
            idx = self.indexAt(event.position().toPoint())
            if idx.isValid():
                first, last = sorted((self.sweep_last, idx.row()))
                for row in range(first, last + 1):
                    if row not in self.swept:
                        self.swept.add(row)
                        self.selectionModel().select(self.model().index(row, 0), QItemSelectionModel.Select | QItemSelectionModel.Rows)
                self.sweep_last = idx.row()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.sweeping:
            self.sweeping = False
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def startDrag(self, supported):
        rows = sorted(i.row() for i in self.selectionModel().selectedRows())
        if not rows:
            return
        mime = QMimeData()
        mime.setData(MIME, json.dumps(rows).encode('utf-8'))
        drag = QDrag(self)
        drag.setMimeData(mime)
        labels = [self.model().data(self.model().index(row, 0)) for row in rows[:3]]
        if len(rows) > 3:
            labels.append(f'+{len(rows) - 3}')
        width = min(520, self.viewport().width())
        pixmap = QPixmap(width, 28 * len(labels))
        pixmap.fill(QColor('#176c62'))
        painter = QPainter(pixmap)
        painter.setPen(QColor('#ffffff'))
        from PySide6.QtCore import QRect
        for line, label in enumerate(labels):
            text = painter.fontMetrics().elidedText(label, Qt.ElideRight, width - 16)
            painter.drawText(QRect(8, line * 28, width - 16, 28), Qt.AlignVCenter, text)
        painter.end()
        drag.setPixmap(pixmap)
        owner = getattr(self, 'manager', None)
        if owner:
            owner.begin_drag(rows)
        self.edge_direction = 0
        self.edge_last = time.monotonic()
        self.edge_timer.start()
        try:
            drag.exec(Qt.MoveAction)
        finally:
            self.edge_timer.stop()
            if getattr(self, 'manager', None):
                self.manager.scroll_feedback.clear()
            owner = getattr(self, 'manager', None)
            if owner:
                owner.end_drag(rows)
            for view in owner.views if owner else [self]:
                view.drop_point = None
                view.viewport().update()


class PlaylistManager(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.model = PlaylistModel(self)
        self.model.reordered.connect(self.reorder)
        self.metadata = None
        self.metadata_jobs = []
        self.audio = QAudioOutput(self)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio)
        self.player.errorOccurred.connect(lambda *args: self.status.setText(self.player.errorString()))
        layout = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.back = QPushButton()
        self.back.clicked.connect(window.show_picker)
        self.open = QPushButton()
        self.open.clicked.connect(self.open_file)
        self.current = QPushButton()
        self.current.clicked.connect(self.reload)
        bar.addWidget(self.back)
        bar.addWidget(self.open)
        bar.addWidget(self.current)
        bar.addStretch()
        self.go_start = QPushButton()
        self.go_end = QPushButton()
        self.go_start.clicked.connect(lambda: self.scroll.setValue(0))
        self.go_end.clicked.connect(lambda: self.scroll.setValue(self.scroll.maximum()))
        bar.addWidget(self.go_start)
        bar.addWidget(self.go_end)
        layout.addLayout(bar)
        self.heading = QLabel()
        layout.addWidget(self.heading)
        panes = QHBoxLayout()
        self.scroll = QScrollBar(Qt.Vertical)
        self.capacity = 1
        self.scroll.valueChanged.connect(self.update_pages)
        self.views = [PlaylistView(), PlaylistView()]
        self.selection = QItemSelectionModel(self.model, self)
        for view in self.views:
            view.manager = self
            view.setModel(self.model)
            view.setSelectionModel(self.selection)
            view.scroll_requested.connect(lambda delta: self.scroll.setValue(self.scroll.value() + delta))
            view.resized.connect(self.update_pages)
            panes.addWidget(view)
        panes.addWidget(self.scroll)
        layout.addLayout(panes, 1)
        bottom = QHBoxLayout()
        self.to_start = QPushButton()
        self.to_end = QPushButton()
        self.to_start.clicked.connect(lambda: self.move_to_edge(False))
        self.to_end.clicked.connect(lambda: self.move_to_edge(True))
        bottom.addWidget(self.to_start)
        bottom.addWidget(self.to_end)
        self.undo_button = QPushButton()
        self.undo_button.clicked.connect(self.undo)
        bottom.addWidget(self.undo_button)
        self.scroll_feedback = QLabel()
        bottom.addWidget(self.scroll_feedback)
        bottom.addStretch()
        layout.addLayout(bottom)
        self.motion = RowMotion(self, self.views)
        self.drag_generation = 0
        self.model.modelReset.connect(self.reset_pages)
        self.status = QLabel()
        layout.addWidget(self.status)
        self.space = QShortcut(QKeySequence('Space'), self)
        self.space.setContext(Qt.WidgetWithChildrenShortcut)
        self.space.activated.connect(self.preview)
        self.undo_shortcut = QShortcut(QKeySequence('Ctrl+Z'), self)
        self.undo_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.undo_shortcut.activated.connect(self.undo)
        self.retranslate()
        self.refresh_undo()

    def undo(self):
        if self.model.drag_rows is not None:
            return
        if getattr(self.window, 'save_job', None) or getattr(self.window, 'duplicate_job', None):
            return
        self.window.undo(on_success=self.reload)

    def refresh_undo(self):
        self.undo_button.setEnabled(bool(getattr(self.window, 'undo_stack', [])) and not getattr(self.window, 'save_job', None) and not getattr(self.window, 'duplicate_job', None))

    def retranslate(self):
        de = self.window.lang == 'de'
        self.go_start.setText('Zum Listenanfang' if de else 'Go to beginning')
        self.go_end.setText('Zum Listenende' if de else 'Go to end')
        self.go_start.setToolTip('Ansicht zum ersten Titel bewegen' if de else 'Scroll to the first track')
        self.go_end.setToolTip('Ansicht zum letzten Titel bewegen' if de else 'Scroll to the last track')
        self.undo_button.setText('Rückgängig [Strg+Z]' if de else 'Undo [Ctrl+Z]')
        self.to_start.setText('An den Anfang' if de else 'Move to beginning')
        self.to_end.setText('Ans Ende' if de else 'Move to end')
        self.back.setText('← Zurück zum PartyPicker' if de else '← Back to PartyPicker')
        self.open.setText('Playlist öffnen …' if de else 'Open playlist …')
        self.current.setText('Aktuelle Playlist übernehmen' if de else 'Use current playlist')
        self.heading.setText('PLAYLIST-MANAGER · Links beginnt die Liste · rechts geht sie weiter' if de else 'PLAYLIST MANAGER · Playlist continues from left to right')
        self.status.setText('Strg + Ziehen: markieren · Auswahl ziehen: verschieben · Leertaste: vorhören' if de else 'Ctrl + drag: select · Drag selection to reorder · Space: preview')

    def begin_drag(self, rows):
        self.drag_generation += 1
        generation = self.drag_generation
        before = self.motion.capture()
        self.model.begin_drag(rows)
        self.motion.animate(before)
        def collapse():
            if generation == self.drag_generation and self.model.drag_rows is not None and self.model.drag_target is None:
                before = self.motion.capture()
                self.model.collapse_drag()
                self.motion.animate(before)
        QTimer.singleShot(140, collapse)

    def preview_drop(self, view, point):
        if self.model.drag_rows is None:
            return
        destination, _ = view.insertion_at(point)
        target = self.model.remaining_destination(destination)
        if target != self.model.drag_target:
            before = self.motion.capture()
            self.model.show_gap(target)
            self.motion.animate(before)

    def end_drag(self, rows):
        self.drag_generation += 1
        if not self.model.drag_dropped:
            before = self.motion.capture()
            self.model.cancel_drag()
            for row in rows:
                self.selection.select(self.model.index(row, 0), QItemSelectionModel.Select | QItemSelectionModel.Rows)
            self.motion.animate(before)
        elif self.model.projection is not None and not getattr(self.window, 'save_job', None):
            # No change or rejected save: restore the authoritative in-memory list.
            self.reload()

    def reset_pages(self):
        for view in self.views:
            view.shown_rows = None
        self.update_pages()

    def update_pages(self, *args):
        if not self.views:
            return
        capacity = max(1, min(v.viewport().height() for v in self.views) // 28)
        self.capacity = capacity
        count = self.model.rowCount()
        self.scroll.blockSignals(True)
        self.scroll.setRange(0, max(0, count - 2 * capacity))
        self.scroll.setPageStep(2 * capacity)
        start = self.scroll.value()
        self.scroll.blockSignals(False)
        for column, view in enumerate(self.views):
            first = start + column * capacity
            end = min(count, first + capacity)
            view.visible_start, view.visible_end = first, end
            shown = set(range(first, end))
            if view.shown_rows is None:
                for row in range(count):
                    view.setRowHidden(row, row not in shown)
            else:
                for row in view.shown_rows - shown:
                    if row < count:
                        view.setRowHidden(row, True)
                for row in shown - view.shown_rows:
                    view.setRowHidden(row, False)
            view.shown_rows = shown
            view.verticalScrollBar().setValue(0)

    def move_to_edge(self, end):
        if self.model.drag_rows is not None:
            return
        rows = [i.row() for i in self.selection.selectedRows()]
        if not rows:
            return
        updated = moved_entries(self.model.entries, rows, len(self.model.entries) if end else 0)
        if updated != self.model.entries:
            self.reorder(updated)

    def reload(self):
        if self.model.drag_rows is not None:
            return
        self.drag_generation += 1
        self.refresh_undo()
        if self.metadata in self.metadata_jobs and self.metadata.isRunning():
            self.metadata.requestInterruption()
        self.model.reset_entries(self.window.selected)
        self.audio.setVolume(self.window.user_volume)
        self.metadata = Metadata(self.window.selected, self)
        self.metadata.found.connect(self.model.set_label)
        job = self.metadata
        self.metadata_jobs.append(job)
        job.finished.connect(lambda: self.metadata_jobs.remove(job) if job in self.metadata_jobs else None)
        job.finished.connect(job.deleteLater)
        job.start()

    def open_file(self):
        if self.model.drag_rows is not None:
            return
        name, _ = QFileDialog.getOpenFileName(self, self.window.t('open_playlist_title'), '', self.window.t('open_playlist_filter'))
        if name and self.window.load_playlist(name):
            self.player.stop()
            self.reload()

    def reorder(self, entries):
        if self.window.commit(entries, ui_change=('full',), on_success=self.reload):
            self.setEnabled(False)
        else:
            self.reload()

    def preview(self):
        if self.model.drag_rows is not None:
            return
        rows = self.selection.selectedRows()
        if len(rows) != 1:
            return
        path = self.model.entries[rows[0].row()]
        url = QUrl.fromLocalFile(str(path))
        if self.player.source() == url:
            if self.player.playbackState() == QMediaPlayer.PlayingState:
                self.player.pause()
            else:
                self.player.play()
        else:
            self.player.setSource(url)
            self.player.play()

    def stop(self):
        self.drag_generation += 1
        self.motion.finish()
        if self.model.drag_rows is not None:
            self.model.cancel_drag()
        self.player.stop()
        self.player.setSource(QUrl())
        for job in list(self.metadata_jobs):
            job.requestInterruption()
        for job in list(self.metadata_jobs):
            job.wait()
