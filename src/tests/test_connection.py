import unittest

from api.database import DataBaseConnection
from tests.config import Config as TestConfig


class DataBaseConnectionTest(unittest.TestCase):
    def test_connect(self):
        """
            Проверка подключения. Если не подключается, будет Exception
        """
        connection = DataBaseConnection(**TestConfig.NEO4J_DATA)
        connection.connect(**TestConfig.NEO4J_DATA)
