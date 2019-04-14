from PyQt5.QtCore import QRectF, Qt, QTimer
from PyQt5.QtGui import QPainter, QBrush, QKeyEvent, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene


class GraphWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        scene = QGraphicsScene(self)
        scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        scene.setSceneRect(-200, -200, 400, 400)
        self.setScene(scene)
        self.setCacheMode(self.CacheBackground)
        self.setViewportUpdateMode(self.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        animationTimer = QTimer(self)
        animationTimer.start(10)
        animationTimer.timeout.connect(self.process_animations)

    def drawBackground(self, painter: QPainter, rect: QRectF):
        scene_rect = self.sceneRect()
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(scene_rect)

    def process_animations(self):
        from .edge import Edge
        for item in self.scene().items():
            if isinstance(item, Edge):
                item.process_animations()

    def item_moved(self):
        return

    def scale_view(self, scale_factor):
        factor = self.transform().scale(scale_factor, scale_factor).mapRect(QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scale_factor, scale_factor)

    def zoom_in(self):
        self.scale_view(1.2)

    def zoom_out(self):
        self.scale_view(1 / 1.2)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Plus:
            self.zoom_in()
        elif event.key() == Qt.Key_Minus:
            self.zoom_out()
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        self.scale_view(2**(-event.angleDelta().y() / 240))
