from PyQt5.QtWidgets import QWidget
from ui_compiled.algorithm_result import Ui_AlgorithmResult
from api import Describer
from api.algorithm import AbstractAlgorithm
from .matrix import MatrixWidget
from models import TextNode


class AlgorithmResults(QWidget, Ui_AlgorithmResult):
    def __init__(self, algorithm: AbstractAlgorithm, processor, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.algorithm = algorithm
        self.processor = processor
        self.describer = Describer(algorithm, processor)

        self.result_matrix = None
        self.hide_empty = False
        self.thresholdSlider.valueChanged.connect(
            self.on_thresholdslider_value_changed)
        self.hideEmptyCheckBox.stateChanged.connect(
            self.on_hide_empty_checkbox_state_changed)
        self.graphButton.clicked.connect(self.on_show_graph)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.updateButton.clicked.connect(self.update_results)

    def on_hide_empty_checkbox_state_changed(self, value):
        self.hide_empty = value
        self.update_results()

    def on_thresholdslider_value_changed(self, value):
        self.min_val = value / 100
        if self.result_matrix:
            if not self.hide_empty:
                self.result_matrix.set_min_val(self.min_val)
            else:
                self.update_results()

    def on_item_clicked(self, item: TextNode):
        self.textBrowser.setHtml(
            self.describer.describe_node(item))

    def on_show_graph(self):
        from ui import GraphWindow
        self.graph_window = GraphWindow(self.processor, self.algorithm, self)
        self.graph_window.show()

    def on_relation_clicked(self, item):
        id1, id2, item = item
        self.textBrowser.setHtml(
            self.describer.describe_query_relation(item, id1, id2))

    def update_results(self):
        min_val = self.thresholdSlider.value() / 100
        matrixModel, head = self.processor.get_matrix(
            self.algorithm.name, self.hide_empty, min_val)
        head_items = self.processor.get_node_list(head)
        if self.result_matrix:
            self.resultMatrixLayout.removeWidget(self.result_matrix)
            self.result_matrix.deleteLater()
        self.result_matrix = MatrixWidget(matrixModel, head, head_items,
                                          min_val, self)
        self.result_matrix.item_clicked.connect(self.on_item_clicked)
        self.result_matrix.relation_clicked.connect(self.on_relation_clicked)
        self.resultMatrixLayout.addWidget(self.result_matrix)

    def _set_matrix_widget(self, widget: MatrixWidget):
        if self.result_matrix:
            self.resultMatrixLayout.removeWidget(self.result_matrix)
            self.result_matrix.deleteLater()
        self.result_matrix = widget
        self.result_matrix.item_clicked.connect(self.on_item_clicked)
        self.result_matrix.relation_clicked.connect(self.on_relation_clicked)
        self.resultMatrixLayout.addWidget(self.result_matrix)
