from typing import List, Pattern
from api.algorithm import AbstractAlgorithm, DictionaryAlgorithm
from api import FragmentsAnalyzer
from logger import log
from loading_wrapper import LoadingThread


class TextProcessor:
    """Класс, выполняющие основные операции по работе с фрагментами.
    Внесение изменений в фрагменты требует явного выполнения синхронизации.
    Таким образом в БД не будут занесены ошибочные данные"""

    # TODO Подумать над объединенем TextProcessor и TextAnalyzer

    class PreprocessThread(LoadingThread):
        def __init__(self, proc, parent=None):
            super().__init__(parent)
            self.proc = proc
            self.operation = 'Выполнение предобработки'
            self.setInterval(len(proc.analyzer))

        def run(self):
            for index, algorithm in enumerate(self.proc.algorithms):
                self.updateStatus.emit(f'Обработка алгоритма {index}')
                log.info(f'Preprocessing for {algorithm}')
                for index, node in enumerate(self.proc.analyzer):
                    self.checkPercent(index)
                    if not node.alg_results:
                        node.alg_results = algorithm.preprocess(node.text)
                    else:
                        node.alg_results = {
                            **node.alg_results,
                            **algorithm.preprocess(node.text)
                        }
            self.loadingDone.emit()

    class ProcessThread(LoadingThread):
        def __init__(self, proc, parent=None):
            super().__init__(parent)
            self.proc = proc
            self.operation = 'Выполнение алгоритмов'
            self.setInterval(len(proc.analyzer))

        def run(self):
            log.info('Started processing')
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
            self.loadingDone.emit()

    class ClearResultsThread(LoadingThread):
        def __init__(self, proc, parent=None):
            super().__init__(parent)
            self.operation = 'Очистка результатов'
            self.proc = proc
            self.setInterval(len(self.proc.analyzer))

        def run(self):
            for index, node in enumerate(self.proc.analyzer):
                node.link.disconnect_all()
                self.checkPercent(index)
            self.loadingDone.emit()

    def __init__(self, algorithm_classes=None):
        super().__init__()
        if not algorithm_classes:
            self.algorithm_classes = [DictionaryAlgorithm]
        else:
            self.algorithm_classes = algorithm_classes
        self.algorithms: List[AbstractAlgorithm] = []
        self.analyzer = FragmentsAnalyzer()
        self.analyzer.download_db()
        self.set_up_algorithms()

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

    def do_preprocess(self):
        thread = self.PreprocessThread(self)
        thread.run()
        thread.wait()

    def do_process(self):
        thread = self.ProcessThread(self)
        thread.run()
        thread.wait()

    def clear_db(self):
        """Очистить  БД"""
        self.analyzer.clear()

    def upload_db(self):
        """Загрузить изменения в БД"""
        thread = self.analyzer.UploadDBThread(self.analyzer)
        thread.run()
        thread.wait()

    def clear_results(self):
        """Удалить результаты из БД"""
        thread = self.ClearResultsThread(self)
        thread.run()
        thread.wait()
