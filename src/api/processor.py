from typing import List, Pattern
from api.algorithm import AbstractAlgorithm, DictionaryAlgorithm
from api import FragmentsAnalyzer
from PyQt5.QtCore import QThread, pyqtSignal, QObject


class AlgorithmWorker(QObject):
    percentDone = pyqtSignal(int)  # TODO percent
    algorithmDone = pyqtSignal(int)
    processingDone = pyqtSignal()

    def __init__(self, processor, parent=None):
        super().__init__(parent)
        self.proc = processor
        self.interval = 1
        self.iter_num = 1
        self.i = 0

    def setInterval(self, iter_num):
        self.iter_num = iter_num
        if iter_num <= 100:
            self.interval = 1
        else:
            self.interval = int(iter_num / 100)

    def checkPercent(self, iter_):  # TODO is this optimal?
        if self.interval == 1:
            self.percentDone.emit(int(iter_ / self.iter_num * 100))
        else:
            self.i += 1
            if self.i == self.interval:
                self.percentDone.emit(int(iter_ / self.iter_num * 100))
                self.i = 0

    def doPreprocess(self):
        self.setInterval(len(self.proc.analyzer))
        for index, algorithm in enumerate(self.proc.algorithms):
            for index, node in enumerate(self.proc.analyzer):
                self.checkPercent(index)
                if not node.alg_results:
                    node.alg_results = algorithm.preprocess(node.text)
                else:
                    node.alg_results = {
                        **node.alg_results,
                        **algorithm.preprocess(node.text)
                    }
            self.algorithmDone.emit(index)
        self.processingDone.emit()

    def doProcess(self):
        self.setInterval(len(self.proc.analyzer))
        for i in range(len(self.proc.analyzer)):
            for j in range(i + 1, len(self.proc.analyzer)):
                node1 = self.proc.analyzer[i]
                node2 = self.proc.analyzer[j]
                for algorithm in self.proc.algorithms:
                    result = algorithm.compare(node1.alg_results,
                                               node2.alg_results)
                    if result["intersection"] > 0:
                        node1.link.connect(
                            node2, {
                                "algorithm_name": algorithm.name,
                                "intersection": result["intersection"],
                                "results": result["data"]
                            }
                        )
            self.checkPercent(i)
        self.processingDone.emit()


class TextProcessor:
    """Класс, выполняющие основные операции по работе с фрагментами.
    Внесение изменений в фрагменты требует явного выполнения синхронизации.
    Таким образом в БД не будут занесены ошибочные данные"""

    def __init__(self, algorithm_classes=None):
        if not algorithm_classes:
            self.algorithm_classes = [DictionaryAlgorithm]
        else:
            self.algorithm_classes = algorithm_classes
        self.algorithms: List[AbstractAlgorithm] = []
        self.analyzer = FragmentsAnalyzer()
        self.analyzer.download_db()
        self.set_up_algorithms()
        self.worker_thread = QThread()

    def set_up_algorithms(self):
        """Инициализация алгоритмов"""
        self.algorithms = []
        for algorithm_class in self.algorithm_classes:
            self.algorithms.append(algorithm_class())

    def parse_file(self, filename: str, regex: Pattern):
        """Считать файл и вытащить из него все фрагменты

        :param filename:
        :type filename: str
        """
        self.analyzer.set_separator(regex)
        self.analyzer.read_file(filename)
        self.upload_db()

    def _init_worker(self):
        self.worker = AlgorithmWorker(self)
        self.worker.moveToThread(self.worker_thread)
        self.worker.processingDone.connect(self.worker_thread.quit)
        self.worker_thread.start()

    def do_preprocess(self):
        self._init_worker()
        self.worker.doPreprocess()

    def do_process(self):
        self._init_worker()
        self.worker.doProcess()

    # TODO delete this?
    # def apply_algorithms_old(self):
    #     """Применить набор алгоритмов к вершинам"""
    #     for algorithm in self.algorithms:
    #         for node in self.analyzer:
    #             if not node.alg_results:
    #                 node.alg_results = algorithm.preprocess(node.text)
    #             else:
    #                 node.alg_results = {
    #                     **node.alg_results,
    #                     **algorithm.preprocess(node.text)
    #                 }
    #     for i in range(len(self.analyzer)):
    #         for j in range(i + 1, len(self.analyzer)):
    #             node1 = self.analyzer[i]
    #             node2 = self.analyzer[j]
    #             for algorithm in self.algorithms:
    #                 result = algorithm.compare(node1.alg_results,
    #                                            node2.alg_results)
    #                 if result["intersection"] > 0:
    #                     node1.link.connect(
    #                         node2, {
    #                             "algorithm_name": algorithm.name,
    #                             "intersection": result["intersection"],
    #                             "results": result["data"]
    #                         }
    #                     )

    def clear_db(self):
        """Очистить  БД"""
        self.analyzer.clear()

    def upload_db(self):
        """Загрузить изменения в БД"""
        self.analyzer.upload_db()
