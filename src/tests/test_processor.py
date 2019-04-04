import unittest
from api.processor import TextProcessor
from api.database.connection import DataBaseConnection
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
        processor = TextProcessor()
        processor._analyzer.set_separator(r'\n')
        processor.parse_file('../samples/short.txt')
        processor.upload_db()
        self.assertGreater(len(processor._analyzer), 1)
        processor.apply_algorithms()
        processor.upload_db()
