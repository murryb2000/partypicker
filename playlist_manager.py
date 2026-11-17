import json
from pathlib import Path
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QMimeData, QItemSelectionModel, QThread, Signal, QUrl, QSize, QTimer
from PySide6.QtGui import QDrag, QKeySequence, QShortcut, QPixmap, QPainter, QColor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                               QListView, QAbstractItemView, QFileDialog, QScrollBar)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from tinytag import TinyTag

MIME = 'application/x-partypicker-rows'


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

    def reset_entries(self, entries):
        self.beginResetModel()
        self.entries = list(entries)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.entries)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self.entries):
            return None
        path = self.entries[index.row()]
        if role == Qt.SizeHintRole:
            return QSize(150, 28)
        if role == Qt.DisplayRole:
            return f'{index.row() + 1}. ' + self.labels.get(str(path), Path(path).stem)
        if role == Qt.ToolTipRole:
            return str(path)
        return None

    def flags(self, index):
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
            updated = moved_entries(self.entries, rows, destination)
        except (ValueError, TypeError):
            return False
        if updated != self.entries:
            self.reordered.emit(updated)
        return True

    def set_label(self, path, label):
        self.labels[path] = label
        for row, entry in enumerate(self.entries):
            if str(entry) == path:
                index = self.index(row, 0)
                self.dataChanged.emit(index, index, [Qt.DisplayRole])


class PlaylistView(QListView):
    scroll_requested = Signal(int)
    resized = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAutoScroll(True)
        self.setAutoScrollMargin(50)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setUniformItemSizes(True)
        self.setSpacing(0)
        self.setStyleSheet("QListView { background:#101827; border:1px solid #425970; } QListView::item { margin:1px 2px; padding-left:7px; background:#293d53; border:1px solid #425970; border-radius:4px; } QListView::item:selected { background:#176c62; border:1px solid #32d1b0; } QListView::item:hover { border:1px solid #92b5d0; }")
        self.visible_start, self.visible_end = 0, 0
        self.edge_direction = 0
        self.edge_timer = QTimer(self)
        self.edge_timer.setInterval(90)
        self.edge_timer.timeout.connect(lambda: self.scroll_requested.emit(self.edge_direction))
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

    def dragMoveEvent(self, event):
        super().dragMoveEvent(event)
        y = event.position().y()
        self.edge_direction = -1 if y < 35 else (1 if y > self.viewport().height() - 35 else 0)
        if self.edge_direction:
            self.edge_timer.start()
        else:
            self.edge_timer.stop()
        event.setDropAction(Qt.MoveAction)
        event.accept()

    def dragLeaveEvent(self, event):
        self.edge_timer.stop()
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        self.edge_timer.stop()
        idx = self.indexAt(event.position().toPoint())
        destination = self.visible_end
        if idx.isValid():
            destination = idx.row() + (event.position().y() > self.visualRect(idx).center().y())
        if self.model().dropMimeData(event.mimeData(), Qt.MoveAction, destination, 0, QModelIndex()):
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
        pixmap = QPixmap(min(520, self.viewport().width()), 28)
        pixmap.fill(QColor('#176c62'))
        painter = QPainter(pixmap)
        painter.setPen(QColor('#ffffff'))
        label = self.model().data(self.model().index(rows[0], 0))
        if len(rows) > 1:
            label = f'{len(rows)} × ' + label
        painter.drawText(pixmap.rect().adjusted(8, 0, -8, 0), Qt.AlignVCenter, label)
        painter.end()
        drag.setPixmap(pixmap)
        drag.exec(Qt.MoveAction)
        self.edge_timer.stop()


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
        bottom.addStretch()
        layout.addLayout(bottom)
        self.model.modelReset.connect(self.update_pages)
        self.status = QLabel()
        layout.addWidget(self.status)
        self.space = QShortcut(QKeySequence('Space'), self)
        self.space.setContext(Qt.WidgetWithChildrenShortcut)
        self.space.activated.connect(self.preview)
        self.retranslate()

    def retranslate(self):
        de = self.window.lang == 'de'
        self.to_start.setText('An den Anfang' if de else 'Move to beginning')
        self.to_end.setText('Ans Ende' if de else 'Move to end')
        self.back.setText('← Zurück zum PartyPicker' if de else '← Back to PartyPicker')
        self.open.setText('Playlist öffnen …' if de else 'Open playlist …')
        self.current.setText('Aktuelle Playlist übernehmen' if de else 'Use current playlist')
        self.heading.setText('PLAYLIST-MANAGER · Links beginnt die Liste · rechts geht sie weiter' if de else 'PLAYLIST MANAGER · Playlist continues from left to right')
        self.status.setText('Strg + Ziehen: markieren · Auswahl ziehen: verschieben · Leertaste: vorhören' if de else 'Ctrl + drag: select · Drag selection to reorder · Space: preview')

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
            for row in range(count):
                hide = not first <= row < end
                if view.isRowHidden(row) != hide:
                    view.setRowHidden(row, hide)
            view.verticalScrollBar().setValue(0)

    def move_to_edge(self, end):
        rows = [i.row() for i in self.selection.selectedRows()]
        if not rows:
            return
        updated = moved_entries(self.model.entries, rows, len(self.model.entries) if end else 0)
        if updated != self.model.entries:
            self.reorder(updated)

    def reload(self):
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
        self.player.stop()
        self.player.setSource(QUrl())
        for job in list(self.metadata_jobs):
            job.requestInterruption()
        for job in list(self.metadata_jobs):
            job.wait()
