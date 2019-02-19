from neo4j import GraphDatabase


class HelloWorldExample(object):

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()


database = HelloWorldExample('http://localhost:7474/', 'neo4j', 'neo4j')
database.close()
