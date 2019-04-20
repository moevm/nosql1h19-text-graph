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
        processor.do_process()
        processor.upload_db()
