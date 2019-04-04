from abc import ABC, abstractmethod, abstractproperty
from typing import Dict


class AbstractAlgorithm(ABC):
    @abstractmethod
    def preprocess(self, text: str) -> Dict:
        """Применяется к каждому фрагменту текста.

        :param text: Текст
        :type text: str
        :rtype: Dict
        :return: Словарь вида {
            Параметр: Значение
        }
        """
        pass

    @abstractmethod
    def compare(self, res1: Dict, res2: Dict) -> Dict:
        """Сравнивает два словаря, возвращаемые preprocess.
        Применяется к каждой уникальной паре фрагментов текста
        :type res1: Dict
        :type res2: Dict
        :rtype: Dict
        :return: Словарь вида {
            intersection: Численная характеристика связи от 0 до 1
            data: Прочие характеристики связи
        }
        """
        pass

    @abstractproperty
    def name(self) -> str:
        pass
