from neomodel import db
from abc import ABC, abstractmethod, abstractproperty
from typing import List


__all__ = ['centrality_algs', 'AbstractCentralityGraphAlg',
           'AverageIntersectionCentrality', 'EigenvectorCentrality']


class AbstractCentralityGraphAlg(ABC):
    def __init__(self, processor, algorithm, min_val=0):
        self.processor = processor
        self.algorithm = algorithm
        self.min_val = min_val

    def _node_query(self):
        return 'MATCH (n:TextNode) RETURN id(n) as id'

    def _rel_query(self):
        # TODO А нужен ли здесь min_val?
        return f"""
            MATCH (n:TextNode)-[r:ALG]-(n2:TextNode)
            WHERE r.algorithm_name = '{self.algorithm.name}'
            RETURN id(n) as source, id(n2) as target, r.intersection as weight
        """

    @abstractproperty
    def query(self):
        pass

    @abstractproperty
    def name(self):
        pass

    def exec_query(self):
        """Выполнить запрос

        :rtype: List[int, str,float]
        :return: Список [order_id, label, score]
        """
        res, meta = db.cypher_query(self.query)
        res = [(int(order_id), label, float(score))
               for order_id, label, score in res]
        return res


class AverageIntersectionCentrality(AbstractCentralityGraphAlg):
    @property
    def name(self):
        return "Среднее пересечение"

    @property
    def query(self):
        return f"""
        MATCH (n:TextNode)
        OPTIONAL MATCH (n)-[r:ALG]-(n2:TextNode)
        WHERE r.algorithm_name='{self.algorithm.name}'
        WITH avg(r.intersection) as intersection, n as n
        RETURN n.order_id, n.label, CASE intersection WHEN null THEN 0
            ELSE round(intersection * 10000) / 10000 END
        ORDER BY n.order_id
        """


class EigenvectorCentrality(AbstractCentralityGraphAlg):
    @property
    def name(self):
        return "Эйгенвектор"

    @property
    def query(self):
        return """
            CALL algo.eigenvector.stream("%s", "%s", {
                graph: 'cypher',
                weightProperty: 'weight',
                normalization: 'max',
                write: false
        })
        YIELD nodeId, score

        RETURN algo.asNode(nodeId).order_id as order_id,
            algo.asNode(nodeId).label AS label,
            round(score * 10000) / 10000
        ORDER BY score DESC
        """ % (self._node_query(), self._rel_query())


centrality_algs = [EigenvectorCentrality, AverageIntersectionCentrality]
