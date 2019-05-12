from neomodel import JSONProperty, StructuredNode


__all__ = ['GlobalResults']


class GlobalResults(StructuredNode):
    accs = JSONProperty(required=True)  # Результаты анализа связей
    stats = JSONProperty(required=True)  # Результаты анализа вершин
    algs = JSONProperty(required=True)  # Включенные алгоритмы
