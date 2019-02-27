from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QLineEdit, QApplication
from ui.login import Ui_LoginWindow


class LoginWindow(QMainWindow, Ui_LoginWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
