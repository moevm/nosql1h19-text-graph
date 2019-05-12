from neomodel import db
from abc import ABC, abstractmethod, abstractproperty
from .centrality import AbstractGraphAlg


__all__ = ['AbstractCommGraphAlg', 'comm_algs']



class AbstractCommGraphAlg(AbstractGraphAlg):
    def exec_query(self):
        res, meta = db.cypher_query(self.query)
        communities = {}
        for i in range(len(res)):
            order_id, label, comm = res[i]
            try:
                comm = communities[comm]
            except KeyError:
                comm = communities[comm] = len(communities)
            res[i] = int(order_id), label, comm
        return res


class LouvainCommGraphAlg(AbstractCommGraphAlg):
    @property
    def name(self):
        return "Louvain"

    @property
    def query(self):
        return """
            CALL algo.louvain.stream("%s", "%s", {
                graph: 'cypher',
                weightProperty: 'weight',
                write: false
            })
            YIELD nodeId, community
            RETURN algo.asNode(nodeId).order_id as order_id,
                algo.asNode(nodeId).label AS label,
                community
            ORDER BY community
        """ % (self._node_query(), self._rel_query())


class LabelPropagationGraphAlg(AbstractCommGraphAlg):
    @property
    def name(self):
        return "Label Propagation"

    @property
    def query(self):
        return """
            CALL algo.labelPropagation.stream("%s", "%s", {
                graph: 'cypher',
                direction: 'BOTH',
                weightProperty: 'weight',
                write: false
            })
            YIELD nodeId, label as community
            RETURN algo.asNode(nodeId).order_id as order_id,
                algo.asNode(nodeId).label AS label,
                community
            ORDER BY community
        """ % (self._node_query(), self._rel_query())


class UnionGraphAlg(AbstractCommGraphAlg):
    @property
    def name(self):
        return "Connected Components"

    @property
    def query(self):
        return """
            CALL algo.unionFind.stream("%s", "%s", {
                graph: 'cypher',
                write: false
            })
            YIELD nodeId, setId as community
            RETURN algo.asNode(nodeId).order_id as order_id,
                algo.asNode(nodeId).label AS label,
                community
            ORDER BY community
        """ % (self._node_query(), self._rel_query())

comm_algs = [LouvainCommGraphAlg, LabelPropagationGraphAlg, UnionGraphAlg]
