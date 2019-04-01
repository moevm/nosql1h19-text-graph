import unittest
from api.analyzer import TextAnalyzer, SeparatorNotSetException


class TestTextAnalyzer(unittest.TestCase):
    """Тестирование анализатора текста"""

    def test_parse_fragments_throws(self):
        analyzer = TextAnalyzer()
        with self.assertRaises(SeparatorNotSetException):
            analyzer.parse_fragments('test')

    def test_parse_fragments(self):
        analyzer = TextAnalyzer()
        analyzer.set_separator(r' ')
        analyzer.parse_fragments('1 2 3 4')
        self.assertEqual(['1', '2', '3', '4'], analyzer.fragments)

