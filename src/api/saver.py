from matplotlib import pyplot as plt, colors
import networkx as nx
from PyQt5.QtGui import QColor
import numpy as np


class Saver:
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
        cmap = Saver._get_cmap(min_val)

        # TODO Адаптивный размер
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.matshow(matrix.tolist(), cmap=cmap)

        ax.set_xticks(range(len(head)))
        ax.set_yticks(range(len(head)))
        ax.set_xticklabels(head, rotation=90)
        ax.set_yticklabels(head)

        for i in range(len(matrix)):
            for j in range(len(matrix)):
                text = f"{int(matrix[i, j] * 100)}%"
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
    def display(fig):
        plt.show()
