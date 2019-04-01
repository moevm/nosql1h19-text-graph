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
        TextProcessor().clear_db()

    def test_parse_file(self):
        processor = TextProcessor()

        processor._analyzer.set_separator(r'\n')
        processor.parse_file('../samples/denikin_sketch.txt')
        self.assertGreater(len(processor._analyzer), 1)
        processor.upload_db()

        processor2 = TextProcessor()
        processor2.download_db()
        self.assertEqual(processor._analyzer._fragments,
                         processor2._analyzer._fragments)

        processor.clear_db()

