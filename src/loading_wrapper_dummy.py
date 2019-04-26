from PyQt5.QtWidgets import QApplication
from loading_wrapper import LoadingThread
from ui import LoadingWrapper
import time
import sys


class DummyThread(LoadingThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.operation = 'Dummy Operation'
        self.set_interval(1000)

    def run(self):
        for i in range(1000):
            self.check_percent(i)
            time.sleep(0.005)
        self.loadingDone.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    thread = DummyThread()
    wrapper = LoadingWrapper(thread)
    wrapper.start()
    sys.exit(app.exec_())
