import re
from typing import List, Pattern
from models import TextNode
from loading_wrapper import LoadingThread
from logger import log


class FragmentsAnalyzer:
    """Класс, выполняющий разбиение файлов на фрагменты и аггрегирующий
    эти фрагменты (т.е. ссылки на модели neomodel).
    Дает интерфейс контейнера для фрагментов.
    """
    class UploadDBThread(LoadingThread):
        def __init__(self, analyzer, download_first=False, parent=None):
            super().__init__(parent)
            self.analyzer = analyzer
            self.operation = 'Загрузка данных в БД'
            self.set_interval(len(analyzer))
            self.download_first = download_first

        def run(self):
            log.info('Uploading data')
            self.updateStatus.emit('Загрузка')
            if self.download_first:
                self.analyzer.download_db()
            self.updateStatus.emit('Нумерация')
            for i, node in enumerate(self.analyzer):
                self.check_percent(i)
                node.order_id = i
            self.updateStatus.emit('Сохранение')
            for i, node in enumerate(self.analyzer):
                self.check_percent(i)
                node.save()
            self.loadingDone.emit()

    class ClearDBThread(LoadingThread):
        def __init__(self, analyzer, parent=None):
            super().__init__(parent)
            self.analyzer = analyzer
            self.operation = 'Очистка БД'
            self.set_interval(len(analyzer))

        def run(self):
            for i, node in enumerate(TextNode.nodes.all()):
                self.check_percent(i)
                node.delete()
            self.analyzer._fragments.clear()
            self.loadingDone.emit()

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
            self.append(text)
        else:
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
        thread = self.ClearDBThread(self)
        thread.run()
        thread.wait()

    def append(self, value: str):
        """Добавить фрагмент

        :param value: фрагмент
        """
        node = TextNode(text=value)
        self._fragments.append(node)
        node.order_id = len(self._fragments)-1

    def upload_db(self):
        """Загрузить фрагменты в БД"""
        thread = self.UploadDBThread(self)
        thread.run()
        thread.wait()

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
