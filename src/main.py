import logging.config
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
import sys
import traceback

from config.config import Config
from ui import LoginWindow, ExceptionDialog, MainWindow, LoadingWrapper
from api import do_setup
from loading_wrapper import LoadingThread


class App:
    class SetupThread(LoadingThread):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.operation = 'Установка языковых пакетов'

        def run(self):
            do_setup()
            self.loadingDone.emit()

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        logging.config.dictConfig(Config.LOGGING_CONFIG)
        self.log = logging.getLogger('root')

        self.window = None
        self.login = None
        self.log.debug(f'Main thread {QThread.currentThread()}')

    def start(self):
        self.thread = self.SetupThread()
        self.loading = LoadingWrapper(self.thread)
        self.loading.loadingDone.connect(self.showLogin)
        self.loading.start()

        sys.exit(self.app.exec_())

    def showLogin(self):
        if self.window:
            self.window.close()
        self.login = LoginWindow()
        self.login.loginSuccesful.connect(self.showMainWindow)
        self.login.show()

    def showMainWindow(self):
        self.window = MainWindow()
        self.window.actionChangeDB.triggered.connect(self.showLogin)
        self.window.show()

    def onExceptionCaught(self, type_, value, traceback):
        self.exception = ExceptionDialog(type_, value, traceback)
        self.exception.show()


def exceptionHook(type_, value, traceback_):
    app.onExceptionCaught(type_, value, traceback_)
    app.log.error(''.join(
        traceback.format_exception(type_, value, traceback_))
    )


if __name__ == "__main__":
    app = App()
    sys.excepthook = exceptionHook
    app.start()
