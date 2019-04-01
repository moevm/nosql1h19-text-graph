from typing import List
from api.algorithm.abstract import AbstractAlgorithm
from api.algorithm.dictionary import DictionaryAlgorithm
from api.analyzer import TextAnalyzer
from models.text_node import TextNode


class TextProcessor:
    """Класс, выполняющие основные операции по работе с текстами"""

    def __init__(self):
        self.algorithm_classes = [DictionaryAlgorithm]
        self.algorithms: List[AbstractAlgorithm] = []
        self.analyzer = TextAnalyzer()
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
        self.analyzer.read_file(filename)

    def clear_df(self):
        """Очищает БД"""
        nodes = TextNode.nodes.all()
        for node in nodes:
            node.delete()

    def download_db(self):  # TODO
        """Загрузить данные из БД в список фрагментов"""
        pass

    def upload_db(self):  # TODO
        """Загрузить данные в БД из анализатора"""
        for index, fragment in zip(
                range(len(self.analyzer.fragments)),
                self.analyzer.fragments):
            fragment = TextNode(order_id=index, text=fragment)
            fragment.save()
