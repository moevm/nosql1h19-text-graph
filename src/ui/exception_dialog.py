from PyQt5.QtWidgets import QDialog, QMessageBox
from api import TextProcessor
from ui_compiled.exceptiondialog import Ui_ExceptionDialog
import traceback
import sys


class ExceptionDialog(QDialog, Ui_ExceptionDialog):
    def __init__(self, type_, value, traceback_, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.typeEdit.setText(str(type_))
        self.valueEdit.setText(str(value))
        traceback_html = ''.join(traceback.format_tb(traceback_))
        traceback_html = f"<pre>{traceback_html}</pre>"
        self.stackTraceBrowser.setText(traceback_html)
        self.clearDbButton.clicked.connect(self.onClearDbClicked)
        self.exitButton.clicked.connect(self.onExitClicked)

    def onClearDbClicked(self):
        proc = TextProcessor()
        proc.clear_db()
        message = "Очистка завершена. Перезапустите приложение"
        self.box = QMessageBox.information(self, "Сообщение", message)

    def onExitClicked(self):
        sys.exit(1)
