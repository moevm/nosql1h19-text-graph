from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QIcon, QPixmap


class AbstractReportItem(QListWidgetItem):
    def __init__(self, processor, parent=None):
        """
            Имя должно быть уникальным!
        """
        super().__init__(parent)
        self.parent = parent
        if hasattr(self, 'settings'):
            icon = QIcon()
            icon.addPixmap(QPixmap(":/icons/cog_wheel.png"), QIcon.Normal)
            self.setIcon(icon)
        self.processor = processor
        self.name = 'Abstact' if not hasattr(self, 'name') else self.name
        self.setText(self.name)

    def change_settings(self):
        from ui import GuiSettingsDialog
        self.dialog = GuiSettingsDialog(self.settings, self.gui_settings,
                                        self.parent)
        self.dialog.settings_set.connect(
            lambda new_settings: setattr(self, 'settings', new_settings))
        self.dialog.setWindowTitle('Параметры элемента отчёта')
        self.dialog.show()

    def create_html(self):
        # raise NotImplementedError('Not implemented')
        return """ <b> Abstract </b> """

from res_compiled import pictures_rc
