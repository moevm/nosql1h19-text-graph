from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QColor
from ui_compiled.graphwindow import Ui_GraphWindow
from ui.graph import GraphModule
from api import TextProcessor, Describer
from models import TextNode
from supremeSettings import SupremeSettings

import numpy as np


__all__ = ['GraphWindow']


class GraphWindow(QMainWindow, Ui_GraphWindow):
    def __init__(self, processor: TextProcessor,
                 algorithm=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.graph = GraphModule(self)
        self.graph.get_relation_text = self._describe_relation

        self.graphWidgetLayout.addWidget(self.graph.widget)
        self.processor = processor
        self.setupAlgorithms(algorithm)

        self.describer = Describer(self.algorithm, processor)
        self.populateGraph()

        self.actionSaveGraph.triggered.connect(self.saveGraph)

        self.excludeZerosCheckBox.stateChanged.connect(
            self.updateGraph)
        self.thresholdSlider.valueChanged.connect(
            self.updateGraph)
        self.algorithmComboBox.currentIndexChanged.connect(self.updateGraph)

        self.relayoutButton.clicked.connect(
            lambda: self.graph.relayout_graph(
                self.layoutComboBox.currentText()))

        self.gravityCheckBox.stateChanged.connect(self.toggle_gravity)
        self.gravityCheckBox.setChecked(
            SupremeSettings()['graphmodule_gravity_enabled'])

        self.graph.start_gravity()

    def setupAlgorithms(self, algorithm=None):
        alg_list = [alg.name for alg in self.processor.algorithms]
        self.algorithmComboBox.addItems(alg_list)
        self.algorithmComboBox.setCurrentIndex(0)
        if algorithm:
            self.algorithm = algorithm
            self.algorithmComboBox.setCurrentIndex(
                self.processor.algorithms.index(self.algorithm))
        else:
            self.onChangeAlgorithms(alg_list[0])

    def toggle_gravity(self, state):
        state = state != 0
        SupremeSettings()['graphmodule_gravity_enabled'] = state
        if state is False:
            self.graph.stop_gravity()
        else:
            self.graph.start_gravity()

    def onChangeAlgorithms(self, name: str):
        self.algorithm = self.processor.alg_by_name(name)

    def getNodeParams(self, node: TextNode):
        x = np.random.random() * 400 - 200
        y = np.random.random() * 400 - 200
        color = QColor.fromRgbF(
            *[np.random.random() * 0.5 + 0.5 for _ in range(3)])
        return x, y, color

    def updateGraph(self):
        self.graph.clear()
        self.populateGraph()

    def _describe_relation(self, item):
        id1, id2 = item
        rel = self.processor.get_relation(self.algorithm.name, id1, id2)
        text = self.describer.describe_query_relation(rel, id1, id2)
        return text

    def populateGraph(self):
        min_val = self.thresholdSlider.value() / 100
        head, res = self.processor.get_node_id_list(
            self.algorithm.name, self.excludeZerosCheckBox.isChecked(),
            min_val)
        nodes = self.processor.get_node_list(head)
        for node in nodes:
            info = self.describer.describe_node(node)
            x, y, color = self.getNodeParams(node)
            self.graph.add_node(node.order_id, x, y, color=color,
                                label=str(node.label), info=info)
        if res:
            for id1, id2, intersection in res:
                if min_val < 1:
                    weight = (intersection - min_val + 0.005) \
                           / (1 - min_val)
                else:
                    weight = 1
                info = (id1, id2)
                self.graph.add_edge(id1, id2, ud=True, info=info,
                                    weight=weight)

    def saveGraph(self):
        self.graph.save_graph()
