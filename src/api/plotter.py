from matplotlib import pyplot as plt, colors
import networkx as nx
from PyQt5.QtGui import QColor
import numpy as np
from io import BytesIO
import base64
from neomodel import db


class Plotter:
    def __init__(self, processor, algorithm=None):
        self.processor = processor
        self.algorithm = algorithm

    def algorithm_matrix(self, min_val=0):
        matrix, head = self.processor.get_matrix(self.algorithm.name,
                                                 sort=True)
        head = self.processor.get_node_label_list(head)
        return Plotter.save_to_matrix(matrix, head, min_val)

    def fragments_length_plot(self):
        text_lens = [len(node.text) for node in self.processor.analyzer]
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.set_title('Распределение длин фрагментов')
        ax.hist(text_lens)
        ax.set_ylabel('Количество фрагментов')
        ax.set_xlabel('Длина фрагмента')
        return fig

    def intersection_plot(self):
        query = f"""
            MATCH (:TextNode)-[r:ALG]-(:TextNode)
            WHERE r.algorithm_name = '{self.algorithm.name}'
                AND r.intersection > 0
            RETURN r.intersection
            ORDER BY r.intersection
        """
        res, meta = db.cypher_query(query)
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.set_title(
            f'Распределение пересечений для алгоритма {self.algorithm.name}')
        ax.hist([r[0] for r in res])
        ax.set_ylabel('Количество')
        ax.set_xlabel('Пересечение')
        return fig

    @staticmethod
    def _get_cmap(min_val):
        """Получение matplotlib'овской Colormap для заданного
        минимального значения

        :param min_val:
        """
        assert 0 <= min_val <= 1
        cdict = {
            'red': [
                (0.0, 0.6, 0.6),
                (min_val, 0.6, 1.0),
                (1.0, 0.0, 0.0)
            ],
            'green': [
                (0.0, 0.6, 0.6),
                (min_val, 0.6, 0.0),
                (1.0, 1.0, 1.0)
            ],
            'blue': [
                (0.0, 0.6, 0.6),
                (min_val, 0.6, 0.0),
                (1.0, 0.0, 0.0)
            ]
        }
        cmap = colors.LinearSegmentedColormap('rg', cdict, N=256)
        return cmap

    @staticmethod
    def save_to_matrix(matrix, head, min_val=0):
        cmap = Plotter._get_cmap(min_val)

        # TODO Адаптивный размер
        fig, ax = plt.subplots(figsize=(10, 10))
        # if not isinstance(matrix, list):
        #    matrix = list(matrix)
        ax.matshow(matrix, cmap=cmap)

        ax.set_xticks(range(len(head)))
        ax.set_yticks(range(len(head)))
        ax.set_xticklabels(head, rotation=90)
        ax.set_yticklabels(head)

        for i in range(len(matrix)):
            for j in range(len(matrix)):
                text = f"{int(matrix[i][j] * 100)}%"
                ax.text(j, i, text, ha="center", va="center",
                        color="k", fontsize=8)

        return fig

    @staticmethod
    def save_to_graph(graph):
        graph.calculate_matrix()
        matrix = np.array(graph.matrix)
        G = nx.from_numpy_matrix(matrix)  # Перевести в NetworkX граф

        # Параметры вершин
        pos, labels = {}, {}
        node_colors = []
        for i, position in enumerate(graph.positions):
            pos[i] = position[0], -position[1]
            node = graph.nodes[graph.head.index(i)]
            labels[i] = node.label
            node_colors.append(node.color.name(QColor.HexRgb))

        # Параметры связей
        edge_labels = {}
        edge_colors = []
        for a, b in G.edges():
            try:
                edge = graph._edges[(a, b)]
            except KeyError:
                edge = graph._edges[(b, a)]
            edge_colors.append(edge.get_color().name(QColor.HexRgb))
            edge_labels[(a, b)] = f"{int(edge.weight*100)}%"

        # Рисование
        # TODO Адаптивный размер шрифта
        fig, ax = plt.subplots(figsize=(8, 8))
        nx.draw_networkx(G, pos=pos, ax=ax, labels=labels,
                         node_color=node_colors, edge_color=edge_colors,
                         node_size=600, font_size=7, width=2.0)
        nx.draw_networkx_edge_labels(G, pos=pos, ax=ax, font_size=6,
                                     edge_labels=edge_labels)
        return fig

    @staticmethod
    def fig_to_base64(fig, close=True):
        figfile = BytesIO()
        fig.savefig(figfile, format='png', bbox_inches='tight')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue())
        if close:
            plt.close(fig)
        return figdata_png.decode('utf8')

    @staticmethod
    def fig_to_base64_tag(*args, **kwargs):
        return '<img src="data:image/jpeg;base64,' \
            + Plotter.fig_to_base64(*args, **kwargs) + '" />'

    @staticmethod
    def display(fig):
        plt.show()
