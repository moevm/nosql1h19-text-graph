from api.database import DataBaseConnection
from api import TextProcessor
from ui import GraphWindow
from PyQt5.QtWidgets import QApplication
from tests.config import Config
import sys
from supremeSettings import SupremeSettings


if __name__ == "__main__":
    db = DataBaseConnection(**Config.NEO4J_DATA)
    app = QApplication(sys.argv)
    processor = TextProcessor()
    algorithm = processor.algorithms[0]
    window = GraphWindow(processor)
    window.show()
    window.accepted.connect(lambda: print(str(SupremeSettings())))
    sys.exit(app.exec_())
