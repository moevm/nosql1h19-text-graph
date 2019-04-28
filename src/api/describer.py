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

    def _describe_stats(self, stats):
        return f"""
        <table border="1" width=100%>
            <tr>
                <th>Всего фрагментов</th>
                <td>{stats['frags']}</td>
            </tr>
            <tr>
                <th>Всего предложений</th>
                <td>{stats['sentences']}</td>
            </tr>
            <tr>
                <th>Всего слов</th>
                <td>{stats['words']}
            </tr>
            <tr>
                <th>Всего символов</th>
                <td>{stats['symbols']}</td>
            </tr>
        </table>
        """

    def describe_results(self, accs=None, stats=None, all_algs=False):
        assert accs is None or len(accs) == len(self.processor.algorithms)
        html_body = f"""
        <h1>Общие результаты работы</h1>"""
        if stats:
            html_body += f"""
            <h2>Статистика</h2>
            {self._describe_stats(stats)}"""
        if accs:
            html_body += """
            <h2>Результаты алгоритмов</h2>"""
            if all_algs:
                for acc, algorithm in zip(accs, self.processor.algorithms):
                    html_body += algorithm.describe_result(acc)
            else:
                acc = accs[self.processor.algorithms.index(self.algorithm)]
                html_body += self.algorithm.describe_result(acc)
        return encapsulate_html(html_body)
