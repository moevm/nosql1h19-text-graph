import unittest
from api.algorithm import DiffAlgorithm
from supremeSettings import SupremeSettings


text1 = """
    Hello!
    Goodbye!
"""
text2 = """
    Hello!
    Hello!
"""

text3 = """
    Hello!
    Goooo
"""

class TestDiffAlgorithm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.alg = DiffAlgorithm()

    def test_compare(self):
        diff, inter = self.alg.compare_texts(text1, text2)
        self.assertIsNotNone(diff)
        self.assertTrue(0 < inter < 1)
        self.assertEqual(self.alg.compare_texts(text1, text1)[1], 1)
        self.assertTrue(0 < self.alg.compare_texts(text1, text3)[1] < 1)
        self.assertEqual(self.alg.compare_texts(text1, text2)[1],
                         self.alg.compare_texts(text2, text1)[1])

    def test_compare_lines(self):
        diff, inter = self.alg.compare_texts_lines(text1, text2)
        self.assertIsNotNone(diff)
        self.assertTrue(0 < inter < 1)
        self.assertEqual(self.alg.compare_texts_lines(text1, text1)[1], 1)
        self.assertTrue(0 < self.alg.compare_texts_lines(text1, text3)[1] < 1)
        self.assertEqual(self.alg.compare_texts_lines(text1, text2)[1],
                         self.alg.compare_texts_lines(text2, text1)[1])

    def test_process(self):
        res1, res2 = self.alg.preprocess(text1), self.alg.preprocess(text2)
        comp = self.alg.compare(res1, res2)
        self.assertTrue(0 < comp['intersection'] < 1)
        self.assertIsNotNone(comp['data'])

        desc = self.alg.describe_comparison(comp)
        self.assertGreater(len(desc), 0)
