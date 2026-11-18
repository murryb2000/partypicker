"""Drag within the manager without Windows OLE blocking timers at the taskbar."""
from PySide6.QtCore import QObject, QEvent, QEventLoop, QTimer, QPoint, QModelIndex, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QLabel


class InternalDrag(QObject):
    def __init__(self, source):
        super().__init__(source)
        self.source = source
        self.mime = self.pixmap = None
        self.target = None
        self.point = None
        self.accepted = False
        self.loop = QEventLoop(self)
        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.update_position)

    def setMimeData(self, mime):
        self.mime = mime

    def setPixmap(self, pixmap):
        self.pixmap = pixmap

    def update_position(self, position=None):
        owner = getattr(self.source, 'manager', None)
        if not self.source.isVisible():
            self.finish(False)
            return
        position = QCursor.pos() if position is None else position
        self.target, self.point = None, None
        for view in owner.views if owner else [self.source]:
            point = view.viewport().mapFromGlobal(position)
            inside = view.isVisible() and view.viewport().rect().contains(point)
            view.drop_point = point if inside else None
            if inside:
                self.target, self.point = view, point
                if owner:
                    owner.preview_drop(view, point)
            view.viewport().update()
        screen = QApplication.screenAt(position)
        preview_pos = position + QPoint(16, 16)
        if screen:
            rect = screen.geometry()
            preview_pos.setX(max(rect.left(), min(preview_pos.x(), rect.right()-self.preview.width()+1)))
            if preview_pos.y() + self.preview.height() > rect.bottom():
                preview_pos.setY(position.y()-self.preview.height()-16)
        self.preview.move(preview_pos)

    def finish(self, accepted):
        self.accepted = accepted and self.target is not None
        self.loop.quit()

    def eventFilter(self, obj, event):
        kind = event.type()
        if kind == QEvent.MouseMove:
            self.update_position(event.globalPosition().toPoint())
            return True
        if kind == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            self.update_position(event.globalPosition().toPoint())
            self.finish(True)
            return True
        if kind == QEvent.ShortcutOverride:
            event.accept()
            return True
        if kind == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.finish(False)
            return True
        if kind == QEvent.ApplicationDeactivate:
            self.finish(False)
        if kind in (QEvent.Close, QEvent.Hide) and obj is self.source.window():
            self.finish(False)
        return False

    def exec(self, supported):
        app = QApplication.instance()
        self.preview = QLabel(None, Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowTransparentForInput)
        self.preview.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.preview.setAttribute(Qt.WA_ShowWithoutActivating)
        self.preview.setPixmap(self.pixmap)
        self.preview.adjustSize()
        self.update_position()
        self.preview.show()
        app.installEventFilter(self)
        self.source.viewport().grabMouse()
        app.setOverrideCursor(Qt.ClosedHandCursor)
        self.timer.start()
        try:
            self.loop.exec()
        finally:
            self.timer.stop()
            app.removeEventFilter(self)
            self.source.viewport().releaseMouse()
            app.restoreOverrideCursor()
            self.preview.hide()
            self.preview.deleteLater()
            self.deleteLater()
        if self.accepted:
            owner = getattr(self.source, 'manager', None)
            before = owner.motion.capture() if owner else None
            destination, _ = self.target.insertion_at(self.point)
            if self.target.model().dropMimeData(self.mime, Qt.MoveAction, destination, 0, QModelIndex()):
                if owner:
                    owner.motion.animate(before)
                return Qt.MoveAction
        return Qt.IgnoreAction
