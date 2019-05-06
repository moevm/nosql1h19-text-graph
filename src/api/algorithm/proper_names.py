from typing import Dict

from api.algorithm import AbstractAlgorithm
from natasha import NamesExtractor, LocationExtractor
from supremeSettings import SupremeSettings


def sumarize_data(dict1: Dict, dict2: Dict):
    result = {}

    for key, value in dict1.items():
        if key in result.keys():
            result[key] += value
        else:
            result[key] = value

    for key, value in dict2.items():
        if key in result.keys():
            result[key] += value
        else:
            result[key] = value

    return result


class ProperNamesAlgorithm(AbstractAlgorithm):

    nameExtractor = NamesExtractor()
    locationExtractor = LocationExtractor()

    def __init__(self):
        # self.stem = Mystem()
        settings = SupremeSettings()
        # self.stopwords = stopwords.words('russian') \
        #     + settings['dictionary_exclude_list']
        self.words_num = settings['dictionary_words_num']
        self.word_regex = r'[а-яА-Я]'
        self.min_freq = settings['dictionary_min_words']

    @property
    def name(self):
        return 'Proper names'

    @property
    def preprocess_keys(self):
        return ['tokens', 'top_proper_names']

    def get_loc_data(self):
        result = {}

        for match in self.locationMatches:
            data = match.fact

            if data.name in result.keys():
                result[data.name] += 1
            else:
                result[data.name] = 1

        return result

    def get_names_data(self):
        result = {}

        for match in self.nameMatches:
            string = ""
            data = match.fact

            if data.first is not None:
                string += data.first
            if data.middle is not None:
                string += ' ' + data.middle
            if data.last is not None:
                string += ' ' + data.last
            if data.nick is not None:
                string += ' ' + data.nick

            if string in result.keys():
                result[string] += 1
            else:
                result[string] = 1

        return result

    def make_dict(self):
        names_data = self.get_names_data()
        locations_data = self.get_loc_data()
        result = sumarize_data(names_data, locations_data)

        return result

    def compare_results(self, top1: Dict, top2: Dict):  # TODO Убрать дублирование кода
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

    def preprocess(self, text: str) -> Dict:
        self.nameMatches = self.nameExtractor(text)
        self.locationMatches = self.locationExtractor(text)

        result = self.make_dict()
        sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True)

        return {'top_proper_names': sorted_result}

    def compare(self, res1: Dict, res2: Dict, *args, **kwargs):
        intersection, top_words = self.compare_results(
            res1["top_proper_names"], res2["top_proper_names"],
            *args, **kwargs
        )
        return {
            "intersection": intersection,
            "data": {
                "top_proper_names": top_words
            }
        }
        pass

    def describe_result(self) -> str:
        # TODO Describe_result_proper
        pass

    def describe_comparison(self, comp_dict) -> str:
        data = comp_dict["top_proper_names"]
        result = "<div>" + self.extract_html(data)

        return result

    def extract_html(self, data):
        result = ""
        for item in data:
            result += "<p>" + str(item[1]) + " - " + str(item[0]) + "</p>"
        result += "</div>"
        return result

    def describe_preprocess(self, prep_dict) -> str:
        data = prep_dict["top_proper_names"]
        result = "<div>" + self.extract_html(data)

        return result
