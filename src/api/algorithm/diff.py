from .abstract import AbstractAlgorithm
import diff_match_patch as dmp_module
from supremeSettings import SupremeSettings


__all__ = ['DiffAlgorithm']


class DiffAlgorithm(AbstractAlgorithm):
    def __init__(self):
        self.dmp = dmp_module.diff_match_patch()
        self.settings = SupremeSettings()

    def preprocess(self, text):
        return {
            "text": text
        }

    def compare(self, res1, res2):
        text1, text2 = res1['text'], res2['text']
        if self.settings['diff_lines']:
            diff, intersection = self.compare_texts_lines(text1, text2)
        else:
            diff, intersection = self.compare_texts(text1, text2)
        return {
            "intersection": intersection,
            "data": diff
        }

    def calculate_intersection(self, diffs):
        common_len = 0
        text_1_len = 0
        text_2_len = 0
        for delta, word in diffs:
            if delta == 0:
                common_len += len(word)
            elif delta < 0:
                text_1_len += len(word)
            else:
                text_2_len += len(word)
        return common_len / (common_len + text_1_len + text_2_len)

    def compare_texts(self, text1, text2):
        diff = self.dmp.diff_main(text1, text2)
        intersection = self.calculate_intersection(diff)
        return diff, intersection

    def compare_texts_lines(self, text1, text2):
        l1, l2, lines = self.dmp.diff_linesToChars(text1, text2)
        diff = self.dmp.diff_main(l1, l2)
        self.dmp.diff_charsToLines(diff, lines)
        intersection = self.calculate_intersection(diff)
        return diff, intersection

    @property
    def name(self):
        return "Diff"

    @property
    def preprocess_keys(self):
        return ['text']

    def describe_comparison(self, comp_dict):
        html = self.dmp.diff_prettyHtml(comp_dict['data'])
        html = html.replace('#ffe6e6', '#ff1a1a')
        html = html.replace('#e6ffe6', '#33ff33')
        return f"""
        <!-- COLLAPSE Сравнение текстов -->
            {html}
        <!-- END COLLAPSE -->
        """

    def describe_preprocess(self, prep_dict):
        return ""
