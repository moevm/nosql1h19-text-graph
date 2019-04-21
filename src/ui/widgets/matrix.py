from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor
from typing import List, Tuple, Union, Dict
from ui.misc import get_foreground_color
from models import TextRelation


class IntersectionItem(QTableWidgetItem):
    def __init__(self, value: float, min_val=0, relation=None):
        super().__init__()
        self.val = value
        self.updateText(min_val)
        self.rel = relation

    def updateText(self, min_val):
        self.min_val = min_val
        if self.val < self.min_val:
            self.back = QColor(Qt.lightGray)
        else:
            p = (self.val - self.min_val) / (1 - self.min_val)
            hue = 120 / 360 * p
            self.back = QColor.fromHslF(hue, 0.6, 0.5)
        self.front = get_foreground_color(self.back)
        self.setBackground(QBrush(self.back))
        self.setForeground(QBrush(self.front))
        self.setText(str(int(self.val * 100)) + '%')


class MatrixWidget(QTableWidget):
    updateMinVal = pyqtSignal(float)

    def __init__(self, matrix: List[List[
                Tuple[float, Union[TextRelation, Dict, None]]
            ]], head, min_val=0, parent=None):
        super().__init__(parent)
        self.setEditTriggers(self.NoEditTriggers)
        self.min_val = min_val
        self.head = [str(i) for i in head]
        self.setItems(matrix)
        self.setHorizontalHeaderLabels(self.head)
        self.setVerticalHeaderLabels(self.head)

    def setItems(self, matrix):
        self.setRowCount(len(matrix))
        if len(matrix) > 0:
            self.setColumnCount(len(matrix[0]))
        for i, row in enumerate(matrix):
            self.setColumnWidth(i, 10)
            for j, matrix_item in enumerate(row):
                value, relation = matrix_item
                item = IntersectionItem(value, self.min_val, relation)
                self.updateMinVal.connect(item.updateText)
                self.setItem(i, j, item)

    def setMinVal(self, min_val):
        self.min_val = min_val
        self.updateMinVal.emit(min_val)
