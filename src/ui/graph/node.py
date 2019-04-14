from PyQt5.QtCore import QRect, QRectF, Qt, QVariant
from PyQt5.QtGui import QPainterPath, QPainter, QColor, QPen
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QStyle, QGraphicsSceneMouseEvent


class Node(QGraphicsItem):
    Type = QGraphicsItem.UserType + 1
    edge_list = []

    # TODO Node label
    # TODO Node info
    def __init__(self, graph_widget, label=None, info=None):
        """Создание вершины

        :param graph_widget: объект класса GraphWidget
        :param label: Надпись на вершине
        :param info: HTML-текст, который будет открываться при ПКМ
        """
        super(Node, self).__init__()
        self.graph = graph_widget
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setZValue(-1)
        self.size = QRect(-15, -15, 30, 30)

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

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        color: QColor = QColor(Qt.yellow)
        if option.state & QStyle.State_Sunken:
            color = QColor(Qt.darkYellow)
        painter.setBrush(color)
        painter.setPen(QPen(Qt.black, 0))
        painter.drawEllipse(self.size)

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

