import re
from typing import Dict, List, Tuple, Any

from api.algorithm import NotSoAbstractAlgorithm

FreqList = List[Tuple[int, Any]]


class DictionaryAlgorithm(NotSoAbstractAlgorithm):
    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return 'Dictionary'

    @property
    def preprocess_keys(self):
        return ['tokens', 'top_words']

    def check_word(self, word: str) -> bool:
        """
        Проверяет, удовлетворяет ли слово заданным критерием
        :param word: одно слово (токен)
        :return: True или False
        """
        if not re.match(self.word_regex, word):
            return False
        return word not in self.stopwords

    def do_stem(self, text: str) -> List[str]:
        """
        Производить стемминг текста
        :param text: Текст для обработки
        :return: Список из слов в нормальной форме
        """
        tokens = self.stem.lemmatize(text.lower())
        tokens = [token for token in tokens if self.check_word(token)]
        return tokens

    def get_freq(self, tokens: List) -> FreqList:
        """
        Определяет частоту встречи слов в списке.
        Единственное условие - элементы списка должны быть хэшируемы
        :param tokens: Список из хэшируемых элементов
        :return: Отсортированный список из кортежей вида (частота, элемент)
        из n элементов
        """
        hash_map = dict()
        for token in tokens:
            try:
                hash_map[token] += 1
            except KeyError:
                hash_map[token] = 1
        sorted_list = sorted(
            hash_map.items(),
            key=lambda x: x[1],
            reverse=True)
        if len(sorted_list) > self.words_num:
            sorted_list = sorted_list[:self.words_num]
        sorted_list = [elem for elem in sorted_list if elem[1] > self.min_freq]
        return sorted_list

    def preprocess(self, text: str) -> Dict:
        """
        Дает самые часто встречаемые слова в тексте
        :param text: Текст для обработки
        :return: Словарь вида {
            top_words: Сортированный список, как в DictionaryAlgorithm.get_freq
        }
        """
        tokens = self.do_stem(text)
        freq = self.get_freq(tokens)
        return {
            "tokens": tokens,
            "top_words": freq
        }

    def analyze_comparison(self, res1, res2, comp_res, acc):
        return acc

