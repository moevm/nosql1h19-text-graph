import re
from typing import List, Pattern, Union
from api.exceptions import Error
from models.text_node import TextNode


class SeparatorNotSetException(Error):
    pass


class FragmentWrapper:
    """Класс-обертка для фрагмента. Будет содержать базовые методы
    для работы с одним фрагментом"""
    def __init__(self, text: str, id):
        self.id = id
        self.text = text

    def __str__(self):
        return self.text

    def __eq__(self, obj):
        return str(obj) == self.text

    def __repr__(self):
        return f'<FragmentWrapper: len(text)={len(self.text)}'

    def to_TextNode(self):
        return TextNode(order_id=self.id, text=self.text, short=self.short())

    def short(self):
        res = ''.join([word + ' ' for word in self.text.split(' ')[:5]])
        return res


class FragmentsAnalyzer:
    """Класс, выполняющий разбиение файлов на фрагменты и аггрегирующий
    эти фрагменты.

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
            self.parse_fragments(content)

    def parse_fragments(self, text: str):
        """Разобрать текст на фрагменты по установленному регулярному
        выражению

        :param text:
        :type text: str
        """
        if not self.separator:
            raise SeparatorNotSetException("Separator regex is not set")
        for candidate in re.split(self.separator, text):
            if len(candidate) > 0:
                self._fragments.append(candidate)

    def set_separator(self, separator: Pattern):
        """Установить регулярное выражение, по которому следующий файл
        поделиться на фрагменты

        :param separator: Регулярное выражение
        :type separator: Pattern
        """
        self.separator = separator

    def clear(self):
        """Очистить список фрагментов"""
        self._fragments.clear()

    def _check_item(self, value):
        """Проверяет, является ли value строкой или FragmentWrapper

        :param value: проверяемый объект
        """
        if isinstance(value, str):
            return value
        elif isinstance(value, FragmentWrapper):
            return str(value)
        else:
            raise TypeError(f"Fragment must be string or FragmentWrapper, \
                              not {type(value)}")

    def append(self, value: Union[str, FragmentWrapper]):
        """Доабавить фрагмент

        :param value: фрагмент
        """
        self._fragments.append(self._check_item(value))

    def __setitem__(self, key, value: Union[str, FragmentWrapper]):
        self._fragments[key] = self._check_item(value)

    def __len__(self):
        return len(self._fragments)

    def __getitem__(self, key) -> FragmentWrapper:
        return FragmentWrapper(self._fragments[key], key)

    def __delitem__(self, key):
        del self._fragments[key]

    def __iter__(self):
        return (FragmentWrapper(text, index) for text, index
                in zip(self._fragments, range(len(self._fragments))))
