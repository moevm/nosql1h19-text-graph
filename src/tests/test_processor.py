import unittest
from api import TextProcessor
from api.algorithm import DummyAlgorithm, DictionaryAlgorithm
from api.database import DataBaseConnection
from tests.config import Config as TestConfig
from PyQt5.QtWidgets import QApplication
import sys


class TestTextProcessor(unittest.TestCase):
    """Тестирование основного класса API"""

    @classmethod
    def setUpClass(cls):
        DataBaseConnection(**TestConfig.NEO4J_DATA)
        TextProcessor().clear_db()
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_parse_file(self):
        processor = TextProcessor([DictionaryAlgorithm])
        processor.analyzer.set_separator(r'\n')
        processor.parse_file('../samples/short.txt', '\n{1}')
        processor.upload_db()
        self.assertGreater(len(processor.analyzer), 1)
        processor.do_preprocess()
        res, stats = processor.do_process(analyze=True)
        processor.upload_db()
        self.assertIsNotNone(res)
        self.assertIsNotNone(stats)

    def test_get_matrix(self):
        processor = TextProcessor([DictionaryAlgorithm, DummyAlgorithm])
        processor.analyzer.set_separator(r'\n')
        processor.parse_file('../samples/short.txt', '\n{1}')
        processor.upload_db()
        processor.do_preprocess()
        processor.do_process()
        processor.upload_db()

        matrix, head = processor.get_matrix('Dictionary')
        self.assertIsNotNone(matrix)
        self.assertGreater(len(matrix), 0)
        matrix2, head2 = processor.get_matrix('Dictionary', True)
        self.assertLessEqual(len(head2), len(head))
        self.assertLessEqual(len(matrix2), len(matrix))
        self.assertGreater(len(matrix2), 0)

        results = processor.get_node_list(head)
        self.assertGreater(len(results), 0)
        results_id = processor.get_node_id_list('Dictionary')
        self.assertGreater(len(results_id), 0)
