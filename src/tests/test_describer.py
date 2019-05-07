import unittest
from api import Describer
from tests.config import Config as TestConfig
from api.database import DataBaseConnection
from .test_processor import _fill_db
from api.graph_algs import GraphAlgDispatcher


class TestDescriber(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        DataBaseConnection(**TestConfig.NEO4J_DATA)

    def test_describe(self):
        self.processor = _fill_db()
        self.algorithm = self.processor.algorithms[0]

        desc = Describer(self.algorithm, self.processor)
        node_desc = desc.describe_node(self.processor.analyzer[0])
        self.assertGreater(len(node_desc), 0)
        alg_desc = desc.describe_results()
        self.assertGreater(len(alg_desc), 0)
        total_desc = desc.describe_results(all_algs=True)
        self.assertGreaterEqual(len(total_desc), 0)

    def test_describe_centrality(self):
        processor = _fill_db()
        algorithm = processor.algorithms[0]
        desc = Describer(algorithm, processor)
        disp = GraphAlgDispatcher(processor, algorithm)
        results = disp.dispatch_centrality()
        centr_desc = desc.describe_centrality_results(results)
        self.assertGreater(len(centr_desc), 0)

    def test_describe_community(self):
        processor = _fill_db()
        algorithm = processor.algorithms[0]
        desc = Describer(algorithm, processor)
        disp = GraphAlgDispatcher(processor, algorithm)
        results = disp.dispatch_community()
        comm_desc = desc.describe_community_results(results)
        self.assertGreater(len(comm_desc), 0)
