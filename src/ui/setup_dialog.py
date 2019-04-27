from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QThread, pyqtSignal

from ui_compiled.setup_dialog import Ui_SetupDialog


class LoadingThread(QThread):
    actionReady = pyqtSignal(int)

    def __init__(self, action, parent=None, *args, **kwargs):
        super().__init__(parent)
        self.action = action
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.action(*self.args, **self.kwargs)
        self.actionReady.emit(0)
