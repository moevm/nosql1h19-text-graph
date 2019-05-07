from .centrality import centrality_algs


class CentralityDispatcher:
    def __init__(self, processor, algorithm):
        self.processor = processor
        self.algorithm = algorithm

    def dispatch(self, test_alg_func=None):
        def test_alg_func(n):
            return True if test_alg_func is None \
                else test_alg_func
        results = {}
        for alg_cls in centrality_algs:
            alg = alg_cls(self.processor, self.algorithm)
            if test_alg_func(alg):
                results[alg.name] = alg.exec_query()
        return results
