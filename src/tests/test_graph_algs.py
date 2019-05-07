import unittest

from .test_processor import _fill_db
from api.graph_algs import centrality_algs
from api.database import DataBaseConnection
from api import TextProcessor
from tests.config import Config as TestConfig


class TestAlgs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        DataBaseConnection(**TestConfig.NEO4J_DATA)
        TextProcessor().clear_db()

    def test_centrality(self):
        processor = _fill_db()
        algorithm = processor.algorithms[0]
        algs = [alg_cls(processor, algorithm) for alg_cls in centrality_algs]
        results = [alg.exec_query() for alg in algs]
        for result in results:
            self.assertGreater(len(result), 0)
