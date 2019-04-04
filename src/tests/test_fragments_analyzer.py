import unittest
from api.analyzer import FragmentsAnalyzer, SeparatorNotSetException
from api.database.connection import DataBaseConnection
from models.text_node import TextNode
from tests.config import Config as TestConfig


class TestTextAnalyzer(unittest.TestCase):
    """Тестирование анализатора текста"""

    @classmethod
    def setUpClass(cls):
        DataBaseConnection(**TestConfig.NEO4J_DATA)
        [node.delete() for node in TextNode.nodes.all()]

    def test_parse_fragments_throws(self):
        analyzer = FragmentsAnalyzer()
        with self.assertRaises(SeparatorNotSetException):
            analyzer._parse_fragments('test')

    def test_parse_fragments(self):
        analyzer = FragmentsAnalyzer()
        analyzer.set_separator(r' ')
        analyzer._parse_fragments('1 2 3 4')
        self.assertEqual(['1', '2', '3', '4'], [n.text
                                                for n in analyzer._fragments])

    def test_read_file(self):
        analyzer = FragmentsAnalyzer()
        analyzer.set_separator(r'\n')
        analyzer.read_file('../samples/short.txt')
        self.assertGreater(len(analyzer._fragments), 1)
        analyzer.upload_db()

        analyzer2 = FragmentsAnalyzer()
        analyzer2.download_db()
        self.assertEqual(analyzer._fragments, analyzer2._fragments)

        analyzer.clear()

    def test_iteration(self):
        analyzer = FragmentsAnalyzer()
        analyzer.set_separator(r'\n')
        analyzer.read_file('../samples/short.txt')
        self.assertEqual(len(analyzer), len(analyzer._fragments))

        fragments = [f for f in analyzer]
        key_fragments = [analyzer[i] for i in range(len(analyzer))]
        self.assertEqual(len(fragments), len(analyzer))
        self.assertEqual(fragments, key_fragments)
        self.assertNotEqual(analyzer[0], analyzer[1])

        old_len = len(analyzer)
        del analyzer[0]
        self.assertEqual(old_len, len(analyzer) + 1)

        analyzer.clear()
        self.assertEqual(len(analyzer), 0)
