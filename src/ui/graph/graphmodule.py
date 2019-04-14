from ui.graph import Node, Edge, GraphWidget
from PyQt5.QtWidgets import QMainWindow


class GraphModule:
    """
    Класс, занимающийся работой с GraphWidget.
    """
    def __init__(self, window: QMainWindow, nodes=None, edges=None):
        """Конструктор класса

        :param window: Окно-родитель для GraphWidget
        :type window: QMainWindow
        :param nodes: Список вида {
            id: Id Вершины,
            args: Список аргументов для конструктора Node
        }
        :param edges: Список вида {
            id: Id Ребра,
            args: Список аргументов для конструктора Edge
        }
        """
        self.window = window
        self.widget = GraphWidget(self.window)

        self.nodes = {}  # Хранилище вершин
        self.edges = {}  # Хранилище связей

    def _add_node(self, id, pos_x, pos_y, **kwargs):
        node = Node(self.widget, **kwargs)
        node.setPos(pos_x, pos_y)
        self.widget.scene().addItem(node)
        self.nodes[id] = node

    def _add_edge(self, id1, id2, **kwargs):
        edge = Edge(self.nodes[id1], self.nodes[id2], self.widget, **kwargs)
        self.widget.scene().addItem(edge)
