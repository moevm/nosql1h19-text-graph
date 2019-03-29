from neomodel import db

from logger import log


class DataBaseConnection:
    """
        Обертка над подключением к БД в neomodel
    """
    def __init__(self, uri: str, login: str, password: str):
        """
            :exception neo4j.exceptions.ServiceUnavailable: Если не подключается
        """
        self.connect(uri, login, password)

    @staticmethod
    def get_uri(url: str, login: str, password: str):
        """
            Добавляет логин и пароль в URI
        """
        uri = f"{url[0:7]}{login}:{password}@{url[7:]}"
        return uri

    def connect(self, uri: str, login: str, password: str):
        """
            :exception neo4j.exceptions.ServiceUnavailable: Если не подключается
        """
        uri = DataBaseConnection.get_uri(uri, login, password)
        log.debug(f'Connecting to {uri}')
        db.set_connection(uri)
