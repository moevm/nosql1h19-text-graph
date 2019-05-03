from PyQt5.QtWidgets import QMainWindow

from ui_compiled.report_editor import Ui_ReportEditorWindow
from ui.report import AbstractReportItem
from api import encapsulate_html


_report_classes = [AbstractReportItem]


class ReportEditor(QMainWindow, Ui_ReportEditorWindow):
    def __init__(self, processor, parent=None):
        super().__init__(parent)
        self.processor = processor
        self._report_items = {}

        self.setupUi(self)
        self.actionUpdate.triggered.connect(self._create_report)

        self._init_report_items()

    def _init_report_items(self):
        self._report_items = {}
        for report_class in _report_classes:
            report_item = report_class(self.processor, self.availableList)
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
