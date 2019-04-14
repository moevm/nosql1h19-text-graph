from ui.graph import Node, Edge, GraphWidget, TextItem
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow
import numpy as np
import sys
import re


class GraphModule:
    """
    Класс, занимающийся работой с GraphWidget.
    """

    def __init__(self, window: QMainWindow, nodes=None, edges=None, **kwargs):
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
        :param kwargs: Аргументы для GraphWidget
        """
        self.window = window
        self.widget = GraphWidget(self.window, **kwargs)

        self._nodes = {}  # Хранилище вершин
        self._edges = {}  # Хранилище связей
        self._texts = {}  # Хранилище текстов

        self.gravity_timer = None  # Таймер для работы с гравитацией

    def add_text(self, id, pos_x, pos_y, parent_id=None, **kwargs):
        """Добавить текст

        :param id: Уникальный id текста
        :param pos_x: x-координата
        :param pos_y: y-координата
        :param **kwargs: Аргументы конструктора TextItem
        """
        assert id not in self._texts
        try:
            parent_node = self._nodes[parent_id]
        except KeyError:
            parent_node = None
        text = TextItem(id=id, parent=parent_node, **kwargs)
        text.setPos(pos_x, pos_y)
        text.linkActivated.connect(self._on_text_link_clicked)
        self._texts[id] = text
        self.widget.scene().addItem(text)

    def add_node(self, id, pos_x, pos_y, **kwargs):
        """Добавить вершину

        :param id: Уникальный идентификатор вершины
        :param pos_x: x-координата вершины
        :param pos_y: y-координата вершины
        :param **kwargs: Аргументы конструктора Node
        """
        assert id not in self._nodes
        node = Node(self.widget, **kwargs)
        node.setPos(pos_x, pos_y)
        self.widget.scene().addItem(node)
        self._nodes[id] = node

    def add_edge(self, id1, id2, **kwargs):
        """Добавить ребро

        :param id1: source id
        :param id2: target id
        :param **kwargs: Аргументы конструктора Edge
        """
        edge = Edge(self._nodes[id1], self._nodes[id2], self.widget, **kwargs)
        self.widget.scene().addItem(edge)

    def _on_text_link_clicked(self, link):
        if link[:11] == 'internal://':
            if re.search(r'close\?id=[0-9]+', link):
                id = link[re.search(r'id=[0-9]+', link).start()+3:]
                try:
                    self.widget.scene().removeItem(self._texts[id])
                except KeyError:
                    id = int(id)
                    self.widget.scene().removeItem(self._texts[id])
                del self._texts[id]

    @property
    def nodes(self):
        """Вернуть список вершин.
        Возможно (TODO), здесь будет реализовано скрытие вершин
        """
        return list(self._nodes.values())

    @property
    def edges(self):
        """Вернуть список ребер"""
        return list(self._edges.values())

    def _adjust_scene(self):
        """ Подровнять сцену под вершины """
        if len(self.nodes) == 0:
            self.widget.scene().setSceneRect(-200, -200, 400, 400)
        min_x, min_y, max_x, max_y = sys.maxsize, sys.maxsize, \
            -sys.maxsize, -sys.maxsize
        for node in self.nodes + list(self._texts.values()):
            min_x = min(node.x(), min_x)
            min_y = min(node.y(), min_y)
            max_x = max(node.x(), max_x)
            max_y = max(node.y(), max_y)
        margin = 30
        x, y = min_x, min_y
        w, h = max(max_x - min_x, 100), max(max_y - min_y, 100)
        self.widget.scene().setSceneRect(x-margin, y-margin,
                                         w+margin*2, h+margin*2)

    def start_gravity(self):
        """ Запустить расчёт взаимодействия вершин """
        if self.gravity_timer:
            return
        self.gravity_timer = QTimer(self.widget)
        self.gravity_timer.start(20)
        self.gravity_timer.timeout.connect(self._process_gravity)

    def do_gravity_ticks(self, ticks):
        """Выполнить нужное количество тиков расчёта гравитации.
        Можно использовать для первоначальной стабилизации сцены.

        :param ticks: Количество тиков
        """
        for _ in range(ticks):
            self._process_gravity()

    def _process_gravity(self):
        """ Один тик обработки взаимодействия вершин """
        new_coords = {}
        for id, node in self._nodes.items():
            new_coords[id] = self._calculate_forces(node)
        for id in self._nodes:
            x, y = new_coords[id]
            self._nodes[id].setX(x)
            self._nodes[id].setY(y)
        if not self.widget.scene().mouseGrabberItem():
            self._adjust_scene()

    def _calculate_forces(self, node: Node):
        """ Вычислить новые координаты вершины  """
        if self.widget.scene().mouseGrabberItem() == node:
            return node.x(), node.y()
        xvel, yvel = 0, 0
        vertex_weight = 250  # TODO Settings

        # Силы, отталкивающие вершины
        for node2 in self._nodes.values():
            if node2 != node:
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
                dy = node.y() - edge.dest.y()
            else:
                dx = node.x() - edge.source.x()
                dy = node.y() - edge.source.y()
            xvel -= dx / weight
            yvel -= dy / weight

        if np.linalg.norm((xvel, yvel)) < 0.2:
            xvel = yvel = 0

        new_x, new_y = node.x() + xvel, node.y() + yvel
        return new_x, new_y
