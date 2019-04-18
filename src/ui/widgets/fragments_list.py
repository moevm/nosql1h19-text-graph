from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from models import TextNode


class FragmentItem(QListWidgetItem):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node
        self.setText(node.preview())


class FragmentsList(QListWidget):
    fragmentItemActivated = pyqtSignal(TextNode)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemActivated.connect(self.onItemChanged)

    def update(self):
        self.clear()
        for node in TextNode.nodes.all():
            item = FragmentItem(node, self)
            self.addItem(item)
        super().update()

    def onItemChanged(self, item):
        self.fragmentItemActivated.emit(item.node)
