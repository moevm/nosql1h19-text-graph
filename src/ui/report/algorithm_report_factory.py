from PyQt5.QtGui import QBrush, QColor
import numpy as np

from .abstract import AbstractReportItem
from api import Describer, Plotter


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


class AlgorithmMatrixGraph(AbstractReportItem):
    def __init__(self, processor, algorithm, parent=None):
        self.name = f'Матрица для алгоритма {algorithm.name}'
        self.algorithm = algorithm
        self.min_val = 0  # TODO?
        super().__init__(processor, parent)

    def create_html(self):
        plotter = Plotter(self.processor, self.algorithm)
        fig = plotter.algorithm_matrix(self.min_val)
        fig_base = Plotter.fig_to_base64_tag(fig)
        return f"""
            <center>
                {fig_base}
            </center>
        """


class AlgorithmIntersectionGraph(AbstractReportItem):
    def __init__(self, processor, algorithm, parent=None):
        self.name = f'Распределение пересечений для {algorithm.name}'
        self.algorithm = algorithm
        super().__init__(processor, parent)

    def create_html(self):
        plotter = Plotter(self.processor, self.algorithm)
        fig = plotter.intersection_plot()
        fig_base = Plotter.fig_to_base64_tag(fig)
        return f"<center> {fig_base} </center>"


class AlgorithmReportFactory:
    def __init__(self, processor, item_parent):
        self.processor = processor
        self.item_parent = item_parent

    def get_report_items(self):
        items = []
        for algorithm in self.processor.algorithms:
            report_item = AlgorithmReportItem(self.processor, algorithm,
                                              self.item_parent)
            matr_graph = AlgorithmMatrixGraph(self.processor, algorithm,
                                              self.item_parent)
            inter_graph = AlgorithmIntersectionGraph(self.processor, algorithm,
                                                     self.item_parent)
            alg_items = [report_item, matr_graph, inter_graph]
            color = random_color()
            [item.setBackground(QBrush(color)) for item in alg_items]
            items.extend(alg_items)
        return items
