import logging.config
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
import sys
import traceback
import tempfile

from config.config import Config
from ui import LoginWindow, ExceptionDialog, MainWindow, LoadingWrapper
from api import do_setup
from loading_wrapper import LoadingThread
from supremeSettings import SupremeSettings


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
        self.settings = SupremeSettings()
        self.settings.check_settings()
        logging.config.dictConfig(Config.LOGGING_CONFIG)
        self.log = logging.getLogger('root')

        self.tempdir = tempfile.TemporaryDirectory()
        self.log.debug(f'Temporary Directory is {self.tempdir}')
        self.settings['tempdir'] = self.tempdir.name

        self.window = None
        self.login = None
        self.log.debug(f'Main thread {QThread.currentThread()}')

    def start(self):
        if self.settings['setup']:
            self.thread = self.SetupThread()
            self.loading = LoadingWrapper(self.thread)
            self.loading.loadingDone.connect(self.show_login)
            self.loading.start()
        else:
            self.show_login()

        exit_code = self.app.exec_()
        sys.exit(exit_code)

    def show_login(self):
        if self.window:
            self.window.close()
        self.login = LoginWindow()
        self.login.loginSuccesful.connect(self.show_main_window)
        self.login.show()

    def show_main_window(self):
        self.window = MainWindow()
        self.window.actionChangeDB.triggered.connect(self.show_login)
        self.window.show()

    def on_exception_caught(self, type_, value, traceback):
        self.exception = ExceptionDialog(type_, value, traceback)
        self.exception.show()


def exception_hook(type_, value, traceback_):
    app.on_exception_caught(type_, value, traceback_)
    app.log.error(''.join(
        traceback.format_exception(type_, value, traceback_))
    )


if __name__ == "__main__":
    app = App()
    sys.excepthook = exception_hook
    app.start()
