from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from ui_compiled.login import Ui_LoginWindow
from api.database import DataBaseConnection


class LoginWindow(QMainWindow, Ui_LoginWindow):
    loginSuccesful = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.exitButton.clicked.connect(self.close)
        self.connectButton.clicked.connect(self.on_connect_button_clicked)

    def on_connect_button_clicked(self):
        uri = self.uriEdit.text()
        login = self.loginEdit.text()
        password = self.passwordEdit.text()
        self.connection = DataBaseConnection(uri, login, password)
        self.loginSuccesful.emit()
        self.close()
