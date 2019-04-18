import logging.config
from PyQt5.QtWidgets import QApplication
import sys
import traceback

from config.config import Config
from ui import SetupDialog, LoginWindow, ExceptionDialog


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        logging.config.dictConfig(Config.LOGGING_CONFIG)
        self.log = logging.getLogger('root')

        self.setup = SetupDialog()
        self.setup.setupFinished.connect(self.onSetupFinished)

    def start(self):
        self.setup.show()
        self.setup.start_setup()
        sys.exit(self.app.exec_())

    def onSetupFinished(self):
        self.log.debug('test')
        self.login = LoginWindow()
        self.login.show()

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
