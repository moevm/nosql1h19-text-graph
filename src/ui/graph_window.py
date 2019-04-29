from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QColor
from ui_compiled.graphwindow import Ui_GraphWindow
from ui.graph import GraphModule
from api import TextProcessor, Describer
from models import TextNode
from supremeSettings import SupremeSettings

import numpy as np


class GraphWindow(QMainWindow, Ui_GraphWindow):
    def __init__(self, processor: TextProcessor,
                 algorithm=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.graph = GraphModule(self)

        self.actionCalibrate.triggered.connect(self.on_calibrate)

        self.graphWidgetLayout.addWidget(self.graph.widget)
        self.processor = processor
        self.setupAlgorithms(algorithm)

        self.describer = Describer(self.algorithm, processor)
        self.populateGraph()

        self.excludeZerosCheckBox.stateChanged.connect(
            self.updateGraph)
        self.thresholdSlider.valueChanged.connect(
            self.updateGraph)
        self.algorithmComboBox.currentIndexChanged.connect(self.updateGraph)

        self.relayoutButton.clicked.connect(
            lambda: self.graph.relayout_graph(
                self.layoutComboBox.currentText()))

        self.gravityCheckBox.stateChanged.connect(self.toggle_gravity)

        self.graph.start_gravity()

    def setupAlgorithms(self, algorithm=None):
        alg_list = [alg.name for alg in self.processor.algorithms]
        self.algorithmComboBox.addItems(alg_list)
        self.algorithmComboBox.setCurrentIndex(0)
        if algorithm:
            self.algorithm = algorithm
        else:
            self.onChangeAlgorithms(alg_list[0])

    def toggle_gravity(self, state):
        state = state != 0
        SupremeSettings()['graphmodule_gravity_enabled'] = state
        if state == False:
            self.graph.stop_gravity()
        else:
            self.graph.start_gravity()

    def on_calibrate(self):
        self.graph.do_gravity_ticks(1000)

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
                                label=str(node.label), info=info)
        if res:
            for id1, id2, rel, res_a in res:
                if min_val < 1:
                    weight = (rel['intersection'] - min_val) / (1 - min_val)
                else:
                    weight = 1
                info = self.describer.describe_query_relation(rel, id1, id2)
                self.graph.add_edge(id1, id2, ud=True, info=info,
                                    weight=weight)

    def resizeEvent(self, event):
        super().resizeEvent(event)
