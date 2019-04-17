from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QStyle
from PyQt5.QtGui import QPainterPath, QPainter, QColor, QPen
from PyQt5.QtCore import Qt

class TextItem(QGraphicsTextItem):
    def __init__(self, html_text, id, parent=None):
        super().__init__(parent)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.setZValue(1)
        text = f"""
        <div align="right">
        <a href="internal://close?id={id}">Закрыть</a>
            <hr>
        </div>
        """
        self.setHtml(text + html_text)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget=None):
        painter.setBrush(QColor(255, 204, 0))
        painter.drawRect(self.boundingRect())
        super().paint(painter, option, widget)
