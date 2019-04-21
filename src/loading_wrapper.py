from PyQt5.QtCore import QObject, pyqtSignal, QThread


class LoadingThread(QThread):
    updateStatus = pyqtSignal(str)
    updatePercent = pyqtSignal(int)
    loadingDone = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.operation = 'Operation'
        self.i = 0
        self.interval = -1

    def setInterval(self, iter_num):
        self.total = iter_num
        if iter_num <= 100:
            self.interval = 1
        else:
            self.interval = int(iter_num / 100)

    def checkPercent(self, iter_):  # TODO is this optimal?
        if self.interval == 1:
            self.updatePercent.emit(int(iter_ / self.total * 100))
        elif self.interval < 0:
            return
        else:
            self.i += 1
            if self.i == self.interval:
                self.updatePercent.emit(int(iter_ / self.total * 100))
                self.i = 0

    def run(self, *args, **kwargs):
        raise NotImplementedError(f'{self.run} is not implemented')

