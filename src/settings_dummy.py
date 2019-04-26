from ui import SettingsDialog
from PyQt5.QtWidgets import QApplication
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = SettingsDialog()
    settings.show()
    sys.exit(app.exec_())
