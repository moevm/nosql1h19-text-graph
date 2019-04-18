from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QThread, pyqtSignal

from ui_compiled.setup_dialog import Ui_SetupDialog
from api import do_setup


class SetupThread(QThread):
    setupReady = pyqtSignal(int)

    def run(self):
        do_setup()
        self.setupReady.emit(0)


class SetupDialog(QDialog, Ui_SetupDialog):
    setupFinished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def start_setup(self):
        self.thread = SetupThread()
        self.thread.setupReady.connect(self.on_setup_finished)
        self.thread.start()

    def on_setup_finished(self):
        self.done(0)
        self.setupFinished.emit()
