from neomodel import db


class Exporter:
    @staticmethod
    def import_db(filename):
        Exporter.purge_db()
        query = """
            CALL apoc.import.graphml('%s',
                                      {readLabels: true})
        """ % filename
        db.cypher_query(query)

    @staticmethod
    def export_db(filename):
        query = """
            CALL apoc.export.graphml.all('%s',
                                         {useTypes: true})
        """ % filename
        db.cypher_query(query)

    @staticmethod
    def purge_db():
        query = """MATCH p=()-->()
                DELETE p
                """
        db.cypher_query(query)
