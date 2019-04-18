from typing import List, Pattern
from api.algorithm import AbstractAlgorithm, DictionaryAlgorithm
from api import FragmentsAnalyzer
from neomodel import db


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

    def apply_algorithms(self):
        """Применить набор алгоритмов к вершинам"""
        for algorithm in self.algorithms:
            for node in self.analyzer:
                if not node.alg_results:
                    node.alg_results = algorithm.preprocess(node.text)
                else:
                    node.alg_results = {
                        **node.alg_results,
                        **algorithm.preprocess(node.text)
                    }
        for i in range(len(self.analyzer)):
            for j in range(i + 1, len(self.analyzer)):
                node1 = self.analyzer[i]
                node2 = self.analyzer[j]
                for algorithm in self.algorithms:
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

    def clear_db(self):
        """Очистить  БД"""
        try:  # TODO
            self.analyzer.clear()
        except:
            db.set_connection('bolt://neo4j:kinix951@localhost:7687')
            self.analyzer.upload_db()

    def upload_db(self):
        """Загрузить изменения в БД"""
        try:  # TODO
            self.analyzer.upload_db()
        except:
            db.set_connection('bolt://neo4j:kinix951@localhost:7687')
            self.analyzer.upload_db()
