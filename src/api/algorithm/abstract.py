from abc import ABC, abstractmethod
from typing import Dict


class AbstractAlgorithm(ABC):
    @abstractmethod
    def preprocess(self, text: str) -> Dict:
        pass

    @abstractmethod
    def compare(self, res1: Dict, res2: Dict) -> Dict:
        pass
