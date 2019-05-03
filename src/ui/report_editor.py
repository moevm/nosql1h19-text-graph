from PyQt5.QtWidgets import QMainWindow, QFontComboBox, QComboBox, QApplication
from PyQt5.QtGui import QFontDatabase

from ui_compiled.report_editor import Ui_ReportEditorWindow
from ui.report import AbstractReportItem, AlgorithmReportFactory
from api import encapsulate_html


_report_classes = [AbstractReportItem]


class ReportEditor(QMainWindow, Ui_ReportEditorWindow):
    def __init__(self, processor, parent=None):
        super().__init__(parent)
        self.processor = processor
        self._report_items = {}

        self.setupUi(self)
        self.actionUpdate.triggered.connect(self._create_report)

        self._setup_text_editor()

        self._init_report_items()

    def _setup_text_editor(self):
        self.styleComboBox = QComboBox(self.fontToolBar)
        self.styleComboBox.addItem("Standard")
        self.styleComboBox.addItem("Bullet List (Disc)")
        self.styleComboBox.addItem("Bullet List (Circle)")
        self.styleComboBox.addItem("Bullet List (Square)")
        self.styleComboBox.addItem("Ordered List (Decimal)")
        self.styleComboBox.addItem("Ordered List (Alpha lower)")
        self.styleComboBox.addItem("Ordered List (Alpha upper)")
        self.styleComboBox.addItem("Ordered List (Roman lower)")
        self.styleComboBox.addItem("Ordered List (Roman upper)")
        self.styleComboBox.addItem("Heading 1")
        self.styleComboBox.addItem("Heading 2")
        self.styleComboBox.addItem("Heading 3")
        self.styleComboBox.addItem("Heading 4")
        self.styleComboBox.addItem("Heading 5")
        self.styleComboBox.addItem("Heading 6")
        self.fontToolBar.addWidget(self.styleComboBox)  # TODO connect

        self.fontComboBox = QFontComboBox(self.fontToolBar)  # TODO connect
        self.fontToolBar.addWidget(self.fontComboBox)

        self.sizeComboBox = QComboBox(self.fontToolBar)
        sizes = QFontDatabase.standardSizes()
        [self.sizeComboBox.addItem(str(size)) for size in sizes]
        self.sizeComboBox.setCurrentIndex(
            sizes.index(QApplication.font().pointSize()))
        self.fontToolBar.addWidget(self.sizeComboBox)

    def _init_report_items(self):
        items = [report_class(self.processor, parent=self.availableList)
                 for report_class in _report_classes]
        factory = AlgorithmReportFactory(self.processor, self.availableList)
        items += factory.get_report_items()
        self._report_items = {}
        for report_item in items:
            self._report_items[report_item.name] = report_item
            self.availableList.addItem(report_item)

    def _create_report(self):
        self.textEdit.clear()
        html = ""
        for i in range(self.usedList.count()):
            list_item = self.usedList.item(i)
            report_item = self._report_items[list_item.text()]
            html += report_item.create_html()
        html = encapsulate_html(html)
        self.textEdit.setHtml(html)
