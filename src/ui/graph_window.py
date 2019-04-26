from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QColor
from ui_compiled.graphwindow import Ui_GraphWindow
from ui.graph import GraphModule
from api import TextProcessor, Describer
from models import TextNode

import numpy as np


class GraphWindow(QMainWindow, Ui_GraphWindow):
    def __init__(self, processor: TextProcessor,
                 algorithm=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.graph = GraphModule(self)
        self.graphWidgetLayout.addWidget(self.graph.widget)
        self.processor = processor
        self.setupAlgorithms(algorithm)

        self.describer = Describer(self.algorithm, processor)
        self.populateGraph()

        self.excludeZerosCheckBox.stateChanged.connect(
            self.updateGraph)
        self.thresholdSlider.valueChanged.connect(
            self.updateGraph)
        #  self.graph.do_gravity_ticks(1000)
        self.graph.start_gravity()

    def setupAlgorithms(self, algorithm=None):
        alg_list = [alg.name for alg in self.processor.algorithms]
        self.algorithmComboBox.addItems(alg_list)
        self.algorithmComboBox.setCurrentIndex(0)
        if algorithm:
            self.algorithm = algorithm
        else:
            self.onChangeAlgorithms(alg_list[0])

    def onChangeAlgorithms(self, name: str):
        self.algorithm = self.processor.alg_by_name(name)

    def getNodeParams(self, node: TextNode):
        x = np.random.random() * 200 - 100
        y = np.random.random() * 200 - 100
        color = QColor.fromRgbF(*[np.random.random() for _ in range(3)])
        return x, y, color

    def updateGraph(self):
        self.graph.clear()
        self.populateGraph()

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
                                label=str(node.order_id), info=info)
        if res:
            for id1, id2, rel, res_a in res:
                weight = rel['intersection']
                info = self.describer.describe_query_relation(rel, id1, id2)
                self.graph.add_edge(id1, id2, ud=True, info=info,
                                    weight=weight)

    def resizeEvent(self, event):
        super().resizeEvent(event)
