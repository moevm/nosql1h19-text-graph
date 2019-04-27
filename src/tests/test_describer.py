import unittest
from api import TextProcessor, Describer
from tests.config import Config as TestConfig
from api.database import DataBaseConnection


class TestDescriber(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        DataBaseConnection(**TestConfig.NEO4J_DATA)
        cls.processor = TextProcessor()
        cls.processor.clear_db()
        cls.algorithm = cls.processor.algorithms[0]

    def test_describe(self):
        self.processor.parse_file('../samples/short.txt', '\n{1}')
        self.processor.upload_db()
        self.processor.do_preprocess()
        accs, stats = self.processor.do_process(analyze=True)
        self.processor.upload_db()

        desc = Describer(self.algorithm, self.processor)
        node_desc = desc.describe_node(self.processor.analyzer[0])
        self.assertGreater(len(node_desc), 0)
        alg_desc = desc.describe_results(accs, stats)
        self.assertGreater(len(alg_desc), 0)
        total_desc = desc.describe_results(accs, all_algs=True)
        self.assertGreaterEqual(len(total_desc), 0)
