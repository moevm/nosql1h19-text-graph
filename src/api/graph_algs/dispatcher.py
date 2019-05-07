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

    def _dispatch(self, algs, _test_alg_func=None, *args, **kwargs):
        def test_alg_func(n):
            if _test_alg_func is None:
                return True
            else:
                return _test_alg_func(n)
        results = {}
        for alg_cls in algs:
            alg = alg_cls(self.processor, self.algorithm, *args, **kwargs)
            if test_alg_func(alg):
                results[alg.name] = alg.exec_query()
        return results
