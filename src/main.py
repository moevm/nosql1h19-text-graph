import logging.config
from PyQt5.QtWidgets import QApplication
import sys

from config.config import Config
from ui.graph_window import GraphWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    logging.config.dictConfig(Config.LOGGING_CONFIG)
    logger = logging.getLogger('root')
    logger.info('Starting app...')
    window = GraphWindow()
    window.show()

    sys.exit(app.exec_())
