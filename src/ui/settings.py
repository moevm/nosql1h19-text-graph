from PyQt5.QtWidgets import QDialog, QLineEdit, QSpinBox, QDoubleSpinBox, \
        QCheckBox, QBoxLayout, QLabel, QGroupBox, QPushButton
from ui_compiled.settings import Ui_SettingsDialog
from ui.widgets import SettingsListDialog
from supremeSettings import SupremeSettings


class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.max_ = 1000
        self.min_ = 0
        self.list_values = {}

        self.settings = SupremeSettings()
        self.settings.check_settings()
        self.controls = {}
        self.add_settings()
        self.saveButton.clicked.connect(self.on_ok_clicked)

    def get_setting_control(self, name, text):
        value = self.settings[name]
        if isinstance(value, bool):
            layout = QBoxLayout(QBoxLayout.TopToBottom)
            control = QCheckBox(text, self)
            control.setChecked(value)
        elif isinstance(value, str):
            layout = QBoxLayout(QBoxLayout.TopToBottom)
            label = QLabel(text, self)
            control = QLineEdit(value, self)
            layout.addWidget(label)
        elif isinstance(value, int) or isinstance(value, float):
            if isinstance(value, float):
                control = QDoubleSpinBox(self)
            else:
                control = QSpinBox(self)
            control.setRange(self.min_, self.max_)
            control.setValue(value)
            layout = QBoxLayout(QBoxLayout.LeftToRight)
            label = QLabel(text, self)
            layout.addWidget(label)
        elif isinstance(value, list) or isinstance(value, dict):
            self.list_values[name] = value
            control = QPushButton('Изменить список', self)
            control.clicked.connect(lambda: self.on_list_change_clicked(name))
            label = QLabel(text, self)
            layout = QBoxLayout(QBoxLayout.LeftToRight)
            layout.addWidget(label)
        else:
            raise ValueError(f'Не GUI для настройки типа {type(value)} ')
        layout.addWidget(control)
        return control, layout

    def on_list_change_clicked(self, name):
        self.list_dialog = SettingsListDialog(self.list_values[name])
        self.list_dialog.settings_changed.connect(
            lambda l: self.list_values.__setitem__(name, l))
        self.list_dialog.show()

    def add_settings(self):
        main_layout = QBoxLayout(QBoxLayout.TopToBottom)
        for box_title, settings in self.settings.settings_gui.items():
            box = QGroupBox(box_title, self)
            box_layout = QBoxLayout(QBoxLayout.TopToBottom)
            for name, text in settings.items():
                control, layout = self.get_setting_control(name, text)
                box_layout.addLayout(layout)
                self.controls[name] = control
            box.setLayout(box_layout)
            main_layout.addWidget(box)
            if main_layout.count() > 2:
                self.settingsLayout.addItem(main_layout)
                main_layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.settingsLayout.addItem(main_layout)

    def on_ok_clicked(self):
        for name, widget in self.controls.items():
            prev_value = self.settings[name]
            if isinstance(prev_value, bool):
                new_value = widget.isChecked()
            elif isinstance(prev_value, str):
                new_value = widget.text()
            elif isinstance(prev_value, list) or isinstance(prev_value, dict):
                new_value = self.list_values[name]
            else:
                new_value = widget.value()
            new_value = type(prev_value)(new_value)
            self.settings[name] = new_value
        self.accept()
