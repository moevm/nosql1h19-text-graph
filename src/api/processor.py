from typing import List
from api.algorithm.abstract import AbstractAlgorithm
from api.algorithm.dictionary import DictionaryAlgorithm
from api.analyzer import FragmentsAnalyzer
from models.text_node import TextNode


class TextProcessor:
    """Класс, выполняющие основные операции по работе с фрагментами"""

    def __init__(self):
        self.algorithm_classes = [DictionaryAlgorithm]
        self.algorithms: List[AbstractAlgorithm] = []
        self._analyzer = FragmentsAnalyzer()
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

    def clear_db(self):
        """Очищает БД"""
        nodes = TextNode.nodes.all()
        for node in nodes:
            node.delete()

    def download_db(self):
        """Загрузить данные из БД в список фрагментов"""
        self._analyzer.clear()
        nodes = TextNode.nodes.all()
        nodes.sort(key=lambda node: node.order_id)
        for node in nodes:
            self._analyzer.append(node.text)

    def upload_db(self):
        """Загрузить данные в БД из анализатора"""
        self.clear_db()
        for fragment in self._analyzer:
            node = fragment.to_TextNode()
            node.save()
