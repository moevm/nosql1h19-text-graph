import setup_

from PyQt5.QtWidgets import QApplication

from ui.widgets import TextBrowser
import sys


text = """
    <h1>Header</h1>
    <!-- COLLAPSE текст -->
        Должно сворачиваться <br>
        Всё ещё должно <br>
    <!-- END COLLAPSE -->
    А теперь не должно
"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = TextBrowser()
    widget.setHtml(text * 4)
    widget.show()
    sys.exit(app.exec_())
