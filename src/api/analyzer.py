import re
from typing import List, Pattern
from .exceptions import Error
from models import TextNode


class SeparatorNotSetException(Error):
    pass


class FragmentsAnalyzer:
    """Класс, выполняющий разбиение файлов на фрагменты и аггрегирующий
    эти фрагменты (т.е. ссылки на модели neomodel).
    Дает интерфейс контейнера для фрагментов.
    """

    def __init__(self):
        self.separator = None
        self._fragments: List[str] = []

    def read_file(self, filename: str):
        """Считать фрагменты из файла

        :param filename: Имя файла
        :type filename: str
        :exception SeparatorNotSetException: Если регулярное выражение для
        разделения не установлено
        """
        with open(filename, 'r') as file:
            content = file.read()
            self._parse_fragments(content)

    def _parse_fragments(self, text: str):
        """Разобрать текст на фрагменты по установленному регулярному
        выражению

        :param text:
        :type text: str
        """
        if not self.separator:
            raise SeparatorNotSetException("Separator regex is not set")
        for candidate in re.split(self.separator, text):
            if len(candidate) > 0:
                self.append(candidate)

    def set_separator(self, separator: Pattern):
        """Установить регулярное выражение, по которому следующий файл
        поделиться на фрагменты

        :param separator: Регулярное выражение
        :type separator: Pattern
        """
        self.separator = separator

    def clear(self):
        """Очистить список фрагментов и БД"""
        [node.delete() for node in TextNode.nodes.all()]
        self._fragments.clear()

    def append(self, value: str):
        """Добавить фрагмент

        :param value: фрагмент
        """
        node = TextNode(text=value)
        self._fragments.append(node)
        node.order_id = len(self._fragments)-1

    def update_order_id(self):
        for index, node in zip(range(len(self._fragments)), self._fragments):
            node.order_id = index

    def upload_db(self):
        """Загрузить фрагменты в БД"""
        self.update_order_id()
        [node.save() for node in self._fragments]

    def download_db(self):
        """Скачать фрагменты из БД"""
        self._fragments = TextNode.nodes.all()
        self._fragments.sort(key=lambda node: node.order_id)

    def __len__(self):
        return len(self._fragments)

    def __getitem__(self, order_id: int):
        return self._fragments[order_id]

    def __delitem__(self, order_id):
        del self._fragments[order_id]

    def __iter__(self):
        return (node for node in self._fragments)
