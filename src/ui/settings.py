from PyQt5.QtWidgets import QDialog, QLineEdit, QSpinBox, QDoubleSpinBox, \
        QCheckBox, QBoxLayout, QLabel, QGroupBox
from ui_compiled.settings import Ui_SettingsDialog
from supremeSettings import SupremeSettings


class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.max_ = 1000
        self.min_ = 0

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
        layout.addWidget(control)
        return control, layout

    def add_settings(self):
        for box_title, settings in self.settings.settings_gui.items():
            box = QGroupBox(box_title, self)
            box_layout = QBoxLayout(QBoxLayout.TopToBottom)
            for name, text in settings.items():
                control, layout = self.get_setting_control(name, text)
                box_layout.addLayout(layout)
                self.controls[name] = control
            box.setLayout(box_layout)
            self.settingsLayout.addWidget(box)

    def on_ok_clicked(self):
        for name, widget in self.controls.items():
            prev_value = self.settings[name]
            if isinstance(prev_value, bool):
                new_value = widget.isChecked()
            elif isinstance(prev_value, str):
                new_value = widget.text()
            else:
                new_value = widget.value()
            new_value = type(prev_value)(new_value)
            self.settings[name] = new_value
        self.accept()
