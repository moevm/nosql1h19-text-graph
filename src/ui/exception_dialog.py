from PyQt5.QtWidgets import QDialog, QMessageBox
from api import TextProcessor
from ui_compiled.exceptiondialog import Ui_ExceptionDialog
import traceback
import sys


__all__ = ['ExceptionDialog']


class ExceptionDialog(QDialog, Ui_ExceptionDialog):
    def __init__(self, type_, value, traceback_, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.typeEdit.setText(str(type_))
        self.valueEdit.setText(str(value))
        traceback_html = ''.join(traceback.format_tb(traceback_))
        traceback_html = f"<pre>{traceback_html}</pre>"
        self.stackTraceBrowser.setText(traceback_html)
        self.clearDbButton.clicked.connect(self.on_clear_db_clicked)
        self.exitButton.clicked.connect(self.on_exit_clicked)

    def on_clear_db_clicked(self):
        proc = TextProcessor()
        proc.clear_db()
        message = "Очистка завершена. Перезапустите приложение"
        self.box = QMessageBox.information(self, "Сообщение", message)

    def on_exit_clicked(self):
        sys.exit(1)
