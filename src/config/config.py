class Config:
    NEO4J_URI = 'bolt://localhost:7687'
    NEO4J_LOGIN = 'neo4j'
    NEO4J_PASSWORD = 'kinix951'

    def get_uri(self):
        return f"{self.NEO4J_URI[0:7]}{self.NEO4J_LOGIN}:{self.NEO4J_PASSWORD}@{self.NEO4J_URI[7:]}"
