import unittest
from api.connection import DataBaseConnection
config = {
    'uri': 'bolt://localhost:7687',
    'login': 'neo4j',
    'password': 'kinix951'
}


class DataBaseConnectionTest(unittest.TestCase):
    def test_connect(self):
        """
            Проверка подключения. Если не подключается, будет Exception
        """
        connection = DataBaseConnection(**config)
        connection.connect(**config)
