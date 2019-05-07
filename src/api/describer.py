import json
import pandas as pd
from functools import reduce

from logger import log
from api.algorithm import AbstractAlgorithm
from api import TextProcessor
from models import TextNode


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

    def describe_centrality_results(self, results):
        from ui.misc import get_color_by_weight, get_foreground_color

        def reduce_func(a, b):
            return a.merge(b, on=['order_id', 'label'])

        dfs = []
        for name, res in results.items():
            df = pd.DataFrame(res)
            df.columns = 'order_id', 'label', name
            dfs.append(df)
        df = reduce(reduce_func, dfs)
        df = df.set_index('order_id')

        html_body = f"""
            <h2>Алгоритмы центральности</h2>
            <table border="1" width=100%>
                <thead>
                    <tr>
                        <th>Номер</th>
                        <th>Название</th>
        """
        weights = []
        for name in df.columns[1:]:
            html_body += f"<th>{name}</th>"
            weights.append((max(df[name]), min(df[name])))
        html_body += """
                    </tr>
                </thead>"""
        for row in df.itertuples():
            html_body += "<tr>"
            for elem in row[:2]:
                html_body += f"<td>{elem}</td>"
            for elem, weight in zip(row[2:], weights):
                max_, min_ = weight
                color_weight = (max_ - elem) / (max_ - min_)
                bg_color = get_color_by_weight(color_weight)
                fg_color = get_foreground_color(bg_color)
                html_body += f"""
                    <td bgcolor={bg_color.name()} color={fg_color.name()}>
                        {elem}
                    </td>
                """
            html_body += "</tr>"
        html_body += "</table>"
        return html_body
