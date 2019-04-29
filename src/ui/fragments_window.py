from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeyEvent
import re
from os import listdir
from os.path import isfile, join

from ui_compiled.fragments import Ui_FragmentsWindow
from api import TextProcessor
from .loading_dialog import LoadingWrapper
from loading_wrapper import LoadingThread
from ui.widgets import FragmentsList
from models import TextNode


class FragmentsWindow(QMainWindow, Ui_FragmentsWindow):
    # TODO Пересмотреть структуру, чтобы можно было вывести прогресс
    # FIXME Мб треды перетащить в TextProcessor всё же?
    class AddFragmentsThread(LoadingThread):
        def __init__(self, proc, file_name, regex, parent=None):
            super().__init__(parent)
            self.operation = 'Добавление фрагментов'
            self.proc = proc
            self.args = [file_name, regex]

        def run(self):
            self.proc.parse_file(*self.args)
            self.loadingDone.emit()

    class AddFragmentsFolderThread(LoadingThread):
        def __init__(self, proc, folder, regex, parent=None):
            super().__init__(parent)
            self.operation = 'Добавление фрагметов из файла'
            self.proc = proc
            self.folder = folder
            self.regex = regex

        def run(self):
            if not self.regex:
                def get_name(filename, i): return filename
            else:
                def get_name(filename, i): return f"{filename}_{i}"

            files = [f for f in listdir(self.folder)
                     if isfile(join(self.folder, f))]
            self.set_interval(len(files))
            for i, file_name in enumerate(files):
                def get_name_local(index): return get_name(file_name, index)
                file_path = join(self.folder, file_name)
                self.proc.parse_file(file_path, self.regex,
                                     get_name=get_name_local, upload=False)
                self.check_percent(i)
            self.updateStatus.emit('Загрузка в БД')
            self.proc.upload_db()
            self.loadingDone.emit()

    # TODO То же самое
    class ClearFragmentsThread(LoadingThread):
        def __init__(self, proc, parent=None):
            super().__init__(parent)
            self.operation = 'Удаление фрагментов'
            self.proc = proc

        def run(self):
            self.proc.clear_db()
            self.loadingDone.emit()

    fragmentsChanged = pyqtSignal()

    def __init__(self, processor: TextProcessor, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.processor = processor
        self.fragments_list = FragmentsList(self)
        self.fragmentsChanged.connect(self.fragments_list.update)
        self.fragmentsChanged.connect(lambda:
                                      self.fragmentsNumberLabel.setText(
                                          str(len(self.processor.analyzer))
                                          ))

        self.regex = ''
        self.file_name = ''
        self.uploadOnClose = False
        self.folder = False
        self.fragment = None

        self.fragments_list.fragmentItemActivated.connect(
            self.on_fragments_item_changed)
        self.enterSpinBox.valueChanged.connect(
            lambda enters:
            self.sepRegExEdit.setText('\\n{' + str(enters) + '}')
        )
        self.entersRadioButton.clicked.connect(
            self.enterSpinBox.valueChanged.emit
        )
        self.openFileButton.clicked.connect(self.on_file_open)
        self.openFolderButton.clicked.connect(self.on_folder_open)
        self.addFragmentButton.clicked.connect(self.on_add_fragments)
        self.renameButton.clicked.connect(self.on_rename_fragment)
        self.fragmentLabelEdit.returnPressed.connect(self.on_rename_fragment)
        self.dontSeparateRadioButton.clicked.connect(
            lambda: self.sepRegExEdit.setText('.*')
        )
        self.removeAllFragmentsButton.clicked.connect(
            self.on_clear_fragments
        )
        self.removeSelectedFragmentButton.clicked.connect(
            self.on_remove_selected
        )

        self.fragmentsWidgetLayout.addWidget(self.fragments_list)
        self.okButton.clicked.connect(self.close)
        self.fragments_list.update()

    def on_fragments_item_changed(self, node: TextNode):
        self.fragment = node
        self.fragmentLabelEdit.setText(node.label)
        self.fragmentTextBrowser.setText(node.text)
        self.wordNumberLabel.setText(str(node.words_num()))
        self.sentencesNumberLabel.setText(str(node.sentences_num()))
        self.symbolsNumberLabel.setText(str(node.character_num()))
        self.tabWidget.setCurrentIndex(1)

    def on_rename_fragment(self):
        new_name = self.fragmentLabelEdit.text()
        if self.fragment:
            self.uploadOnClose = True
            self.fragment.label = new_name
            self.fragment.save()
            self.fragments_list.update()

    def drop_fragment_info(self):
        self.fragment = None
        self.fragmentLabelEdit.clear()
        self.fragmentTextBrowser.clear()
        self.wordNumberLabel.setText('0')
        self.sentencesNumberLabel.setText('0')
        self.symbolsNumberLabel.setText('0')

    def on_file_open(self):
        self.file_name, filter = \
                QFileDialog.getOpenFileName(self, 'Открыть файл', '.')
        self.fileNameEdit.setText(self.file_name if self.file_name else
                                  'Файл не загружен')
        self.folder = False

    def on_folder_open(self):
        self.file_name = QFileDialog.getExistingDirectory(self,
                                                          'Открыть папку')
        self.fileNameEdit.setText(self.file_name if self.file_name else
                                  'Файл не загружен')
        self.folder = True

    def on_add_fragments(self):
        regex = re.compile(self.sepRegExEdit.text()) \
                if self.sepRegExEdit.text() != '.*' else None
        if len(self.file_name) > 0:
            if not self.folder:
                self.thread = self.AddFragmentsThread(self.processor,
                                                      self.file_name, regex)
            else:
                self.thread = self.AddFragmentsFolderThread(self.processor,
                                                            self.file_name,
                                                            regex)
            self.loading = LoadingWrapper(self.thread)
            self.loading.loadingDone.connect(self.fragments_list.update)
            self.loading.start()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Файл не выбран',
                                QMessageBox.Ok)

    def on_clear_fragments(self):
        self.thread = self.ClearFragmentsThread(self.processor)
        self.loading = LoadingWrapper(self.thread)
        self.loading.loadingDone.connect(self.fragments_list.update)
        self.loading.loadingDone.connect(self.drop_fragment_info)
        self.loading.start()

    def on_remove_selected(self):
        for item in self.fragments_list.selectedItems():
            if item == self.fragment:
                self.drop_fragment_info()
            node = item.node
            node.delete()
        self.uploadOnClose = True
        self.fragments_list.update()

    def closeEvent(self, event):
        if self.uploadOnClose:
            self.thread = self.processor.analyzer.UploadDBThread(
                self.processor.analyzer, download_first=True)
            self.loading = LoadingWrapper(self.thread)
            self.loading.loadingDone.connect(self.fragmentsChanged.emit)
            self.loading.loadingDone.connect(
                lambda: QMainWindow.closeEvent(self, event))
            self.loading.start()
        else:
            self.fragmentsChanged.emit()
            super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)
