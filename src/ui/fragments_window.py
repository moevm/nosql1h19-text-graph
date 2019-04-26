from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal
from ui_compiled.fragments import Ui_FragmentsWindow
from api import TextProcessor
from .loading_dialog import LoadingWrapper
from ui.widgets import FragmentsList
from models import TextNode
import re
from loading_wrapper import LoadingThread


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
        self.addFragmentButton.clicked.connect(self.on_add_fragments)
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
        self.fragmentTextBrowser.setText(node.text)
        self.wordNumberLabel.setText(str(node.words_num()))
        self.sentencesNumberLabel.setText(str(node.sentences_num()))
        self.symbolsNumberLabel.setText(str(node.character_num()))
        self.tabWidget.setCurrentIndex(1)

    def on_file_open(self):
        self.file_name, filter = \
                QFileDialog.getOpenFileName(self, 'Открыть файл', '.')
        self.fileNameEdit.setText(self.file_name if self.file_name else
                                  'Файл не загружен')

    def on_add_fragments(self):
        regex = re.compile(self.sepRegExEdit.text()) \
                if self.sepRegExEdit.text() != '.*' else None
        if len(self.file_name) > 0:
            self.thread = self.AddFragmentsThread(self.processor,
                                                  self.file_name, regex)
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
        self.loading.start()

    def on_remove_selected(self):
        for item in self.fragments_list.selectedItems():
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
