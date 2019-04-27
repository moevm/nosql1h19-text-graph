import numpy as np
from api.algorithm import AbstractAlgorithm
from typing import Dict

class DummyAlgorithm(AbstractAlgorithm):
    def preprocess(self, text: str) -> Dict:
        return {
            "lol": "kek"
        }

    def compare(self, res1: Dict, res2: Dict) -> Dict:
        return {
            "intersection": np.random.random(),
            "data": {
                "kek": "lol"
            }
        }

    @property
    def name(self):
        return "DUMMY"

    def describe_result(self):
        return "Dummy describe results"

    def describe_comparison(self, comp_dict):
        return "Dummy describe_comparison"

    def describe_preprocess(self, prep_dict):
        return "Dummy describe preprocess"
