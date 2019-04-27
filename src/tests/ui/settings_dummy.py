import setup_

from ui import SettingsDialog
from PyQt5.QtWidgets import QApplication
import sys
from supremeSettings import SupremeSettings


if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = SettingsDialog()
    settings.show()
    settings.accepted.connect(lambda: print(str(SupremeSettings())))
    sys.exit(app.exec_())
