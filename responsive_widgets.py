"""Single-line labels that keep full text for tooltips and accessibility."""
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QPalette
from PySide6.QtWidgets import QLabel, QSizePolicy, QStyle, QStyleOption


class ElidedLabel(QLabel):
    def __init__(self, text='', mode=Qt.ElideRight, parent=None):
        super().__init__(parent)
        self.elide_mode = mode
        self.setTextFormat(Qt.PlainText)
        self.setWordWrap(False)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.setText(text)

    def setText(self, text):
        text = str(text)
        super().setText(text)
        self.setToolTip(text)
        self.updateGeometry()
        self.update()

    def sizeHint(self):
        margins = self.contentsMargins()
        return QSize(220, self.fontMetrics().height() + margins.top() + margins.bottom() + 2*self.margin())

    def minimumSizeHint(self):
        return QSize(0, self.sizeHint().height())

    def displayed_text(self):
        text = self.text().replace('\r', ' ').replace('\n', ' ')
        return self.fontMetrics().elidedText(text, self.elide_mode,
                                            max(0, self.contentsRect().width() - 2*self.margin()))

    def paintEvent(self, event):
        painter = QPainter(self)
        option = QStyleOption()
        option.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, option, painter, self)
        painter.setFont(self.font())
        painter.setPen(self.palette().color(QPalette.WindowText))
        margin = self.margin()
        painter.drawText(self.contentsRect().adjusted(margin, margin, -margin, -margin),
                         self.alignment() | Qt.TextSingleLine, self.displayed_text())
        painter.end()
