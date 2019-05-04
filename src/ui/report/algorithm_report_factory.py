from PyQt5.QtGui import QBrush, QColor
import numpy as np

from .abstract import AbstractReportItem
from api import Describer, Saver


def random_color():
    return QColor.fromRgbF(*[np.random.random() * 0.5 + 0.5 for _ in range(3)])


class AlgorithmReportItem(AbstractReportItem):
    def __init__(self, processor, algorithm, parent=None):
        self.name = f'Отчёт для алгоритма {algorithm.name}'
        self.algorithm = algorithm
        super().__init__(processor, parent)

    def create_html(self):
        describer = Describer(self.algorithm, self.processor)
        return describer.describe_results()


class AlgorithmMatrixItem(AbstractReportItem):
    def __init__(self, processor, algorithm, parent=None):
        self.name = f'Матрица для алгоритма {algorithm.name}'
        self.algorithm = algorithm
        self.min_val = 0  # TODO?
        super().__init__(processor, parent)

    def create_html(self):
        matrix, head = self.processor.get_matrix(self.algorithm.name,
                                                 min_val=self.min_val)
        matrix = np.array(matrix)[:, :, 0]
        head = self.processor.get_node_label_list(head)
        fig = Saver.save_to_matrix(matrix, head)
        fig_base = Saver.fig_to_base64(fig)
        return f"""
            <h3>
                Матрица пересечения для алгоритма {self.algorithm.name}
            </h3>
            <p>
                <img src="data:image/jpeg;base64,{fig_base}" />
            </p>
        """


class AlgorithmReportFactory:
    def __init__(self, processor, item_parent):
        self.processor = processor
        self.item_parent = item_parent

    def get_report_items(self):
        items = []
        for algorithm in self.processor.algorithms:
            report_item = AlgorithmReportItem(self.processor, algorithm,
                                              self.item_parent)
            matrix_item = AlgorithmMatrixItem(self.processor, algorithm,
                                              self.item_parent)
            alg_items = [report_item, matrix_item]
            color = random_color()
            [item.setBackground(QBrush(color)) for item in alg_items]
            items.extend(alg_items)
        return items
