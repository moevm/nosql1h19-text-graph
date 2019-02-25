from config.config import Config
from neomodel import config as neo_config
from models.helloNode import HelloNode


class HelloWorldExample(object):
    def __init__(self, uri, user, password):
        neo_config.DATABASE_URL = f"{uri[0:7]}{user}:{password}@{uri[7:]}"
        print(neo_config.DATABASE_URL)

    def close(self):
        pass

    def print_greeting(self, message):
        hello = HelloNode(hello_text=message)
        hello.save()
        return hello.__repr__()


if __name__ == "__main__":
    db = HelloWorldExample(Config.NEO4J_URI, Config.NEO4J_LOGIN, Config.NEO4J_PASSWORD)
