from PyQt5.QtGui import QBrush, QColor
import numpy as np

from .abstract import AbstractReportItem
from api import Describer, Plotter
from api.graph_algs import centrality_algs, comm_algs, GraphAlgDispatcher


def random_color():
    return QColor.fromRgbF(*[np.random.random() * 0.5 + 0.5 for _ in range(3)])


class AlgorithmReportItem(AbstractReportItem):
    def __init__(self, processor, algorithm, parent=None):
        self.name = f'[{algorithm.name}]: Общий отчёт'
        self.algorithm = algorithm
        super().__init__(processor, parent)

    def create_html(self):
        describer = Describer(self.algorithm, self.processor)
        return describer.describe_results()


class AlgortithmCentralityItem(AbstractReportItem):
    def __init__(self, processor, algorithm, parent=None):
        self.name = f'[{algorithm.name}]: Алгоритмы центральности'
        self.algorithm = algorithm
        self.settings = {'algorithms': {}}
        self.gui_settings = {
            'Выбор алгоритмов': {
                'algorithms': 'Алгоритмы'
            }
        }
        self.graph_algs = []
        for graph_alg in centrality_algs:
            alg = graph_alg(processor, algorithm)
            self.settings['algorithms'][alg.name] = True
            self.graph_algs.append(alg)
        super().__init__(processor, parent)

    def _test_func(self, graph_alg):
        return self.settings['algorithms'][graph_alg.name]

    def create_html(self):
        algs = [alg for alg in self.graph_algs
                if self.settings['algorithms'][alg.name]]
        describer = Describer(self.algorithm, self.processor)
        dispatcher = GraphAlgDispatcher(self.processor, self.algorithm)
        results = dispatcher.dispatch_centrality(self._test_func)
        return describer.describe_centrality_results(results)


class AlgortithmCommunityItem(AbstractReportItem):
    def __init__(self, processor, algorithm, parent=None):
        self.name = f'[{algorithm.name}]: Разбиение на сообщества'
        self.algorithm = algorithm
        self.settings = {
            'algorithms': {},
            'min_val': 0.
        }
        self.gui_settings = {
            'Выбор алгоритмов': {
                'algorithms': 'Алгоритмы',
                'min_val': 'Минимальное значение связи [0-1]'
            }
        }
        self.comm_algs = []
        for graph_alg in comm_algs:
            alg = graph_alg(processor, algorithm)
            self.settings['algorithms'][alg.name] = True
            self.comm_algs.append(alg)
        super().__init__(processor, parent)

    def _test_func(self, graph_alg):
        return self.settings['algorithms'][graph_alg.name]

    def create_html(self):
        algs = [alg for alg in self.comm_algs
                if self.settings['algorithms'][alg.name]]
        describer = Describer(self.algorithm, self.processor)
        dispatcher = GraphAlgDispatcher(self.processor, self.algorithm)
        results = dispatcher.dispatch_community(
            self._test_func, min_val=self.settings['min_val'])
        return describer.describe_community_results(results)


class AlgorithmMatrixGraph(AbstractReportItem):
    def __init__(self, processor, algorithm, parent=None):
        self.name = f'[{algorithm.name}]: Матрица пересечений'
        self.algorithm = algorithm
        self.settings = {
            'min_val': 0.
        }
        self.gui_settings = {
            'Настройки связи': {
                'min_val': 'Минимальное значение связи'
            }
        }
        super().__init__(processor, parent)

    def create_html(self):
        min_val = self.settings['min_val']
        plotter = Plotter(self.processor, self.algorithm)
        fig = plotter.algorithm_matrix(min_val)
        fig_base = Plotter.fig_to_base64_tag(fig)
        return f"""
            <center>
                {fig_base}
            </center>
        """


class AlgorithmIntersectionGraph(AbstractReportItem):
    def __init__(self, processor, algorithm, parent=None):
        self.name = f'[{algorithm.name}] Распределение пересечений'
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
            args = self.processor, algorithm, self.item_parent
            report_item = AlgorithmReportItem(*args)
            matr_graph = AlgorithmMatrixGraph(*args)
            inter_graph = AlgorithmIntersectionGraph(*args)
            centr_item = AlgortithmCentralityItem(*args)
            comm_item = AlgortithmCommunityItem(*args)

            alg_items = [report_item, matr_graph, inter_graph, centr_item,
                         comm_item]
            color = random_color()
            [item.setBackground(QBrush(color)) for item in alg_items]
            items.extend(alg_items)
        return items
