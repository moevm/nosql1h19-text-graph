import logging.config
from PyQt5.QtWidgets import QApplication
import sys
import traceback

from config.config import Config
from ui import LoadingDialog, LoginWindow, ExceptionDialog, MainWindow
from api import do_setup


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        logging.config.dictConfig(Config.LOGGING_CONFIG)
        self.log = logging.getLogger('root')

        self.setup = LoadingDialog('Идет загрузка языковых пакетов', do_setup)
        self.setup.loadingFinished.connect(self.showLogin)

        self.window = None
        self.login = None

    def start(self):
        self.setup.start()
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
