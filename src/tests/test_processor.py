import unittest
from api import TextProcessor
from api.algorithm import DummyAlgorithm, DictionaryAlgorithm
from api.database import DataBaseConnection
from tests.config import Config as TestConfig


class TestTextProcessor(unittest.TestCase):
    """Тестирование основного класса API"""

    @classmethod
    def setUpClass(cls):
        DataBaseConnection(**TestConfig.NEO4J_DATA)
        TextProcessor().clear_db()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_parse_file(self):
        processor = TextProcessor([DictionaryAlgorithm])
        processor._analyzer.set_separator(r'\n')
        processor.parse_file('../samples/short.txt')
        processor.upload_db()
        self.assertGreater(len(processor._analyzer), 1)
        processor.apply_algorithms()
        processor.upload_db()
