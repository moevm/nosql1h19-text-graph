from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QListWidgetItem
from ui_compiled.settings_list import Ui_SettingsListDialog


class SettingsListDialog(QDialog, Ui_SettingsListDialog):
    settings_changed = pyqtSignal(list)

    def __init__(self, settings_list, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.type_ = type(settings_list[0]) if len(settings_list) > 0 else str
        [self.listWidget.addItem(str(t)) for t in settings_list]
        self.listWidget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.addButton.clicked.connect(self.on_add_button_clicked)
        self.okButton.clicked.connect(self.on_ok_button_clicked)

    def on_item_double_clicked(self, item: QListWidgetItem):
        self.listWidget.takeItem(self.listWidget.currentRow())

    def on_add_button_clicked(self):
        text = self.settingEdit.text()
        if len(text) > 0:
            self.listWidget.addItem(text)
            self.settingEdit.clear()

    def on_ok_button_clicked(self):
        new_list = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            value = item.text()
            if self.type_ == bool:
                value = value != 'False'
            else:
                value = self.type_(value)
            new_list.append(value)
        self.settings_changed.emit(new_list)
        self.accept()
