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

    @abstractmethod
    def describe_result(self) -> str:  # TODO А это возможно вообще?
        """Возращает общие результаты работы алгоритма в виде HTML-строки

        :rtype: str
        """
        pass

    @abstractmethod
    def describe_comparison(self, comp_dict) -> str:
        """Описавает результаты сравнения фрагментов

        :param comp_dict: Словарь из AbstractAlgorithm.compare
        :rtype: str
        """
        pass

    @abstractmethod
    def describe_preprocess(self, prep_dict) -> str:
        """Описывает результаты предобработки фрагмента в виде HTML-строки

        :param prep_dict: Словарь из AbstractAlgorithm.preprocess
        :rtype: str
        """
        pass
