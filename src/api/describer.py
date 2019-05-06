from neomodel import db
import json

from logger import log
from api.algorithm import AbstractAlgorithm
from api import TextProcessor
from models import TextNode
from ui.misc import get_color_by_weight, get_foreground_color


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

    def _text_to_html(self, text):
        text = text.replace('\n', '<br>')
        return text

    def describe_node(self, node: TextNode):
        html_body = node.describe()
        html_body += f"""
            <h2>Результаты работы алгоритма</h2>
            {self.algorithm.describe_preprocess(node.alg_results)}
        """
        html_body += f"""
            <h2>Текст фрагмента</h2>
            <!-- COLLAPSE текст фрагмента -->
            {self._text_to_html(node.text)}
            <!-- END COLLAPSE -->
        """
        return encapsulate_html(html_body)

    def describe_query_relation(self, rel, id1=None, id2=None):
        if rel is None:
            intersection = 0
        else:
            intersection = rel['intersection']
            rel['data'] = json.loads(rel['data'])
        html_body = f"""
        <h1>Связь</h1>
        <h3>Пересечение: {intersection*100:.2f}% </h3>"""
        if id1 and id2:
            html_body += f"""
            <h3>Фрагменты: {id1} и {id2} </h3>"""
        if rel:
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
        accs = accs if accs is not None else self.processor.accs
        stats = stats if stats is not None else self.processor.stats
        algorithms = self.processor.algorithms
        if accs and len(accs) != len(algorithms):
            log.warning('Результаты в БД не соответствуют настройкам')
            algorithms = self.processor.all_algorithms
        html_body = ""
        if all_algs:
            html_body += "<h1>Общие результаты работы</h1>"
            if stats:
                html_body += f"""
                <h2>Статистика</h2>
                {self._describe_stats(stats)}"""
        if accs:
            if all_algs:
                html_body += """
                <h2>Результаты алгоритмов</h2>"""
                for acc, algorithm in zip(accs, self.processor.all_algorithms):
                    if self.processor.is_algortihm_active(algorithm):
                        html_body += '<p>' \
                            + f'<h3>Алгоритм {algorithm.name}</h3>' \
                            + algorithm.describe_result(acc) + '</p>'
            else:
                html_body += f'<h2>Алгоритм {self.algorithm.name}</h2>'
                acc = accs[self.processor.algorithms.index(self.algorithm)]
                html_body += self.algorithm.describe_result(acc)
        if all_algs:
            html_body = encapsulate_html(html_body)
        return html_body

    def describe_intersection_per_fragment(self):
        query = f"""
        MATCH (n:TextNode)
        OPTIONAL MATCH (n)-[r:ALG]-(n2:TextNode)
        WHERE r.algorithm_name='{self.algorithm.name}'
        WITH avg(r.intersection) as intersection, n as n
        RETURN n.order_id, n.label, CASE intersection WHEN null THEN 0
            ELSE intersection END
        ORDER BY n.order_id
        """
        res, meta = db.cypher_query(query)
        html_body = f"""
            <h2>Среднее пересечение для каждого фрагмента</h2>
            <table border="1" width=100%>
                <thead>
                    <tr>
                        <th>Номер</th>
                        <th>Название</th>
                        <th>Среднее пересечение</th>
                    </th>
                </thead>
        """
        inters = [r[2] for r in res]
        max_inter = max(inters)
        min_inter = min(inters)
        for order_id, label, intersection in res:
            color_weight = (max_inter - intersection) / (max_inter - min_inter)
            bg_color = get_color_by_weight(color_weight)
            fg_color = get_foreground_color(bg_color)
            html_body += f"""
                <tr>
                    <td>{order_id}</td>
                    <td>{label}</td>
                    <td bgcolor='{bg_color.name()}' color='{fg_color.name()}'>
                        {intersection*100:.2f}%
                    </td>
                </tr>
            """
        html_body += f"""
            </table>
        """
        return html_body
