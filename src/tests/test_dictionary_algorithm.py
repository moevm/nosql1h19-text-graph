import unittest

from api.algorithm.dictionary import DictionaryAlgorithm
from tests.fake.prebuilt import internationale_generator


# noinspection SpellCheckingInspection
class DictionaryAlgorithmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.algorithm = DictionaryAlgorithm(n=10)

    def test_check_word(self):
        self.assertTrue(self.algorithm.check_word('Проклятие'))
        self.assertFalse(self.algorithm.check_word('123'))
        self.assertFalse(self.algorithm.check_word('Hello'))
        self.assertTrue(self.algorithm.check_word('привет'))

    def test_stem(self):
        res = self.algorithm.do_stem('Вставай, проклятьем заклейменный!')
        self.assertEqual(['вставать', 'проклятие', 'заклеймить'], res)
        res = self.algorithm.do_stem('Je vois que je vous fais peur, \
                                     [2 - Я вижу, что я вас пугаю.]')
        self.assertEqual(['видеть', 'пугать'], res)

    def test_get_freq(self):
        test_words = [1] * 10 + [2] * 15 + [3] * 6
        res = self.algorithm.get_freq(test_words)
        self.assertEqual([(2, 15), (1, 10), (3, 6)], res)

    def test_get_freq_sep(self):
        test_words_arr = [[i] * i for i in range(100)]
        test_words = []
        for words_arr in test_words_arr:
            test_words.extend(words_arr)
        res = self.algorithm.get_freq(test_words)
        expected_res = [(i, i) for i in range(99, 89, -1)]
        self.assertEqual(res, expected_res)

    def test_preprocess(self):
        text = " ".join([t for t in internationale_generator()])
        res = self.algorithm.preprocess(text)["top_words"]
        self.assertTrue(('мир', 3) in res)
        self.assertTrue(('весь', 2) in res)
        self.assertTrue(('наш', 2) in res)

    def test_compare_results(self):
        res1 = [(i, i) for i in range(1, 10)]
        res2 = [(i + 10, i) for i in range(1, 10)]
        res3 = [(i, i) for i in range(1, 5)]
        res4 = [(i, i) for i in range(5, 10)]
        self.assertEqual(self.algorithm.compare_results(res1, res1)[0], 1)
        self.assertEqual(self.algorithm.compare_results(res1, res2)[0], 0)
        self.assertLess(self.algorithm.compare_results(res1, res3)[0], 0.5)
        self.assertGreater(self.algorithm.compare_results(res1, res4)[0], 0.5)
        # Транзитивность
        self.assertEqual(self.algorithm.compare_results(res1, res4)[0],
                         self.algorithm.compare_results(res4, res1)[0])
        res5 = [(i*5, i) for i in range(1, 10)]
        res6 = [(i*5, i) for i in range(5, 10)]
        self.assertLess(abs(self.algorithm.compare_results(res1, res4)[0]
                            - self.algorithm.compare_results(res5, res6)[0]),
                        0.00000001)
