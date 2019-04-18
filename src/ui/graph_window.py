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
        self.graphWidgetLayout.addWidget(self.graph.widget)
        self.graph.add_node(1, 0, 0, color=QColor(Qt.red), label='test',
                            info='kek1')
        self.graph.add_node(2, 100, 100, color=QColor(Qt.lightGray),
                            label='test1', info='kek2')
        self.graph.add_node(3, 100, -100, label='test2 teeeee',
                            info='kek3')
        self.graph.add_edge(1, 2)
        self.graph.add_edge(2, 3)
        self.graph.add_edge(3, 1)
        self.graph.add_text(10, 0, 0, html_text="<b>Test</b>")
        self.graph.do_gravity_ticks(1000)
        self.graph.start_gravity()

    def resizeEvent(self, event):
        super().resizeEvent(event)
