from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor
from typing import List, Tuple, Union, Dict
from ui.misc import get_foreground_color


class IntersectionItem(QTableWidgetItem):
    def __init__(self, value: float, min_val=0, relation=None):
        """

        :param value: Значение от 0 до 1, показывает процент связи
        :type value: float
        :param min_val: Значение отсечения связи
        :param relation: Объект, передаваемый при активации вершины
        """

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
    update_min_val = pyqtSignal(float)
    item_clicked = pyqtSignal(object)
    relation_clicked = pyqtSignal(object)

    def __init__(self, matrix: List[List[
                Tuple[float, Union[Dict, None]]
            ]], head, head_dicts, min_val=0, parent=None):
        """
        :param matrix: Отображаемая матрица из элементов вида:
            [Процент пересечения, Передаваемый при клике словарь]
        :type matrix: List[List[Tuple[float, Union[TextRelation, Dict, None]]]]
        :param head: Заголовки матрицы
        :param head_objects: Элементы, передаваемые при клике на соответсвующие
            заголовки матрицы
        :param min_val: Минимальное значение для подсветки
        :param parent: Родитель
        """
        super().__init__(parent)
        self.setEditTriggers(self.NoEditTriggers)
        self.setSelectionMode(self.SingleSelection)
        self.min_val = min_val
        self.head = [str(i) for i in head]
        self.head_objects = head_dicts
        self.setItems(matrix)
        self.setHorizontalHeaderLabels(self.head)
        self.setVerticalHeaderLabels(self.head)
        self.horizontalHeader().sectionClicked.connect(
            lambda i: self.item_clicked.emit(self.head_objects[i]))
        self.verticalHeader().sectionClicked.connect(
            lambda i: self.item_clicked.emit(self.head_objects[i]))
        self.itemActivated.connect(self.onRelationActivated)

    def setItems(self, matrix):
        self.setRowCount(len(matrix))
        if len(matrix) > 0:
            self.setColumnCount(len(matrix[0]))
        for i, row in enumerate(matrix):
            self.setColumnWidth(i, 10)
            for j, matrix_item in enumerate(row):
                value, relation = matrix_item
                item = IntersectionItem(value, self.min_val, relation)
                self.update_min_val.connect(item.updateText)
                self.setItem(i, j, item)

    def setMinVal(self, min_val):
        self.min_val = min_val
        self.update_min_val.emit(min_val)

    def onRelationActivated(self, item):
        if item.rel:
            self.relation_clicked.emit(item.rel)
