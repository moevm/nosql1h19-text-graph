import unittest

from api.algorithm import proper_names


class ProperNamesAlgorithmTest(unittest.TestCase):
    algorithm = proper_names.ProperNamesAlgorithm()
    text = """
        Здравствуй, мир. Сергей Сергеич передает минскому генералу Потемкину привет.
        Минск - столица, значит Сергею Сергеичу надо подготовиться.
        Теперь нужно лишь сгонять в США и увидеть Нью-йорк. А потом...
        Потом брат Наполеона Бонапарта заедет к Андрею Болконскому на чай в Московскую область, в Красное Село.
        Андрей шел домой, размышляя о Минске, неидеальной Наташе и полководце Наполеоне
    """

    proper_names_form_text = {'top_proper_names': [
        ('сергей сергеич', 2),
        ('минск', 2),
        (' потемкин', 1),
        ('наполеон бонапарт', 1),
        ('андрей болконский', 1),
        ('андрей', 1),
        ('наташа', 1),
        ('сша', 1),
        ('йорк', 1),
        ('московская область', 1),
        ('красное', 1)
    ]}

    proper_html = "<p>2 - сергей сергеич</p>" \
                  "<p>2 - минск</p><p>1 -  потемкин</p>" \
                  "<p>1 - наполеон бонапарт</p>" \
                  "<p>1 - андрей болконский</p>" \
                  "<p>1 - андрей</p><p>1 - наташа</p>" \
                  "<p>1 - сша</p>" \
                  "<p>1 - йорк</p>" \
                  "<p>1 - московская область</p>" \
                  "<p>1 - красное</p>" \
                  "</div>"

    dict1 = {
        'Hello': 1,
        'world': 2,
        'test': 3
    }

    dict2 = {
        'NotHello': 2,
        'Hello': 2,
        'NotTest': 2
    }

    res_dict = {
        'Hello': 3,
        'test': 3,
        'world': 2,
        'NotHello': 2,
        'NotTest': 2
    }

    def test_summarize_data(self):
        self.assertEqual(self.res_dict, proper_names.sumarize_data(self.dict1, self.dict2))

    def test_preprocess(self):
        self.assertEqual(self.algorithm.preprocess(self.text), self.proper_names_form_text)

    def test_html_extract(self):
        self.assertEqual(self.proper_html, self.algorithm.extract_html(self.proper_names_form_text["top_proper_names"]))

    def test_preprocess_describe(self):
        self.assertEqual("<div>" + self.proper_html, self.algorithm.describe_preprocess(self.algorithm.preprocess(self.text)))
