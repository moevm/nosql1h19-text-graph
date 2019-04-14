from ui.graph import Node, Edge, GraphWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow
import numpy as np


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

        self.gravity_timer = None  # Таймер для работы с гравитацией

    def _add_node(self, id, pos_x, pos_y, **kwargs):
        node = Node(self.widget, **kwargs)
        node.setPos(pos_x, pos_y)
        self.widget.scene().addItem(node)
        self.nodes[id] = node

    def _add_edge(self, id1, id2, **kwargs):
        edge = Edge(self.nodes[id1], self.nodes[id2], self.widget, **kwargs)
        self.widget.scene().addItem(edge)

    def start_gravity(self):
        if self.gravity_timer:
            return
        self.gravity_timer = QTimer(self.widget)
        self.gravity_timer.start(20)
        self.gravity_timer.timeout.connect(self._process_gravity)

    def _process_gravity(self):
        new_coords = {}
        for id, node in self.nodes.items():
            new_coords[id] = self._calculate_forces(node)
        for id in self.nodes:
            x, y = new_coords[id]
            self.nodes[id].setX(x)
            self.nodes[id].setY(y)

    def _calculate_forces(self, node: Node):
        """ Вычислить новые координаты вершины  """
        if self.widget.scene().mouseGrabberItem() == node:
            return node.x(), node.y()
        xvel, yvel = 0, 0
        vertex_weight = 250  # TODO Settings

        # Силы, отталкивающие вершины
        for node2 in self.nodes.values():
            if not node2 == node:
                dx = node.x() - node2.x()
                dy = node.y() - node2.y()
                length = np.linalg.norm((dx, dy))
                xvel += dx * vertex_weight / length**2
                yvel += dy * vertex_weight / length**2

        # Силы, притягивающие вершины
        weight = (len(node.edge_list) + 1)**1.3 * 10
        for edge in node.edge_list:
            if edge.source == node:
                dx = node.x() - edge.dest.x()
                dy = node.y() - edge.dest.x()
            else:
                dx = node.x() - edge.source.x()
                dy = node.y() - edge.source.y()
            xvel -= dx / weight
            yvel -= dy / weight

        # TODO Силы, отталкивающие вершины от границ

        if np.linalg.norm((xvel, yvel)) < 0.2:
            xvel = yvel = 0

        new_x, new_y = node.x() + xvel, node.y() + yvel
        return new_x, new_y
