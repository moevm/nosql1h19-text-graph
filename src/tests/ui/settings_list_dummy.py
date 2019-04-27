import setup_

from ui.widgets import SettingsListDialog
from PyQt5.QtWidgets import QApplication
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_list = ['a', 'b', 'c', 'd']
    # test_list = [True, False, True]
    # test_list = [1, 2, 3]
    dialog = SettingsListDialog(test_list)
    dialog.settings_changed.connect(
        lambda l: print(l))
    dialog.show()
    sys.exit(app.exec_())
