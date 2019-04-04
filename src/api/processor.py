from typing import List
from api.algorithm import AbstractAlgorithm, DictionaryAlgorithm
from api import FragmentsAnalyzer


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
        self._analyzer = FragmentsAnalyzer()
        self._analyzer.download_db()
        self.set_up_algorithms()

    def set_up_algorithms(self):
        """Инициализация алгоритмов"""
        self.algorithms = []
        for algorithm_class in self.algorithm_classes:
            self.algorithms.append(algorithm_class())

    def parse_file(self, filename: str):
        """Считать файл и вытащить из него все фрагменты

        :param filename:
        :type filename: str
        """
        self._analyzer.read_file(filename)

    def apply_algorithms(self):
        """Применить набор алгоритмов к вершинам"""
        for algorithm in self.algorithms:
            for node in self._analyzer:
                if not node.alg_results:
                    node.alg_results = algorithm.preprocess(node.text)
                else:
                    node.alg_results = {
                        **node.alg_results,
                        **algorithm.preprocess(node.text)
                    }
        for i in range(len(self._analyzer)):
            for j in range(i + 1, len(self._analyzer)):
                node1 = self._analyzer[i]
                node2 = self._analyzer[j]
                for algorithm in self.algorithms:
                    result = algorithm.compare(node1.alg_results,
                                               node2.alg_results)
                    node1.link.connect(
                        node2, {
                            "algorithm_name": algorithm.name,
                            "intersection": result["intersection"],
                            "results": result["data"]
                        }
                    )

    def clear_db(self):
        """Очистить БД"""
        self._analyzer.clear()

    def upload_db(self):
        """Загрузить изменения в БД"""
        self._analyzer.upload_db()
