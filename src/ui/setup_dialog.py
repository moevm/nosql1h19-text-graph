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


class LoadingDialog(QDialog, Ui_SetupDialog):
    loadingFinished = pyqtSignal()

    def __init__(self, label, action, parent=None):
        """Обертка для выполнения тяжеловесных действий в отдельном потоке.
        Из-за GIL нет выигрыша в производительности, но UI не зависает.
        TODO исправить отсутствие подключения к neo4j в отдельном потоке"""
        super().__init__(parent)
        self.setupUi(self)
        self.action = action
        self.label.setText(label)

    def start(self, *args, **kwargs):
        self.show()
        self.thread = LoadingThread(self.action, self, *args, **kwargs)
        self.thread.actionReady.connect(self.on_setup_finished)
        self.thread.start()

    def on_setup_finished(self):
        self.done(0)
        self.loadingFinished.emit()
