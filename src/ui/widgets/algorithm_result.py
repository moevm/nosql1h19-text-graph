from PyQt5.QtWidgets import QWidget

from api import Describer, Plotter
from api.algorithm import AbstractAlgorithm
from models import TextNode

from ui_compiled.algorithm_result import Ui_AlgorithmResult
from .matrix import MatrixWidget
from .text_widget import TextBrowser
from .range_slider import QRangeSlider


class AlgorithmResults(QWidget, Ui_AlgorithmResult):
    def __init__(self, algorithm: AbstractAlgorithm, processor, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.textBrowser = TextBrowser(self)
        self.textBrowserLayout.addWidget(self.textBrowser)

        self.algorithm = algorithm
        self.processor = processor
        self.describer = Describer(algorithm, processor)
        self.plotter = Plotter(self.processor, self.algorithm)

        self._init_ranges()
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

    def _init_ranges(self):
        self.rowsSlider = QRangeSlider(self)
        self.columnsSlider = QRangeSlider(self)
        frag_num = len(self.processor.analyzer)

        self.rowsSlider.startValueChanged.connect(self._update_elem_number)
        self.rowsSlider.endValueChanged.connect(self._update_elem_number)
        self.columnsSlider.startValueChanged.connect(self._update_elem_number)
        self.columnsSlider.endValueChanged.connect(self._update_elem_number)

        self.rowsSlider.setMax(frag_num)
        self.columnsSlider.setMax(frag_num)
        self.rowsSlider.setRange(0, frag_num)
        self.columnsSlider.setRange(0, frag_num)

        self.rowsSliderLayout.addWidget(self.rowsSlider)
        self.columnsSliderLayout.addWidget(self.columnsSlider)

    def _update_elem_number(self):
        num = (self.rowsSlider.end() - self.rowsSlider.start()) \
            * (self.columnsSlider.end() - self.columnsSlider.start())
        self.elementsLabel.setText(str(num))

    def _on_hide_empty_checkbox_state_changed(self, value):
        self.hide_empty = value
        self.update_results()

    def _on_threshold_slider_value_changed(self, value):
        self.min_val = value / 100
        if self.result_matrix:
            if not self.hide_empty:
                self.result_matrix.set_min_val(self.min_val)
            else:
                self.update_results()

    def _on_item_clicked(self, item: TextNode):
        self.textBrowser.setHtml(
            self.describer.describe_node(item))

    def _on_show_graph(self):
        from ui import GraphWindow
        self.graph_window = GraphWindow(self.processor, self.algorithm, self)
        self.graph_window.show()

    def _on_relation_clicked(self, item):
        id1, id2, item = item
        id1 = f"{id1} [{self.processor.get_node_label(id1)}]"
        id2 = f"{id2} [{self.processor.get_node_label(id2)}]"
        self.textBrowser.setHtml(
            self.describer.describe_query_relation(item, id1, id2))

    def _on_export(self):
        min_val = self.thresholdSlider.value() / 100
        Plotter.display(self.plotter.algorithm_matrix(min_val))

    def update_results(self):
        min_val = self.thresholdSlider.value() / 100
        __import__('pudb').set_trace()
        matrixModel, head = self.processor.get_matrix(
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

        self.result_matrix = MatrixWidget(matrixModel, head_names, head_items,
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
