from api.algorithm import AbstractAlgorithm
from api import TextProcessor
from models import TextNode
import json


def encapsulate_html(body):
    """Метод, оборачивающий тело HTML в остальной код.
    Тут применяются разные стили и т.п.

    :param body: Тело HTML
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    </style>
    </head>
    <body>""" + body + """
    </body>
    </html>
    """


class Describer:
    def __init__(self, algorithm: AbstractAlgorithm, processor: TextProcessor):
        self.algorithm = algorithm
        self.processor = processor

    def describe_node(self, node: TextNode):
        html_body = node.describe()
        html_body += f"""
            <h2>Результаты работы алгоритма</h2>
            {self.algorithm.describe_preprocess(node.alg_results)}
        """
        html_body += f"""
            <h2>Текст фрагмента</h2>
            {node.text}
        """
        return encapsulate_html(html_body)

    def describe_query_relation(self, rel, id1=None, id2=None):
        rel = dict(rel)
        rel['data'] = json.loads(rel['data'])
        html_body = f"""
        <h1>Связь</h1>
        <h3>Пересечение: {rel['intersection']*100:.2f}% </h3>"""
        if id1 and id2:
            html_body += f"""
            <h3>Фрагменты: {id1} и {id2} </h3>"""
        html_body += self.algorithm.describe_comparison(rel)
        return encapsulate_html(html_body)
