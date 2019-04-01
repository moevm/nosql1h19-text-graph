import re
from typing import List, Pattern
from api.exceptions import Error


class SeparatorNotSetException(Error):
    pass


class TextAnalyzer:
    """Класс, выполняющий разбиение файлов на фрагменты"""

    def __init__(self):
        self.separator = None
        self.fragments: List[str] = []

    def read_file(self, filename: str):
        """Считать фрагменты из файла

        :param filename: Имя файла
        :type filename: str
        :exception SeparatorNotSetException: Если регулярное выражение для
        разделения не установлено
        """
        with open(filename, 'r') as file:
            content = file.read()
            self.parse_fragments(content)

    def parse_fragments(self, text: str):
        """Разобрать текст на фрагменты по установленному регулярному
        выражению

        :param text:
        :type text: str
        """
        if not self.separator:
            raise SeparatorNotSetException("Separator regex is not set")
        self.add_fragments(re.split(self.separator, text))

    def set_separator(self, separator: Pattern):
        """Установить регулярное выражение, по которому следующий файл
        поделиться на фрагменты

        :param separator: Регулярное выражение
        :type separator: Pattern
        """
        self.separator = separator
