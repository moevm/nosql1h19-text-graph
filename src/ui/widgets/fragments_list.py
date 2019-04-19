from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from models import TextNode


class FragmentItem(QListWidgetItem):
    def __init__(self, node, parent=None, frag_num=0):
        super().__init__(parent)
        self.node = node
        self.setText(node.preview(frag_num))


class FragmentsList(QListWidget):
    fragmentItemActivated = pyqtSignal(TextNode)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortingEnabled(True)
        self.itemActivated.connect(self.onItemChanged)

    def update(self):
        self.clear()
        nodes = TextNode.nodes.all()
        frag_num = len(nodes)
        for node in nodes:
            item = FragmentItem(node, self, frag_num)
            self.addItem(item)
        self.sortItems(Qt.AscendingOrder)
        super().update()

    def onItemChanged(self, item):
        self.fragmentItemActivated.emit(item.node)
