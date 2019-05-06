from PyQt5.QtWidgets import QMainWindow, QFontComboBox, QComboBox, \
        QApplication, QFileDialog, QDialog, QColorDialog, QListWidget
from PyQt5.QtGui import QFontDatabase, QTextDocumentWriter, QTextCharFormat, \
        QFont, QTextCursor, QTextListFormat, QTextFormat, QFontInfo, \
        QMouseEvent
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PyQt5.QtCore import Qt
import webbrowser
import pdfkit
import os
import subprocess
import platform

from ui_compiled.report_editor import Ui_ReportEditorWindow
from ui.report import AlgorithmReportFactory, StatsReport, LenghtDispGraph
from api import encapsulate_html
from supremeSettings import SupremeSettings


_report_classes = [StatsReport, LenghtDispGraph]


class ReportEditor(QMainWindow, Ui_ReportEditorWindow):
    def __init__(self, processor, parent=None):
        super().__init__(parent)
        self.processor = processor
        self.settings = SupremeSettings()
        self._report_items = {}

        self._file_name = None

        self.setupUi(self)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)

        self.actionUpdate.triggered.connect(self._create_report)
        self.usedList.doubleClicked.connect(
            lambda i: self.usedList.takeItem(i.row()))

        self._setup_text_editor()
        self._setup_text_connections()

        self._init_report_items()

    def _init_report_items(self):
        items = [report_class(self.processor, parent=self.availableList)
                 for report_class in _report_classes]
        factory = AlgorithmReportFactory(self.processor, self.availableList)
        items += factory.get_report_items()
        self._report_items = {}
        for report_item in items:
            self._report_items[report_item.name] = report_item
            self.availableList.addItem(report_item)
        self.availableList.mousePressEvent = self._av_list_mouse_press_event

    def _av_list_mouse_press_event(self, event: QMouseEvent):
        if event.button() == Qt.RightButton:
            item = self.availableList.itemAt(event.pos())
            if hasattr(item, 'settings'):
                item.change_settings()
        QListWidget.mousePressEvent(self.availableList, event)

    def _create_report(self):
        self.textEdit.clear()
        self.statusbar.showMessage('Создание отчёта...')
        html = ""
        for i in range(self.usedList.count()):
            list_item = self.usedList.item(i)
            report_item = self._report_items[list_item.text()]
            html += report_item.create_html()
        html = encapsulate_html(html)
        self.textEdit.setHtml(html)
        self.textEdit.document().setModified(True)
        self.statusbar.showMessage('Отчёт создан')

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
        self.fontToolBar.addWidget(self.styleComboBox)

        self.fontComboBox = QFontComboBox(self.fontToolBar)  # TODO connect
        self.fontToolBar.addWidget(self.fontComboBox)

        self.sizeComboBox = QComboBox(self.fontToolBar)  # TODO connect
        sizes = QFontDatabase.standardSizes()
        [self.sizeComboBox.addItem(str(size)) for size in sizes]
        self.sizeComboBox.setCurrentIndex(
            sizes.index(QApplication.font().pointSize()))
        self.fontToolBar.addWidget(self.sizeComboBox)

    def _setup_text_connections(self):
        self.textEdit.currentCharFormatChanged.connect(
            self._current_char_format_changed)
        self.textEdit.cursorPositionChanged.connect(
            self._cursor_position_changed)

        self.actionSave.triggered.connect(self._save)
        self.actionSaveAs.triggered.connect(self._save_as)
        self.actionBrowser.triggered.connect(self._browser)

        self.actionPrint.triggered.connect(self._print)
        self.actionPrintPreview.triggered.connect(self._print_preview)
        self.actionPDF.triggered.connect(self._print_pdf)

        self.textEdit.document().modificationChanged.connect(
            self.actionSave.setEnabled)
        self.textEdit.document().modificationChanged.connect(
            self.actionSaveAs.setEnabled)

        self.styleComboBox.activated.connect(self._text_style)
        self.fontComboBox.currentTextChanged.connect(self._text_family)
        self.sizeComboBox.currentTextChanged.connect(self._text_size)

        self.actionTextBold.triggered.connect(self._text_bold)
        self.actionTextItalic.triggered.connect(self._text_italic)
        self.actionTextUnderline.triggered.connect(self._text_underline)
        self.actionTextColor.triggered.connect(self._text_color)

        self.actionTextLeft.triggered.connect(self._text_align)
        self.actionTextRight.triggered.connect(self._text_align)
        self.actionTextCenter.triggered.connect(self._text_align)
        self.actionTextJustify.triggered.connect(self._text_align)

        self.actionUndo.triggered.connect(self.textEdit.undo)
        self.actionRedo.triggered.connect(self.textEdit.redo)

        self._font_changed(self.textEdit.font())
        self._color_changed(self.textEdit.textColor())
        self._alignment_changed(self.textEdit.alignment())

        self.actionSave.setEnabled(self.textEdit.document().isModified())
        self.actionUndo.setEnabled(self.textEdit.document().isUndoAvailable())
        self.actionRedo.setEnabled(self.textEdit.document().isRedoAvailable())
        QApplication.clipboard().dataChanged.connect(
            self._clipboard_data_changed)

    def _save(self):
        if not self._file_name:
            return self._save_as()
        if self._file_name.startswith(':/'):
            return self._save_as()

        writer = QTextDocumentWriter(self._file_name)
        success = writer.write(self.textEdit.document())
        if success:
            self.statusbar.showMessage('Сохранено успешно')
        else:
            self.statusbar.showMessage('Ошибка сохранения')

    def _save_as(self):
        dialog = QFileDialog(self, 'Сохранить как...')
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        mime_types = ["text/html", "text/plain",
                      "application/vnd.oasis.opendocument.text"]
        dialog.setMimeTypeFilters(mime_types)
        dialog.setDefaultSuffix("html")
        if dialog.exec_() != QDialog.Accepted:
            self.statusbar.showMessage('Сохранение отменено')
            return False
        self._file_name = dialog.selectedFiles()[0]
        return self._save()

    def _print(self):
        printer = QPrinter(QPrinter.HighResolution)
        self.print_dialog = QPrintDialog(printer, self)
        if self.textEdit.textCursor().hasSelection():
            self.print_dialog.addEnabledOption(QPrintDialog.PrintSelection)
        self.print_dialog.setWindowTitle('Печать')
        if self.print_dialog.exec_() == QDialog.accepted:
            self.textEdit.print(printer)
        self.print_dialog = None

    def _print_preview(self):
        printer = QPrinter(QPrinter.HighResolution)
        self.preview_dialog = QPrintPreviewDialog(printer, self)
        self.preview_dialog.paintRequested.connect(
            self._actually_print_preview)
        self.preview_dialog.exec_()

    def _browser(self, not_open=False):
        filename = f'{self.settings["tempdir"]}/temp_report.html'
        writer = QTextDocumentWriter(filename)
        writer.write(self.textEdit.document())
        if not not_open:
            webbrowser.open_new(filename)

    def _actually_print_preview(self, printer: QPrinter):
        self.textEdit.print(printer)

    def _print_pdf(self):
        dialog = QFileDialog(self, 'Сохранить в PDF')
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setMimeTypeFilters(['application/pdf'])
        dialog.setDefaultSuffix('pdf')
        if dialog.exec_() != QDialog.Accepted:
            return
        name = dialog.selectedFiles()[0]
        self._browser(True)
        pdfkit.from_file(f'{self.settings["tempdir"]}/temp_report.html', name)
        self.statusbar.showMessage('Экспорт успешен')
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', name))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(name)
        else:                                   # linux variants
            subprocess.call(('xdg-open', name))

    def _text_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if self.actionTextBold.isChecked()
                          else QFont.Normal)
        self._merge_text_format(fmt)

    def _text_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.actionTextItalic.isChecked())
        self._merge_text_format(fmt)

    def _text_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.actionTextUnderline.isChecked())
        self._merge_text_format(fmt)

    def _merge_text_format(self, format):
        cursor = self.textEdit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.textEdit.mergeCurrentCharFormat(format)

    def _cursor_position_changed(self):
        self._alignment_changed(self.textEdit.alignment())
        text_list = self.textEdit.textCursor().currentList()
        if text_list:
            list_formats = [
                QTextListFormat.ListDisc,
                QTextListFormat.ListCircle,
                QTextListFormat.ListSquare,
                QTextListFormat.ListDecimal,
                QTextListFormat.ListLowerAlpha,
                QTextListFormat.ListUpperAlpha,
                QTextListFormat.ListLowerRoman,
                QTextListFormat.ListUpperRoman
            ]
            try:
                list_index = list_formats.index(text_list.format().style())
            except ValueError:
                list_index = -1
            self.styleComboBox.setCurrentIndex(list_index)
        else:
            heading_level = self.textEdit.textCursor().blockFormat() \
                .headingLevel()
            self.styleComboBox.setCurrentIndex(
                heading_level + 8 if heading_level else 0)

    def _current_char_format_changed(self, format):
        self._font_changed(format.font())
        self._color_changed(format.foreground().color())

    def _text_style(self, index: int):
        styles = {
            1: QTextListFormat.ListDisc,
            2: QTextListFormat.ListCircle,
            3: QTextListFormat.ListSquare,
            4: QTextListFormat.ListDecimal,
            5: QTextListFormat.ListLowerAlpha,
            6: QTextListFormat.ListUpperAlpha,
            7: QTextListFormat.ListLowerRoman,
            8: QTextListFormat.ListUpperRoman
        }

        cursor = self.textEdit.textCursor()
        try:
            style = styles[index]
        except KeyError:
            style = None

        cursor.beginEditBlock()
        block_fmt = cursor.blockFormat()
        if style is None:
            block_fmt.setObjectIndex(-1)
            heading_level = index - 9 + 1 if index >= 9 else 0
            block_fmt.setHeadingLevel(heading_level)
            cursor.setBlockFormat(block_fmt)

            size = 4 - heading_level if heading_level else 0
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Bold if heading_level else QFont.Normal)
            fmt.setProperty(QTextFormat.FontSizeAdjustment, size)
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.mergeCharFormat(fmt)
            self.textEdit.mergeCurrentCharFormat(fmt)
        else:
            list_fmt = QTextListFormat()
            if cursor.currentList():
                list_fmt = cursor.currentList().format()
            else:
                list_fmt.setIndent(block_fmt.indent() + 1)
                block_fmt.setIndent(0)
                cursor.setBlockFormat(block_fmt)
            list_fmt.setStyle(style)
            cursor.createList(list_fmt)
        cursor.endEditBlock()

    def _text_family(self, font: str):
        fmt = QTextCharFormat()
        fmt.setFontFamily(font)
        self._merge_text_format(fmt)

    def _text_size(self, size: str):
        size = float(size)
        fmt = QTextCharFormat()
        fmt.setFontPointSize(size)
        self._merge_text_format(fmt)

    def _text_color(self):
        col = QColorDialog.getColor(self.textEdit.textColor(), self)
        if not col.isValid():
            return
        fmt = QTextCharFormat()
        fmt.setForeground(col)
        self._merge_text_format(fmt)
        self._color_changed(col)

    def _text_align(self):
        action = self.sender()
        if action == self.actionTextLeft:
            self.textEdit.setAlignment(Qt.AlignLeft | Qt.AlignAbsolute)
        elif action == self.actionTextCenter:
            self.textEdit.setAlignment(Qt.AlignHCenter)
        elif action == self.actionTextRight:
            self.textEdit.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        elif action == self.actionTextJustify:
            self.textEdit.setAlignment(Qt.AlignJustify)

    def _font_changed(self, font):
        self.fontComboBox.setCurrentIndex(self.fontComboBox.findText(
            QFontInfo(font).family()))
        self.sizeComboBox.setCurrentIndex(self.sizeComboBox.findText(
            str(int(font.pointSize()))))
        self.actionTextBold.setChecked(font.bold())
        self.actionTextItalic.setChecked(font.italic())
        self.actionTextUnderline.setChecked(font.underline())

    def _color_changed(self, color):
        pass

    def _alignment_changed(self, alignment):
        [a.setChecked(False) for a in
         (self.actionTextLeft, self.actionTextRight,
          self.actionTextCenter, self.actionTextJustify)]
        if alignment & Qt.AlignLeft:
            self.actionTextLeft.setChecked(True)
        elif alignment & Qt.AlignHCenter:
            self.actionTextCenter.setChecked(True)
        elif alignment & Qt.AlignRight:
            self.actionTextRight.setChecked(True)
        elif alignment & Qt.AlignJustify:
            self.actionTextJustify.setChecked(True)

    def _clipboard_data_changed(self):
        md = QApplication.clipboard().mimeData()
        if md:
            self.actionTextPaste.setEnabled(md.hasText())
