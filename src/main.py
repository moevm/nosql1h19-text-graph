from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QLineEdit, QApplication
from ui.mainwindow import Ui_MainWindow
from helloWorld import HelloWorldExample
from config.config import Config


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.hello = HelloWorldExample(Config.NEO4J_URI, Config.NEO4J_LOGIN, Config.NEO4J_PASSWORD)
        self.helloButton.clicked.connect(self.say_hello)
        self.helloText.setPlainText(self.helloText.toPlainText() + f"\n Connected to {Config.NEO4J_URI}")

    def say_hello(self):
        text, entered = QInputDialog.getText(self.helloText, 'Hello, world', 'Input node name', QLineEdit.Normal)
        if entered:
            greeting = self.hello.print_greeting(text)
            self.helloText.setPlainText(self.helloText.toPlainText() + f"\n {greeting}")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
