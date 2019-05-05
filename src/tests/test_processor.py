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

    def _fill_db(self):
        processor = TextProcessor([DictionaryAlgorithm, DummyAlgorithm])
        processor.clear_db()
        processor.analyzer.set_separator(r'\n')
        processor.parse_file('../samples/short.txt', '\n{1}')
        processor.upload_db()
        processor.do_preprocess()
        processor.do_process()
        processor.upload_db()
        return processor

    def test_parse_file(self):
        processor = TextProcessor([DictionaryAlgorithm])
        processor.analyzer.set_separator(r'\n')
        processor.parse_file('../samples/short.txt', '\n{1}')
        processor.upload_db()
        self.assertGreater(len(processor.analyzer), 1)
        processor.do_preprocess()
        processor.upload_db()
        res, stats = processor.do_process(analyze=True)
        self.assertIsNotNone(res)
        self.assertIsNotNone(stats)

    def test_get_node_id_list(self):
        processor = self._fill_db()
        head_full, res = processor.get_node_id_list('Dictionary')
        head_part, res = processor.get_node_id_list('Dictionary',
                                                    exclude_zeros=True)
        self.assertEqual(len(head_full), len(processor.analyzer))
        self.assertLessEqual(len(head_part), len(head_full))

    def test_get_matrix(self):
        processor = self._fill_db()
        matrix_full, head_full = processor.get_matrix('Dictionary')
        self.assertEqual(len(matrix_full), len(head_full))
        for row in matrix_full:
            self.assertGreaterEqual(sum(row), 1)
        matrix_part, head_part = processor.get_matrix('Dictionary',
                                                      exclude_zeros=True)
        self.assertEqual(len(matrix_part), len(head_part))
        if len(head_part) > 0:
            for row in matrix_part:
                self.assertGreater(sum(row), 1)
