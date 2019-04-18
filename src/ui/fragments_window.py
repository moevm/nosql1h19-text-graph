from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from ui_compiled.fragments import Ui_FragmentsWindow
from api import TextProcessor
from ui.widgets import FragmentsList
from models import TextNode
import re
from .setup_dialog import LoadingDialog


class FragmentsWindow(QMainWindow, Ui_FragmentsWindow):
    def __init__(self, processor: TextProcessor, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.processor = processor
        self.fragments_list = FragmentsList(self)
        self.regex = ''
        self.file_name = ''

        self.fragments_list.fragmentItemActivated.connect(
            self.onFragmentsItemChanged)
        self.enterSpinBox.valueChanged.connect(
            lambda enters:
            self.sepRegExEdit.setText('\\n{' + str(enters) + '}')
        )
        self.entersRadioButton.clicked.connect(
            self.enterSpinBox.valueChanged.emit
        )
        self.openFileButton.clicked.connect(self.onFileOpen)
        self.addFragmentButton.clicked.connect(self.onAddFragments)
        self.dontSeparateRadioButton.clicked.connect(
            lambda: self.sepRegExEdit.setText('.*')
        )
        self.removeAllFragmentsButton.clicked.connect(
            self.onClearFragments
        )

        self.fragmentsWidgetLayout.addWidget(self.fragments_list)
        self.fragments_list.update()
        self.fragmentsNumberLabel.setText(str(len(self.processor.analyzer)))

    def onFragmentsItemChanged(self, node: TextNode):
        self.fragmentTextBrowser.setText(node.text)
        self.wordNumberLabel.setText(str(node.words_num()))
        self.sentencesNumberLabel.setText(str(node.sentences_num()))
        self.symbolsNumberLabel.setText(str(node.character_num()))

    def onFileOpen(self):
        self.file_name, filter = \
                QFileDialog.getOpenFileName(self, 'Открыть файл', '.')
        self.fileNameEdit.setText(self.file_name if self.file_name else
                                  'Файл не загружен')

    def onAddFragments(self):
        regex = self.sepRegExEdit.text()
        if len(self.file_name) > 0:
            self.loading = LoadingDialog('Идет добавление фрагментов',
                                         self.processor.parse_file)
            self.loading.start(self.file_name, re.compile(regex))
            self.loading.loadingFinished.connect(self.fragments_list.update)
            # self.processor.parse_file(self.file_name, re.compile(regex))
        else:
            QMessageBox.warning(self, 'Ошибка', 'Файл не выбран',
                                QMessageBox.Ok)


    def onClearFragments(self):
            self.loading = LoadingDialog('Идет добавление фрагментов',
                                         self.analyzer.clear)
            self.loading.start()
            self.loading.loadingFinished.connect(self.fragments_list.update)
        self.fragments_list.update()
