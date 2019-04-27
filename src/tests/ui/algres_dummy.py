import setup_

from api import TextProcessor
from api.database import DataBaseConnection
from api.algorithm import DictionaryAlgorithm
from ui.widgets import AlgorithmResults
from PyQt5.QtWidgets import QApplication
from tests.config import Config
import sys


if __name__ == "__main__":
    db = DataBaseConnection(**Config.NEO4J_DATA)
    proc = TextProcessor()
    alg = DictionaryAlgorithm()
    app = QApplication(sys.argv)
    widget = AlgorithmResults(alg, proc)
    widget.show()

    sys.exit(app.exec_())
