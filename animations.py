"""Short presentation-only transitions. Model changes and saving never wait for them."""
import time
from dataclasses import dataclass
from PySide6.QtCore import (Qt, QRect, QRectF, QPoint, QEvent, QTimer,
                            QVariantAnimation, QEasingCurve, QPersistentModelIndex)
from PySide6.QtGui import QColor, QPainter, QPalette, QRegion
from PySide6.QtWidgets import QWidget, QStyledItemDelegate, QStyleOptionViewItem, QStyle


@dataclass
class Frame:
    rect: QRectF
    pixmap: object
    alpha: float = 1.0


class RowMotion(QWidget):
    """Animate snapshots of visible rows while the real model is already current."""
    def __init__(self, parent, views):
        super().__init__(parent)
        self.views = views
        self.frames = {}
        self.regions = []
        self.progress = 1.0
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(190)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.valueChanged.connect(self.advance)
        self.anim.finished.connect(self.finish)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.hide()
        parent.installEventFilter(self)
        for view in views:
            view.viewport().installEventFilter(self)
            view.verticalScrollBar().valueChanged.connect(self.finish)
            view.horizontalScrollBar().valueChanged.connect(self.finish)

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Resize, QEvent.Hide):
            self.finish()
        return False

    def capture(self, actual=False):
        if not actual and self.isVisible() and self.frames:
            return self.current_frames()
        result = {}
        for column, view in enumerate(self.views):
            if not view.isVisible():
                continue
            viewport = view.viewport()
            model = view.model()
            if hasattr(view, 'shown_rows') and view.shown_rows is not None:
                rows = sorted(view.shown_rows)
            else:
                first = view.indexAt(QPoint(4, 4)).row()
                last = view.indexAt(QPoint(4, max(0, viewport.height() - 4))).row()
                first = max(0, first)
                last = last if last >= first else model.rowCount() - 1
                rows = range(first, last + 1)
            for row in rows:
                index = model.index(row, 0)
                rect = view.visualRect(index)
                if rect.isEmpty() or not viewport.rect().intersects(rect):
                    continue
                key = index.data(Qt.UserRole)
                if key is None:
                    key = ('gap', column, row)
                mapped = QRect(viewport.mapTo(self.parentWidget(), rect.topLeft()), rect.size())
                result[key] = Frame(QRectF(mapped), viewport.grab(rect))
        return result

    def animate(self, before, after=None):
        self.anim.stop()
        after = self.capture(actual=True) if after is None else after
        self.frames = {}
        for key in before.keys() | after.keys():
            old, new = before.get(key), after.get(key)
            if old is None:
                old = Frame(new.rect, new.pixmap, 0.0)
            if new is None:
                new = Frame(old.rect, old.pixmap, 0.0)
            self.frames[key] = (old, new)
        if not self.frames or not self.parentWidget().isVisible():
            self.finish()
            return
        self.regions = [QRect(v.viewport().mapTo(self.parentWidget(), QPoint(0, 0)), v.viewport().size())
                        for v in self.views if v.isVisible()]
        self.setGeometry(self.parentWidget().rect())
        self.progress = 0.0
        self.show()
        self.raise_()
        self.anim.start()

    def advance(self, value):
        self.progress = float(value)
        self.update()

    def current_frames(self):
        p = self.progress
        out = {}
        for key, (old, new) in self.frames.items():
            a, b = old.rect, new.rect
            rect = QRectF(a.x() + (b.x()-a.x())*p, a.y()+(b.y()-a.y())*p,
                          a.width()+(b.width()-a.width())*p, a.height()+(b.height()-a.height())*p)
            out[key] = Frame(rect, new.pixmap if new.alpha else old.pixmap,
                             old.alpha+(new.alpha-old.alpha)*p)
        return out

    def paintEvent(self, event):
        painter = QPainter(self)
        region = QRegion()
        for rect in self.regions:
            region = region.united(QRegion(rect))
        painter.setClipRegion(region)
        for rect in self.regions:
            painter.fillRect(rect, QColor('#101827'))
        for frame in self.current_frames().values():
            painter.setOpacity(frame.alpha)
            painter.drawPixmap(frame.rect, frame.pixmap, QRectF(frame.pixmap.rect()))
        painter.end()

    def finish(self, *args):
        self.anim.stop()
        self.hide()
        self.frames.clear()


class ColorFadeDelegate(QStyledItemDelegate):
    def __init__(self, view):
        super().__init__(view)
        self.view = view
        self.transitions = {}
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.tick)
        view.model().modelReset.connect(self.clear)

    def clear(self):
        self.transitions.clear()
        self.timer.stop()

    def color_at(self, index):
        transition = self.transitions.get(QPersistentModelIndex(index))
        if transition:
            start, target, since = transition
            p = min(1.0, (time.monotonic() - since) / .22)
            return QColor.fromRgbF(*(start.getRgbF()[i] + (target.getRgbF()[i]-start.getRgbF()[i])*p for i in range(4)))
        color = index.data(Qt.ForegroundRole)
        return color.color() if color else self.view.palette().color(QPalette.Text)

    def change(self, item, target):
        index = self.view.indexFromItem(item)
        old = self.color_at(index)
        target = QColor(target)
        item.setForeground(target)  # Public/model state is current immediately.
        if old == target or not self.view.isVisible() or not self.view.visualRect(index).intersects(self.view.viewport().rect()):
            self.transitions.pop(QPersistentModelIndex(index), None)
            return
        self.transitions[QPersistentModelIndex(index)] = (old, target, time.monotonic())
        self.timer.start()
        self.view.viewport().update()

    def tick(self):
        now = time.monotonic()
        self.transitions = {i: t for i, t in self.transitions.items() if i.isValid() and now-t[2] < .22}
        self.view.viewport().update()
        if not self.transitions:
            self.timer.stop()

    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        if QPersistentModelIndex(index) in self.transitions:
            color = self.color_at(index)
            opt.palette.setColor(QPalette.Text, color)
        widget = opt.widget or self.view
        widget.style().drawControl(QStyle.CE_ItemViewItem, opt, painter, widget)


class WaveCrossfade(QWidget):
    def __init__(self, wave):
        super().__init__(wave)
        self.old = None
        self.alpha = 0.0
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(180)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.valueChanged.connect(self.advance)
        self.anim.finished.connect(self.finish)
        wave.installEventFilter(self)
        self.hide()

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Resize, QEvent.Hide):
            self.finish()
        return False

    def capture(self):
        return self.parentWidget().grab() if self.parentWidget().isVisible() else None

    def start(self, old):
        self.anim.stop()
        if old is None:
            self.finish()
            return
        self.old = old
        self.setGeometry(self.parentWidget().rect())
        self.alpha = 1.0
        self.show()
        self.raise_()
        self.anim.start()

    def advance(self, value):
        self.alpha = float(value)
        self.update()

    def paintEvent(self, event):
        if self.old:
            painter = QPainter(self)
            painter.setOpacity(self.alpha)
            painter.drawPixmap(self.rect(), self.old)
            painter.end()

    def finish(self):
        self.anim.stop()
        self.hide()
        self.old = None
