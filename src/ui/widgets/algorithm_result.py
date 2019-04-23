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

        self.resultMatrix = None
        self.hideEmpty = False
        self.thresholdSlider.valueChanged.connect(
            self.onThresholdSliderValueChanged)
        self.hideEmptyCheckBox.stateChanged.connect(
            self.onHideEmptyCheckBoxStateChanged)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.updateResults()

    def onHideEmptyCheckBoxStateChanged(self, value):
        self.hideEmpty = value
        self.updateResults()

    def onThresholdSliderValueChanged(self, value):
        self.min_val = value / 100
        if self.resultMatrix:
            if not self.hideEmpty:
                self.resultMatrix.setMinVal(self.min_val)
            else:
                self.updateResults()

    def onItemClicked(self, item: TextNode):
        self.textBrowser.setHtml(
            self.describer.describeNode(item))

    def onRelationClicked(self, item):
        id1, id2, item = item
        self.textBrowser.setHtml(
            self.describer.describeQueryRelation(item, id1, id2))

    def updateResults(self):  # TODO Это в отдельный тред
        min_val = self.thresholdSlider.value() / 100
        matrixModel, head = self.processor.get_matrix(
            self.algorithm.name, self.hideEmpty, min_val)
        head_items = self.processor.get_node_list(head)
        if self.resultMatrix:
            self.resultMatrixLayout.removeWidget(self.resultMatrix)
            self.resultMatrix.deleteLater()
        self.resultMatrix = MatrixWidget(matrixModel, head, head_items,
                                         min_val, self)
        self.resultMatrix.item_clicked.connect(self.onItemClicked)
        self.resultMatrix.relation_clicked.connect(self.onRelationClicked)
        self.resultMatrixLayout.addWidget(self.resultMatrix)
