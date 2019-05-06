import unittest
from api import TextProcessor, Exporter
from api.database import DataBaseConnection
from tests.config import Config as TestConfig
from neomodel import db
import os


class TestExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        DataBaseConnection(**TestConfig.NEO4J_DATA)
        cls.processor = TextProcessor()
        cls.processor.clear_db()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists("_temp.graphml"):
            os.remove("_temp.graphml")

    def TestImportExport(self):
        def get_relation_number():
            query = """MATCH ()-[r]-() RETURN COUNT(r)"""
            res, meta = db.cypher_query(query)
            return res

        self.processor.parse_file('../samples/short.txt', '\n{1}')
        self.processor.upload_db()
        self.processor.do_preprocess()
        accs, stats = self.processor.do_process(analyze=True)
        self.processor.upload_db()
        self.processor.do_process(analyze=True)
        self.processor.upload_db()

        nodes_num = len(self.processor.analyzer)
        edge_num = get_relation_number()
        Exporter.export_db('_test.graphml')
        self.processor.clear_db()
        self.assertEqual(len(self.processor.analyzer), 0)
        self.assertEqual(get_relation_number(), 0)

        Exporter.import_db('_test.graphml')
        self.processor.download_db()
        self.assertEqual(len(self.processor.analyzer), nodes_num)
        self.assertEqual(get_relation_number(), edge_num)
