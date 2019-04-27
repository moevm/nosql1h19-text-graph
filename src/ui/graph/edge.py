import math
import numpy as np
from typing import List
from PyQt5.QtCore import QLineF, QPointF, QRectF, QSizeF, Qt
from PyQt5.QtGui import QPainter, QPen, QPolygonF, QColor, QBrush, QPainterPath
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QStyle, \
                            QGraphicsSceneMouseEvent

from .graphwidget import GraphWidget
from .node import Node
from supremeSettings import SupremeSettings


class AnimatedObject:
    item: QGraphicsItem
    position: int


class Edge(QGraphicsItem):
    source_point: QPointF
    dest_point: QPointF
    animations: List[AnimatedObject]

    def __init__(self, source: Node, dest: Node,
                 widget: GraphWidget, info=None, weight=1, arrow_size=10):
        super().__init__()
        self.source, self.dest = source, dest
        self.id = f"{source.id}-{dest.id}"
        self.weight = weight
        self.arrow_size = arrow_size
        self.selection_offset = 5
        self.setAcceptHoverEvents(True)
        self.info = info
        source.addEdge(self)
        self.setZValue(0)
        dest.addEdge(self)
        self.widget = widget
        self.animations = []

    def adjust(self):
        if not self.source or not self.dest:
            return
        line = QLineF(
            self.mapFromItem(
                self.source, 0, 0), self.mapFromItem(
                self.dest, 0, 0))
        length = line.length()
        self.prepareGeometryChange()
        if length > 20:
            edge_offset = QPointF(
                (line.dx() * self.source.size.width() / 2) / length,
                (line.dy() * self.source.size.height() / 2) / length)
            self.source_point = line.p1() + edge_offset
            self.dest_point = line.p2() - edge_offset
        else:
            self.source_point = self.dest_point = line.p1()

    def getSelectionPolygon(self):
        line = QLineF(self.source_point, self.dest_point)
        angle = line.angle() * np.pi / 180
        dx = self.selection_offset * np.sin(angle)
        dy = self.selection_offset * np.cos(angle)
        offset1 = QPointF(dx, dy)
        offset2 = QPointF(-dx, -dy)
        points = [line.p1() + offset1,
                  line.p1() + offset2,
                  line.p2() + offset2,
                  line.p2() + offset1]
        polygon = QPolygonF(points)
        return polygon

    def boundingRect(self):
        return self.getSelectionPolygon().boundingRect()

    def shape(self):
        path = QPainterPath()
        path.addPolygon(self.getSelectionPolygon())
        return path

    def boundingRect_old(self):
        if not self.source_point or not self.dest_point:
            return QRectF()
        pen_width = 1
        extra = (pen_width + self.arrow_size) / 2.0
        return QRectF(self.source_point,
                      QSizeF(self.dest_point.x() - self.source_point.x(),
                      self.dest_point.y() - self.source_point.y())) \
            .normalized() \
            .adjusted(-extra, -extra, extra, extra)

    def get_color(self):
        hue = 120 * self.weight / 360
        color = QColor.fromHslF(hue, 1, 0.5)
        return color

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget=None):
        if not self.source or not self.dest:
            return
        line = QLineF(self.source_point, self.dest_point)
        if line.length() == 0.0:
            return
        color = self.get_color()
        width = SupremeSettings()['edge_width']
        if option.state & QStyle.State_Sunken:
            color, width = Qt.red, 2
            painter.setPen(QPen(Qt.black, 2, Qt.DashLine))
            painter.drawPolygon(self.getSelectionPolygon())
        elif option.state & QStyle.State_MouseOver:
            color, width = Qt.blue, 2
        painter.setPen(QPen(color, width, Qt.SolidLine,
                            Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(line)
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = math.pi * 2 - angle
        if self.arrow_size > 0:
            dest_arrow_p1 = self.dest_point + QPointF(
                math.sin(
                    angle - math.pi / 3) * self.arrow_size,
                math.cos(
                    angle - math.pi / 3) * self.arrow_size)
            dest_arrow_p2 = self.dest_point + QPointF(
                math.sin(
                    angle - math.pi + math.pi / 3) * self.arrow_size,
                math.cos(
                    angle - math.pi + math.pi / 3) * self.arrow_size)
            painter.setBrush(color)
            painter.drawPolygon(
                QPolygonF([line.p2(), dest_arrow_p1, dest_arrow_p2]))
        self.draw_animated_objects()

    def add_animation(self, item: QGraphicsItem, position: int):
        item.setParentItem(self)
        item.setPos(self.source_point)
        item.update()
        animated_object = AnimatedObject()
        animated_object.item = item
        animated_object.position = position
        self.animations.append(animated_object)

    def add_ellipse_animation(self, color: QColor, position: int = 0):
        ellipse = self.widget.scene().addEllipse(0, 0, 10, 10)
        ellipse.setPen(QPen(color, 0))
        ellipse.setBrush(QBrush(color))
        self.add_animation(ellipse, position)

    def draw_animated_objects(self):
        for animated in self.animations:
            coef = 1 - animated.position / 100
            xs = self.source_point.x() - 5
            ys = self.source_point.y() - 5
            xd = self.dest_point.x() - 5
            yd = self.dest_point.y() - 5
            newx = xs * coef + xd * (1 - coef)
            newy = ys * coef + yd * (1 - coef)
            animated.item.setX(newx)
            animated.item.setY(newy)
            animated.item.update()

    def process_animations(self):
        for animated in self.animations:
            animated.position = (animated.position + 1) % 100

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        self.update()
        self.grabMouse()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        self.update()
        self.ungrabMouse()
