from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QBoxLayout, QCheckBox, \
    QSpacerItem, QSizePolicy
from ui_compiled.settings_list import Ui_SettingsListDialog


class SettingsListDialog(QDialog, Ui_SettingsListDialog):
    settings_changed = pyqtSignal(object)

    def __init__(self, settings_obj, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.source_obj = settings_obj
        if isinstance(settings_obj, list):
            self.type_ = type(settings_obj[0]) if len(settings_obj) > 0 else str
            [self.listWidget.addItem(str(t)) for t in settings_obj]
            self.listWidget.itemDoubleClicked.connect(
                self.on_item_double_clicked)
            self.dictGroupBox.hide()
        elif isinstance(settings_obj, dict):
            self.listGroupBox.hide()
            self.controls = {}
            layout = QBoxLayout(QBoxLayout.TopToBottom)
            for key, value in settings_obj.items():
                control = QCheckBox(key, self)
                layout.addWidget(control)
                control.setChecked(value)
                self.controls[key] = control
            layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding,
                                       QSizePolicy.Expanding))
            self.dictGroupBox.setLayout(layout)

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
        if isinstance(self.source_obj, list):
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
        else:
            new_dict = {}
            for key, control in self.controls.items():
                new_dict[key] = control.isChecked()
            self.settings_changed.emit(new_dict)
        self.accept()
