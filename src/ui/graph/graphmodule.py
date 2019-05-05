from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QGraphicsItem, QMessageBox
import sys
import re
from fa2 import ForceAtlas2
import networkx as nx
import numpy as np

from supremeSettings import SupremeSettings
from ui.graph import Node, Edge, GraphWidget, TextItem
from api import Plotter
from logger import log


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
        self.fa2 = ForceAtlas2(
            outboundAttractionDistribution=False,
            scalingRatio=100.0,
            verbose=False,
            gravity=10.0
        )

        self._nodes = {}  # Хранилище вершин
        self._edges = {}  # Хранилище связей
        self._texts = {}  # Хранилище текстов
        self.get_relation_text = lambda item: str(item)
        self.matrix = None
        self.positions = None

        self.gravity_timer = None  # Таймер для работы с гравитацией
        self.widget.item_right_clicked.connect(self._on_item_clicked)

    def add_text(self, id, pos_x, pos_y, parent_item=None, **kwargs):
        """Добавить текст

        :param id: Уникальный id текста
        :param pos_x: x-координата
        :param pos_y: y-координата
        :param parent_node: вершина-родитель
        :param **kwargs: Аргументы конструктора TextItem
        """
        text = TextItem(id=id, parent=parent_item, **kwargs)
        if parent_item:
            pos_x -= parent_item.x()
            pos_y -= parent_item.y()
        text.setPos(pos_x, pos_y)
        text.linkActivated.connect(self._on_text_link_clicked)
        self._texts[id] = text

    def add_node(self, id, pos_x, pos_y, **kwargs):
        """Добавить вершину

        :param id: Уникальный идентификатор вершины
        :param pos_x: x-координата вершины
        :param pos_y: y-координата вершины
        :param **kwargs: Аргументы конструктора Node
        """
        # assert id not in self._nodes
        if id in self._nodes:
            log.warning(f"{id} уже добавлена")
        node = Node(self.widget, id=id, **kwargs)
        node.setPos(pos_x, pos_y)
        self.widget.scene().addItem(node)
        self._nodes[id] = node

    def add_edge(self, id1, id2, ud=False, **kwargs):
        """Добавить ребро

        :param id1: source id
        :param id2: target id
        :param ud: не добавлять связь, если уже есть связь в другую сторону
        :param **kwargs: Аргументы конструктора Edge
        """
        assert (id1, id2) not in self._edges
        if ud and (id2, id1) in self._edges:
            return
        edge = Edge(self._nodes[id1], self._nodes[id2], self.widget, **kwargs)
        self._edges[(id1, id2)] = edge
        self.widget.scene().addItem(edge)

    def _on_text_link_clicked(self, link):
        if link[:11] == 'internal://':
            if re.search(r'close\?id=[0-9\-]+', link):
                id = link[re.search(r'id=[0-9\-]+', link).start()+3:]
                try:
                    self.widget.scene().removeItem(self._texts[id])
                except KeyError:
                    id = int(id)
                    self.widget.scene().removeItem(self._texts[id])
                del self._texts[id]

    def _on_item_clicked(self, item: QGraphicsItem):
        if isinstance(item, Node) and item.info \
                and item.id not in self._texts:
            self.add_text(item.id, item.x() + 15, item.y() + 15,
                          item, html_text=item.info)
        elif isinstance(item, Edge) and item.info \
                and item.id not in self._texts:
            x = (item.dest.x() - item.source.x()) / 2 + item.source.x()
            y = (item.dest.y() - item.source.y()) / 2 + item.source.y()
            self.add_text(item.id, x, y, parent_item=item.source,
                          html_text=self.get_relation_text(item.info))

    def clear(self):
        self._nodes.clear()
        self._edges.clear()
        self._texts.clear()
        self.matrix = None
        self.widget.scene().clear()

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

    def calculate_matrix(self, weight=None):
        head = list(self._nodes.keys())
        self.head = head
        self.matrix = np.zeros(len(head)**2).reshape((len(head), len(head)))
        self.positions = [[0, 0] for _ in range(len(head))]
        for key, edge in self._edges.items():
            id1, id2 = key
            id1, id2 = head.index(id1), head.index(id2)
            self.matrix[id1][id2] = edge.weight if weight is None else weight
            self.matrix[id2][id1] = edge.weight if weight is None else weight
        for id_, node in self._nodes.items():
            self.positions[head.index(id_)] = [node.x(), node.y()]
        self.positions = np.array(self.positions)

    def save_graph(self):
        fig = Plotter.save_to_graph(self)
        Plotter.display(fig)

    def relayout_graph(self, name: str):
        """Расположить вершины графа по какому-то алгоритму.
        Алгоритмы:
            * circular - по кругу
            * kamada_kawai - Kamada-Kawai Algorithm
            * planar - без пересечений ребер
            * random - рандом
            * shell - пока то же, что circular
            * spring - Fruchterman-Reingold Algorithm
        :param name:
        :type name: str
        """
        def kamada_kawai(G):
            return nx.kamada_kawai_layout(G, weight=1)

        # def spectral(G):
        #    return nx.spectral_layout(G, scale=20)

        func_dict = {
            'circular': nx.circular_layout,
            'kamada_kawai': kamada_kawai,
            'planar': nx.planar_layout,
            'random': nx.random_layout,
            'shell': nx.shell_layout,  # TODO
            'spring': nx.spring_layout,
            # 'spectral': spectral
        }
        scale_dict = {
            'circular': 0.5,
            'random': 0.3
        }

        self.calculate_matrix()
        matrix = np.array(self.matrix)
        G = nx.from_numpy_matrix(matrix)  # Получить networkx-граф из матрицы
        try:
            pos = func_dict[name](G)
        except nx.exception.NetworkXException:
            self.box = QMessageBox.critical(self.widget,
                                            'Ошибка', 'Граф не планарен')
            return

        # Расчехлить позиции
        pos = np.array([pos[i] for i in range(len(pos))])

        # Масштабировать
        scale = SupremeSettings()['graphmodule_graph_scale']
        try:
            pos = nx.rescale_layout(pos, scale=scale * scale_dict[name])
        except KeyError:
            pos = nx.rescale_layout(pos, scale=scale)

        # Применить позиции
        for index, position in enumerate(pos):
            x, y = position
            node = self._nodes[self.head[index]]
            if node != self.widget.scene().mouseGrabberItem():
                node.setX(x)
                node.setY(y)
        self._adjust_scene()

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
        if self.gravity_timer \
                or not SupremeSettings()['graphmodule_gravity_enabled']:
            return
        self.gravity_timer = QTimer(self.widget)
        self.gravity_timer.start(
            SupremeSettings()['graphmodule_timer_interval'])
        self.gravity_timer.timeout.connect(self._process_gravity)

    def stop_gravity(self):
        if self.gravity_timer:
            self.gravity_timer.stop()
            self.gravity_timer.deleteLater()
            self.gravity_timer = None

    def do_gravity_ticks(self, ticks):
        """Выполнить нужное количество тиков расчёта гравитации.
        Можно использовать для первоначальной стабилизации сцены.

        :param ticks: Количество тиков
        """
        self.stop_gravity()
        for _ in range(ticks):
            self._process_gravity()
        self.start_gravity()

    def _process_gravity(self, ticks=1):
        """ Один тик обработки взаимодействия вершин """
        self.calculate_matrix()
        if len(self.matrix) > 0:
            positions = self.fa2.forceatlas2(
                self.matrix, pos=self.positions, iterations=ticks)
            for index, position in enumerate(positions):
                x, y = position
                node = self._nodes[self.head[index]]
                if node != self.widget.scene().mouseGrabberItem():
                    node.setX(x)
                    node.setY(y)
            self.positions = np.array(positions)
        self._adjust_scene()
