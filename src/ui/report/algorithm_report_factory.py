from logger import log
from .abstract import AbstractReportItem
from api import Describer


class AlgorithmReportItem(AbstractReportItem):
    def __init__(self, processor, algorithm, parent=None):
        self.name = f'Отчёт для алгоритма {algorithm.name}'
        self.algorithm = algorithm
        super().__init__(processor, parent)

    def create_html(self):
        describer = Describer(self.algorithm, self.processor)
        return describer.describe_results()


class AlgorithmReportFactory:
    def __init__(self, processor, item_parent):
        self.processor = processor
        self.item_parent = item_parent

    def get_report_items(self):
        items = []
        for algorithm in self.processor.algorithms:
            report_item = AlgorithmReportItem(self.processor, algorithm,
                                              self.item_parent)
            items.append(report_item)
        return items
