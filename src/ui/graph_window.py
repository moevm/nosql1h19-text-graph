from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QColor
from ui_compiled.graphwindow import Ui_GraphWindow
from ui.graph import GraphModule


class GraphWindow(QMainWindow, Ui_GraphWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.graph = GraphModule(self)
        self.graphicsView.setViewport(self.graph.widget)
        self.graph.add_node(1, 0, 0, color=QColor(Qt.red), label='test')
        self.graph.add_node(2, 100, 100, color=QColor(Qt.lightGray), label='test1')
        self.graph.add_node(3, 100, -100, label='test2 teeeeeeeeeeeeeeeeest')
        self.graph.add_edge(1, 2)
        self.graph.add_edge(2, 3)
        self.graph.add_edge(3, 1)
        self.graph.start_gravity()
