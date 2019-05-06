import copy

from abc import ABC, abstractmethod, abstractproperty
from typing import Dict, Tuple, Any, List
from nltk.corpus import stopwords
from pymystem3 import Mystem

from api.algorithm import AbstractAlgorithm
from supremeSettings import SupremeSettings


class NotSoAbstractAlgorithm(AbstractAlgorithm):

    def __init__(self):

        settings = SupremeSettings()
        self.words_num = settings['dictionary_words_num']
        self.word_regex = r'[а-яА-Я]'
        self.min_freq = settings['dictionary_min_words']

        if self.name == 'Dictionary':
            self.dictParam = 'top_words'

            self.stem = Mystem()
            self.stopwords = stopwords.words('russian') \
                             + settings['dictionary_exclude_list']
        else:
            self.dictParam = 'top_proper_names'

    @abstractmethod
    def preprocess(self, text: str) -> Dict:
        pass

    def compare_results(self, top1, top2):
        def compare_numbers(a, b):
            return 1 - abs(b - a) / max(b, a) if max(b, a) > 0 else 1.0

        def mean(a, b):
            return (a + b) / 2

        res = []

        if len(top1) == 0 or len(top2) == 0:
            return 0, []

        used_indexes_2 = [False for _ in range(len(top2))]
        for index1, elem1, freq1 in zip(range(len(top1)), *zip(*top1)):
            for index2, elem2, freq2 in zip(range(len(top2)), *zip(*top2)):
                if elem1 == elem2:
                    res.append(
                        (compare_numbers(
                            freq1, freq2), mean(
                            freq1, freq2), elem1))
                    used_indexes_2[index2] = True
                    break
            else:
                res.append((0, mean(freq1, 0), elem1))
        for i, used, elem2, freq2 in zip(
                range(len(used_indexes_2)),
                used_indexes_2, *zip(*top2)):
            if not used:
                res.append((0, mean(freq2, 0), elem2))

        res = sorted(res, key=lambda e: e[0] * e[1], reverse=True)

        avg_weight = sum([res_elem[1] for res_elem in res]) / len(res)
        avg = 0
        for comp, weight, elem in res:
            avg += comp * weight / avg_weight
        avg /= len(res)
        words = [res_elem for res_elem in res if res_elem[0] > 0]

        return avg, words[:self.words_num]

    def compare(self, res1: Dict, res2: Dict) -> Dict:
        intersection, top_words = self.compare_results(
            res1[f"{self.dictParam}"], res2[f"{self.dictParam}"],
            *args, **kwargs # TODO Что тут не так?
        )
        return {
            "intersection": intersection,
            "data": {
                "top_proper_names": top_words
            }
        }
        pass

    @abstractproperty
    def name(self) -> str:
        pass

    @abstractproperty
    def preprocess_keys(self) -> list:
        pass

    def analyze(self, res: Dict, acc=None):
        def add_freq_lists(list1, list2):
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
                f'{self.dictParam}': []
            }
        acc[f'{self.dictParam}'] = add_freq_lists(acc[f'{self.dictParam}'], res[f'{self.dictParam}'])
        return acc

    def analyze_comparison(self, res1, res2, comp_res, acc):
        return acc

    def describe_result(self, acc) -> str:
        acc[f'{self.dictParam}'].sort(key=lambda el: el[1], reverse=True)
        html_body = f"""
                            <!-- COLLAPSE Таблица слов -->
                            <table border="1" width="100%">
                                <caption>
                                    Наиболее часто встречающиеся слова во фрагментах
                                    [топ-{self.words_num}]
                                </caption>
                                <thead>
                                    <tr>
                                        <th>Слово</th>
                                        <th>Количество</th>
                                    </tr>
                                </thead>"""
        acc[f'{self.dictParam}'] = acc[f'{self.dictParam}'][:self.words_num]
        for word, freq in acc[f'{self.dictParam}']:
            html_body += f"""
                                <tr>
                                    <td>{word}</td>
                                    <td>{freq}</td>
                                </tr>"""
        html_body += """
                            </table>
                            <!-- END COLLAPSE -->"""
        return html_body

    def describe_comparison(self, comp_dict) -> str:
        text = f"""
                        <!-- COLLAPSE Таблица слов -->
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
        for inter, freq, word in comp_dict['data'][f'{self.dictParam}']:
            text += f"""
                            <tr>
                                <td>{word}</td>
                                <td>{inter:.2f}</td>
                                <td>{int(freq)}</td>
                            </tr>"""
        text += """
                        <!-- END COLLAPSE -->
                        </table>"""
        return text

    def describe_preprocess(self, prep_dict) -> str:
        text = ""
        if prep_dict is None or f'{self.dictParam}' not in prep_dict:
            text += "Результатов нет"
            return text
        text += """
                        <!-- COLLAPSE Таблица слов -->
                            <table border="1" width=100%>
                                <caption>Наиболее часто встречающиеся имена собственные:</caption>
                                <thead>
                                    <tr>
                                        <th>Слово</th>
                                        <th>Частота</th>
                                    </tr>
                                </thead>"""
        for word, freq in prep_dict[f'{self.dictParam}']:
            text += f"""
                                <tr>
                                    <td>{word}</td>
                                    <td>{freq}</td>
                                </tr>"""
        text += """
                            </table>
                        <!-- END COLLAPSE -->"""
        return text
