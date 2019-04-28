import re
import copy
from typing import Dict, List, Tuple, Any
from nltk.corpus import stopwords
from pymystem3 import Mystem

from api.algorithm import AbstractAlgorithm
from supremeSettings import SupremeSettings

FreqList = List[Tuple[int, Any]]


class DictionaryAlgorithm(AbstractAlgorithm):
    def __init__(self):
        self.stem = Mystem()
        settings = SupremeSettings()
        self.stopwords = stopwords.words('russian') \
            + settings['dictionary_exclude_list']
        self.words_num = settings['dictionary_words_num']
        self.word_regex = r'[а-яА-Я]'
        self.min_freq = settings['dictionary_min_words']

    @property
    def name(self):
        return 'Dictionary'

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

    def compare_results(self, top1: FreqList, top2: FreqList):
        """
        Производит сравнение списов частоты
        :param top1: Результат 1 в виде (частота, элемент)
        :param top2: Результат 2
        :param select_words: Количество элементов для характеристики сравнения
        :return: "Коэффициент похожести" и список из пересечений слов в виде:
            [Пересечение употребления, частота употребления, слово]
        """
        def compare_numbers(a, b):
            return 1 - abs(b - a) / max(b, a) if max(b, a) > 0 else 1.0

        def mean(a, b):
            return (a + b) / 2
        res = []

        if len(top1) == 0 or len(top2) == 0:
            return 0, []

        # Показывает использованные элементы top1
        used_indexes_2 = [False for _ in range(len(top2))]
        for index1, elem1, freq1 in zip(range(len(top1)), *zip(*top1)):
            for index2, elem2, freq2 in zip(range(len(top2)), *zip(*top2)):
                if elem1 == elem2:  # Если элемент есть в обеих списках
                    res.append(
                        (compare_numbers(
                            freq1, freq2), mean(
                            freq1, freq2), elem1))
                    used_indexes_2[index2] = True
                    break
            else:  # Если есть только в первом, но нет во втором
                res.append((0, mean(freq1, 0), elem1))
        for i, used, elem2, freq2 in zip(
                range(len(used_indexes_2)),
                used_indexes_2, *zip(*top2)):
            if not used:  # Есть только во втором, но не в первом
                res.append((0, mean(freq2, 0), elem2))

        # Здесь формат результата:
        # List[(Пересечение употребления, частота употребления, слово)]

        # Элементы сортируются по схожести частот употребления, взвешенных
        # относительно частоты употребления
        res = sorted(res, key=lambda e: e[0] * e[1], reverse=True)

        # Вычисляется средневзвешенное
        avg_weight = sum([res_elem[1] for res_elem in res]) / len(res)
        avg = 0
        for comp, weight, elem in res:
            avg += comp * weight / avg_weight
        avg /= len(res)
        words = [res_elem for res_elem in res if res_elem[0] > 0]

        return avg, words[:self.words_num]

    def compare(self, res1: Dict, res2: Dict, *args, **kwargs):
        """
        Сравнивает результаты работы алгоритма для фрагментов
        :param res1: Результат для фрагмента 1
        :param res2: Результат для фрагмента 2
        :param args, kwargs: Параметры, передающиеся в self.compare_results
        :return: {
            intersection: Численная харакетристика связи от 0 до 1
            data: Прочие характеристики связи {
                top_words: топ-select_words слов пересечения
            }
        }
        """
        intersection, top_words = self.compare_results(
            res1["top_words"], res2["top_words"],
            *args, **kwargs
        )
        return {
            "intersection": intersection,
            "data": {
                "top_words": top_words
            }
        }

    def analyze(self, res: Dict, acc=None):
        def add_freq_lists(list1: FreqList, list2: FreqList):
            total = copy.deepcopy(list1 + list2)
            total.sort(key=lambda el: el[0])
            i = 0
            while i < len(total) - 1:
                if total[i][0] != total[i+1][0]:
                    i += 1
                else:
                    total[i] = total[i][0], total[i][1] + total[i+1][1]
                    del total[i+1]
            return total
        if acc is None:
            acc = {
                'top_words': []
            }
        acc['top_words'] = add_freq_lists(acc['top_words'], res['top_words'])
        return acc

    def analyze_comparison(self, res1, res2, comp_res, acc):  # TODO
        return acc

    def describe_result(self, acc):
        acc['top_words'].sort(key=lambda el: el[1], reverse=True)
        html_body = """
            <h3>Алгоритм сравнения словарей</h3>
            <b>Наиболее часто встречающиеся слова во фрагментах</b>
            <table border="1" width="100%">
                <thead>
                    <tr>
                        <th>Слово</th>
                        <th>Количество</th>
                    </tr>
                </thead>"""
        acc['top_words'] = acc['top_words'][:self.words_num]
        for word, freq in acc['top_words']:
            html_body += f"""
                <tr>
                    <td>{word}</td>
                    <td>{freq}</td>
                </tr>"""
        return html_body

    def describe_preprocess(self, prep_dict):
        text = """
        <h3>Алгоритм сравнения словарей</h3>
        """
        if prep_dict is None or 'top_words' not in prep_dict:
            text += "Результатов нет"
            return text
        text += """
        <table border="1" width=100%>
            <caption>Наиболее часто встречающиеся слова:</caption>
            <thead>
                <tr>
                    <th>Слово</th>
                    <th>Частота</th>
                </tr>
            </thead>"""
        for word, freq in prep_dict['top_words']:
            text += f"""
            <tr>
                <td>{word}</td>
                <td>{freq}</td>
            </tr>"""
        text += """
        </table>"""
        return text

    def describe_comparison(self, comp_dict):
        text = f"""
        <table border="1">
            <caption>
                Наиболее часто встречающиеся слова из пересечения
            </caption>
            <thead>
                <tr>
                    <th>Слово</th>
                    <th>Пересечение</th>
                    <th>Частота</th>
                </tr>
            </thead>"""
        for inter, freq, word in comp_dict['data']['top_words']:
            text += f"""
            <tr>
                <td>{word}</td>
                <td>{inter:.2f}</td>
                <td>{int(freq)}</td>
            </tr>"""
        text += """
        </table>"""
        return text
