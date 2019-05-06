from PyQt5.QtWidgets import QListWidgetItem


class AbstractReportItem(QListWidgetItem):
    def __init__(self, processor, parent=None):
        """
            Имя должно быть уникальным!
        """
        super().__init__(parent)
        self.processor = processor
        self.name = 'Abstact' if not hasattr(self, 'name') else self.name
        self.setText(self.name)

    def create_html(self):
        # raise NotImplementedError('Not implemented')
        return """ <b> Abstract </b> """
