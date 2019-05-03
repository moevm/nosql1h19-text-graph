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

    def analyze(self, res: Dict, acc=None):
        """Получить общие результаты. Этот метод должен применится к каждому
        фрагменту. После чего полученный объект-аккумулятор передается в
        AbstractAlgorithm.describe_result для получения общих результатов
        работы

        В отличие от остальных методов, имеет стандартную реализацию, но
        имеет смысл его переопределить/расширить в наследниках,
        чтобы получить более конкретные результаты.

        :param res: результат AbstractAlgorithm.preprocess
        :type res: Dict
        :param acc: аккумулятор. Хранит данные об обработке всех предыдущих
        :return: Аккумулятор
        """
        if acc is None:
            acc = {
                'fragments': 0,
                'edges': 0,
                'sum_intersect': 0
            }
        acc['fragments'] += 1
        return acc

    def analyze_comparison(self, res1: Dict, res2: Dict,
                           comp_res: Dict, acc):
        """Проанализировать результаты сравнения фрагментов.
        Этот метод должен применится к каждой связи.

        :param res1: Результат AbstractAlgorithm.preprocess
        :type res1: Dict
        :param res2: Результат AbstractAlgorithm.preprocess
        :type res2: Dict
        :param comp_res: Результат AbstractAlgorithm.compare(res1, res2)
        :type comp_res: Dict
        :param acc: тот же аккумулятор, что и в AbstractAlgorithm.analyze
        """
        acc['edges'] += 1
        acc['sum_intersect'] += comp_res['intersection']
        return acc

    def describe_result(self, acc) -> str:
        """Описывает общие результаты работы алгоритма в формате HTML-строки

        :param acc: Результат применение AbstractAlgorithm.analyze ко всем
        фрагментам
        :rtype: str
        """
        return f"""
            Проанализировано фрагментов: {acc['fragments']} <br>
            Найдено связей: {acc['edges']} <br>
            Среднее пересечение:
                {acc['sum_intersect'] / acc['edges'] * 100:.2f}%
        """

    @abstractmethod
    def describe_comparison(self, comp_dict) -> str:
        """Описывает результаты сравнения фрагментов

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
