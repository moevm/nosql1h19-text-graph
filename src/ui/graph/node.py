from PyQt5.QtCore import QRect, QRectF, Qt
from PyQt5.QtGui import QPainterPath, QPainter, QColor, QPen
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QStyle, \
                            QGraphicsSceneMouseEvent, QGraphicsSceneHoverEvent

from ui.misc import get_foreground_color


class Node(QGraphicsItem):
    Type = QGraphicsItem.UserType + 1

    def __init__(self, graph_widget, label=None, info=None,
                 color=QColor(Qt.yellow), id=0):
        """Создание вершины

        :param graph_widget: объект класса GraphWidget
        :param label: Надпись на вершине
        :param info: HTML-текст, который будет открываться при ПКМ
        :param color: Цвет
        """
        super(Node, self).__init__()
        self.graph = graph_widget
        self.label = label
        self.info = info
        self.size_value = 20  # TODO Settings
        self.id = id

        self.size = QRect(-self.size_value, -self.size_value,
                          self.size_value * 2, self.size_value * 2)

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setZValue(1)
        self.color = color
        self.edge_list = []

    def addEdge(self, edge):
        self.edge_list.append(edge)
        edge.adjust()

    def boundingRect(self):
        adjust = 2
        return QRectF(self.size.x() - adjust, self.size.y() - adjust,
                      self.size.width() + adjust, self.size.height() + adjust)

    def shape(self):
        path = QPainterPath()
        path.addEllipse(QRectF(self.size))
        return path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget=None):
        color = self.color
        if option.state & QStyle.State_Sunken:
            color = color.darker(200)
        elif option.state & QStyle.State_MouseOver:
            color = color.lighter(150)
        painter.setBrush(color)
        painter.setPen(QPen(Qt.black, 0))
        painter.drawEllipse(self.size)

        if self.label:
            text_color = get_foreground_color(color)
            factor = (self.size.width() - 2) \
                / painter.fontMetrics().width(self.label)
            font = painter.font()
            if len(self.label) == 1:
                factor *= 0.5
            font.setPointSizeF(font.pointSizeF() * factor)
            painter.setFont(font)
            painter.setPen(QPen(text_color, 0))
            painter.drawText(self.size, Qt.AlignHCenter | Qt.AlignVCenter,
                             self.label)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        self.update()
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edge_list:
                edge.adjust()
            self.graph.item_moved()
        return super().itemChange(change, value)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        super().hoverLeaveEvent(event)
