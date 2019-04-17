from PyQt5.QtCore import QRect, QRectF, Qt
from PyQt5.QtGui import QPainterPath, QPainter, QColor, QPen
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QStyle, \
                            QGraphicsSceneMouseEvent


class Node(QGraphicsItem):
    Type = QGraphicsItem.UserType + 1

    # TODO Node info
    def __init__(self, graph_widget, label=None, info=None,
                 color=QColor(Qt.yellow)):
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
        self.size = QRect(-self.size_value, -self.size_value,
                          self.size_value * 2, self.size_value * 2)

        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setZValue(-1)
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
        painter.setBrush(color)
        painter.setPen(QPen(Qt.black, 0))
        painter.drawEllipse(self.size)

        if self.label:
            text_color = QColor.fromHslF((color.hslHueF() + 0.5) % 1,
                                         (color.hslSaturationF() + 0.5) % 1,
                                         (color.lightnessF() + 0.5) % 1)
            factor = (self.size.width() - 2) \
                / painter.fontMetrics().width(self.label)
            font = painter.font()
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
