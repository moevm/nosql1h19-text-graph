from typing import Dict

from api.algorithm import AbstractAlgorithm
from natasha import NamesExtractor, LocationExtractor


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

    @property
    def name(self):
        return 'Proper names'

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

    def compare_results(self, top1: Dict, top2: Dict, select_words=5):
        # TODO То же сравнение, что и в dictionary
        return 0, []

    def preprocess(self, text: str) -> Dict:
        self.nameMatches = self.nameExtractor(text)
        self.locationMatches = self.locationExtractor(text)

        result = self.make_dict()
        sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True)

        return {'top_proper_names': sorted_result}

    def compare(self, res1: Dict, res2: Dict, *args, **kwargs):
        intersection, top_proper_names = self.compare_results(
            res1["top_proper_names"], res2["top_proper_names"],
            *args, **kwargs
        )
        return {
            "intersection": intersection,
            "data": {
                "top_proper_names": top_proper_names
            }
        }

    def describe_result(self) -> str:
        pass

    def describe_comparison(self, comp_dict) -> str:
        data = comp_dict["top_proper_names"]
        result = "<div>" + self.extract_html(data)

        return result

    def extract_html(self, data):
        result = ""
        for item in data:
            result += "<p>" + item[1] + " - " + item[0] + "</p>"
        result += "</div>"
        return result

    def describe_preprocess(self, prep_dict) -> str:
        data = prep_dict["top_proper_names"]
        result = "<div>" + self.extract_html(data)

        return result