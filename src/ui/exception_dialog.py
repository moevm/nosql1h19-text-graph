from PyQt5.QtWidgets import QDialog
from ui_compiled.exceptiondialog import Ui_ExceptionDialog
import traceback


class ExceptionDialog(QDialog, Ui_ExceptionDialog):
    def __init__(self, type_, value, traceback_, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.typeEdit.setText(str(type_))
        self.valueEdit.setText(str(value))
        traceback_html = ''.join(traceback.format_tb(traceback_))
        traceback_html = f"<pre>{traceback_html}</pre>"
        self.stackTraceBrowser.setText(traceback_html)
