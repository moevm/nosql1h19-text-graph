from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtWidgets import QStyleOptionGraphicsItem
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt


class TextItem(QGraphicsTextItem):
    def __init__(self, html_text, id, parent=None):
        super().__init__(parent)
        self.parent = parent

        if parent:
            parent.setZValue(parent.zValue() + 5)

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.setZValue(2)
        text = f"""
        <div align="right">
        <a href="internal://close?id={id}">Закрыть</a>
            <hr>
        </div>
        """
        self.setHtml(text + html_text)
        self.setTextWidth(400)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget=None):
        painter.setBrush(QColor(255, 204, 0))
        painter.drawRect(self.boundingRect())
        super().paint(painter, option, widget)

    def __del__(self):
        if self.parent:
            self.parent.setZValue(self.parent.zValue() - 5)
