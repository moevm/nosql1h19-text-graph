from PyQt5.QtWidgets import QWidget

from api import Describer, Plotter
from api.algorithm import AbstractAlgorithm
from models import TextNode
from supremeSettings import SupremeSettings

from ui_compiled.algorithm_result import Ui_AlgorithmResult
from .matrix import MatrixWidget
from .text_widget import TextBrowser


class AlgorithmResults(QWidget, Ui_AlgorithmResult):
    def __init__(self, algorithm: AbstractAlgorithm, processor, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.settings = SupremeSettings()
        self.textBrowser = TextBrowser(self)
        self.textBrowserLayout.addWidget(self.textBrowser)

        self.algorithm = algorithm
        self.processor = processor
        self.elementsLabel.setText(str(len(self.processor.analyzer)**2))
        self.describer = Describer(algorithm, processor)
        self.plotter = Plotter(self.processor, self.algorithm)

        self.result_matrix = None
        self.hide_empty = False
        self.thresholdSlider.valueChanged.connect(
            self._on_threshold_slider_value_changed)
        self.hideEmptyCheckBox.stateChanged.connect(
            self._on_hide_empty_checkbox_state_changed)
        self.graphButton.clicked.connect(self._on_show_graph)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)

        self.exportButton.clicked.connect(self._on_export)
        self.updateButton.clicked.connect(self.update_results)

    def _on_hide_empty_checkbox_state_changed(self, value):
        self.hide_empty = value
        if self.settings['result_auto_update']:
            self.update_results()

    def _on_threshold_slider_value_changed(self, value):
        self.min_val = value / 100
        if self.result_matrix:
            if not self.hide_empty:
                self.result_matrix.set_min_val(self.min_val)
            elif self.settings['result_auto_update']:
                self.update_results()

    def _on_item_clicked(self, item: TextNode):
        self.textBrowser.setHtml(
            self.describer.describe_node(item))

    def _on_show_graph(self):
        from ui import GraphWindow
        self.graph_window = GraphWindow(self.processor, self.algorithm, self)
        self.graph_window.show()

    def _on_relation_clicked(self, item):
        id1, id2, intersection = item
        rel = self.processor.get_relation(self.algorithm.name, id1, id2)
        id1 = f"{id1} [{self.processor.get_node_label(id1)}]"
        id2 = f"{id2} [{self.processor.get_node_label(id2)}]"
        self.textBrowser.setHtml(
            self.describer.describe_query_relation(rel, id1, id2))

    def _on_export(self):
        min_val = self.thresholdSlider.value() / 100
        Plotter.display(self.plotter.algorithm_matrix(min_val))

    def update_results(self):
        min_val = self.thresholdSlider.value() / 100
        matrix, head = self.processor.get_matrix(
            self.algorithm.name, self.hide_empty, min_val)
        head_items = self.processor.get_node_list(head)
        head_names = self.processor.get_node_label_list(head)
        if self.result_matrix:
            self.resultMatrixLayout.removeWidget(self.result_matrix)
            self.result_matrix.deleteLater()
        else:
            for i in range(self.resultMatrixLayout.count()):
                self.resultMatrixLayout.removeItem(
                    self.resultMatrixLayout.itemAt(i))
            self.loadLabel.deleteLater()

        self.result_matrix = MatrixWidget(matrix, head_names, head_items,
                                          min_val, self)
        self.result_matrix.item_clicked.connect(self._on_item_clicked)
        self.result_matrix.relation_clicked.connect(self._on_relation_clicked)
        self.resultMatrixLayout.addWidget(self.result_matrix)

    def _set_matrix_widget(self, widget: MatrixWidget):
        if self.result_matrix:
            self.resultMatrixLayout.removeWidget(self.result_matrix)
            self.result_matrix.deleteLater()
        self.result_matrix = widget
        self.result_matrix.item_clicked.connect(self._on_item_clicked)
        self.result_matrix.relation_clicked.connect(self._on_relation_clicked)
        self.resultMatrixLayout.addWidget(self.result_matrix)
