from PyQt5.QtWidgets import QMainWindow
from ui_compiled.graphwindow import Ui_GraphWindow
from ui.graph import GraphModule


class GraphWindow(QMainWindow, Ui_GraphWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.graph = GraphModule(self)
        self.graphicsView.setViewport(self.graph.widget)
        self.graph._add_node(1, 0, 0)
        self.graph._add_node(2, 100, 100)
        self.graph._add_edge(1, 2)
