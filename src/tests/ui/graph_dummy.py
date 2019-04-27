import setup_

from api.database import DataBaseConnection
from api import TextProcessor
from ui import GraphWindow
from PyQt5.QtWidgets import QApplication
from tests.config import Config
import sys


if __name__ == "__main__":
    db = DataBaseConnection(**Config.NEO4J_DATA)
    app = QApplication(sys.argv)
    processor = TextProcessor()
    algorithm = processor.algorithms[0]
    window = GraphWindow(processor)
    window.show()
    sys.exit(app.exec_())
