import unittest
from api.analyzer import FragmentsAnalyzer, SeparatorNotSetException


class TestTextAnalyzer(unittest.TestCase):
    """Тестирование анализатора текста"""

    def test_parse_fragments_throws(self):
        analyzer = FragmentsAnalyzer()
        with self.assertRaises(SeparatorNotSetException):
            analyzer.parse_fragments('test')

    def test_parse_fragments(self):
        analyzer = FragmentsAnalyzer()
        analyzer.set_separator(r' ')
        analyzer.parse_fragments('1 2 3 4')
        self.assertEqual(['1', '2', '3', '4'], analyzer._fragments)

    def test_read_file(self):
        analyzer = FragmentsAnalyzer()
        analyzer.set_separator(r'\n')
        analyzer.read_file('../samples/denikin_sketch.txt')
        self.assertGreater(len(analyzer._fragments), 1)

    def test_iteration(self):
        analyzer = FragmentsAnalyzer()
        analyzer.set_separator(r'\n')
        analyzer.read_file('../samples/denikin_sketch.txt')
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
