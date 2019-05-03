from neomodel import JSONProperty, StructuredNode


class GlobalResults(StructuredNode):
    accs = JSONProperty(required=True)  # Результаты анализа связей
    stats = JSONProperty(required=True)  # Результаты анализа вершин
