from .centrality import centrality_algs
from .community import comm_algs


__all__ = ['GraphAlgDispatcher']


class GraphAlgDispatcher:
    def __init__(self, processor, algorithm):
        self.processor = processor
        self.algorithm = algorithm

    def dispatch_centrality(self, *args, **kwargs):
        return self._dispatch(centrality_algs, *args, **kwargs)

    def dispatch_community(self, *args, **kwargs):
        return self._dispatch(comm_algs, *args, **kwargs)

    def _dispatch(self, algs, test_alg_func=None):
        def test_alg_func(n):
            return True if test_alg_func is None \
                else test_alg_func
        results = {}
        for alg_cls in algs:
            alg = alg_cls(self.processor, self.algorithm)
            if test_alg_func(alg):
                results[alg.name] = alg.exec_query()
        return results
