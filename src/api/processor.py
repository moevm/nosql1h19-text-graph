from typing import List, Pattern
from api.algorithm import AbstractAlgorithm, DictionaryAlgorithm, DiffAlgorithm
from api import FragmentsAnalyzer
from logger import log
from loading_wrapper import LoadingThread
from neomodel import db
from supremeSettings import SupremeSettings
from models import TextNode, GlobalResults


class TextProcessor:
    """Класс, выполняющие основные операции по работе с фрагментами.
    Внесение изменений в фрагменты требует явного выполнения синхронизации.
    Таким образом в БД не будут занесены ошибочные данные"""

    # TODO Подумать над объединенем TextProcessor и TextAnalyzer

    class PreprocessThread(LoadingThread):
        """Выполняет предобработку фрагментов"""

        def __init__(self, proc, parent=None):
            super().__init__(parent)
            self.proc = proc
            self.operation = 'Выполнение предобработки'
            self.set_interval(len(proc.analyzer))

        def run(self):
            for index, algorithm in enumerate(self.proc.algorithms):
                self.updateStatus.emit(f'Обработка алгоритма {algorithm.name}')
                log.info(f'Preprocessing for {algorithm}')
                for index, node in enumerate(self.proc.analyzer):
                    self.check_percent(index)
                    if not node.alg_results:
                        node.alg_results = algorithm.preprocess(node.text)
                    else:
                        node.alg_results = {
                            **node.alg_results,
                            **algorithm.preprocess(node.text)
                        }
            self.loadingDone.emit()

    class ProcessThread(LoadingThread):
        """Выполняет обработку фрагментов и производит общий анализ"""

        def __init__(self, proc, analyze=False, parent=None):
            super().__init__(parent)
            self.proc = proc
            self.operation = 'Выполнение алгоритмов'
            self.set_interval(len(proc.analyzer))
            self.analyze = analyze
            self.accs = None
            self.stats = None

        def run(self):
            min_intersection = SupremeSettings()['processor_min_intersection']
            log.info('Started processing')
            if self.analyze:
                accs = [None for _ in range(len(self.proc.algorithms))]
                self.accs = accs

            for i in range(len(self.proc.analyzer)):
                node1 = self.proc.analyzer[i]
                self.stats = self.proc._get_stats(node1, self.stats)
                for index, algorithm in enumerate(self.proc.algorithms):
                    if self.analyze:
                        accs[index] = algorithm.analyze(node1.alg_results,
                                                        accs[index])

                    for j in range(i + 1, len(self.proc.analyzer)):
                        node2 = self.proc.analyzer[j]
                        result = algorithm.compare(node1.alg_results,
                                                   node2.alg_results)
                        if result["intersection"] > min_intersection:
                            node1.link.connect(
                                node2, {
                                    "algorithm_name": algorithm.name,
                                    "intersection": result["intersection"],
                                    "data": result["data"]
                                }
                            )
                            if self.analyze:
                                accs[index] = algorithm.analyze_comparison(
                                    node1.alg_results, node2.alg_results,
                                    result, accs[index])
                self.check_percent(i)
            if self.analyze:
                self.proc._upload_results(self.accs, self.stats)
            self.loadingDone.emit()

    class DescribeThread(LoadingThread):
        def __init__(self, processor, parent=None):
            super().__init__(parent)
            self.operation = 'Общий анализ'
            self.proc = processor
            self.set_interval(len(processor.analyzer))

        def run(self):
            stats = None
            for index, node in enumerate(self.proc.analyzer):
                stats = self.proc._get_stats(node, stats)
                self.check_percent(index)
            self.stats = stats
            self.loadingDone.emit()

    class ClearResultsThread(LoadingThread):
        def __init__(self, proc, parent=None):
            super().__init__(parent)
            self.operation = 'Очистка результатов'
            self.proc = proc
            self.set_interval(len(self.proc.analyzer))

        def run(self):
            for index, node in enumerate(self.proc.analyzer):
                node.alg_results = {}
                node.link.disconnect_all()
                node.save()
                self.check_percent(index)
            self.proc._clear_results()
            self.loadingDone.emit()

    def __init__(self, algorithm_classes=None):
        super().__init__()
        if not algorithm_classes:
            self.algorithm_classes = [DictionaryAlgorithm, DiffAlgorithm]
        else:
            self.algorithm_classes = algorithm_classes
        self.algorithms: List[AbstractAlgorithm] = []
        self.analyzer = FragmentsAnalyzer()
        self.accs = None
        self.stats = None

        self.analyzer.download_db()
        self._download_results()
        self.set_up_algorithms()

    def set_up_algorithms(self):
        """Инициализация алгоритмов"""
        self.algorithms = []
        for algorithm_class in self.algorithm_classes:
            self.algorithms.append(algorithm_class())

    def alg_by_name(self, name):
        for algorithm in self.algorithms:
            if algorithm.name == name:
                return algorithm

        raise KeyError(f'No algorithm {name}')

    def parse_file(self, filename: str, regex: Pattern, get_name=None,
                   upload=True):
        """Считать файл и вытащить из него все фрагменты

        :param filename:
        :param get_name: Функция, получающая имя фрагмента по его номеру
        в текущем файле
        :type filename: str
        """
        self.analyzer.set_separator(regex)
        self.analyzer.read_file(filename, get_name)
        if upload:
            self.upload_db()

    def do_preprocess(self):
        """Выполнить предобработку.
        Для более интерактивной обработки использовать LoadingWrapper с
        PreprocessThread
        """
        thread = self.PreprocessThread(self)
        thread.run()
        thread.wait()

    def _get_stats(self, node: TextNode, acc=None):
        if acc is None:
            acc = {
                'frags': 0,
                'symbols': 0,
                'words': 0,
                'sentences': 0,
            }
        acc['frags'] += 1
        acc['symbols'] += node.character_num()
        acc['words'] += node.words_num()
        acc['sentences'] += node.sentences_num()
        return acc

    def do_process(self, analyze=False):
        thread = self.ProcessThread(self, analyze)
        thread.run()
        thread.wait()
        if analyze:
            return thread.accs, thread.stats

    def get_node_id_list(self, algorithm_name: str, exclude_zeros=False,
                         min_val=0):
        if len(self.analyzer) == 0:
            return None, None
        query = f"""
            MATCH (n:TextNode)-[r:ALG]-(n2:TextNode)
            WHERE r.algorithm_name = '{algorithm_name}'
                AND r.intersection >= {min_val}
            RETURN n.order_id, n2.order_id, r, n.alg_results
        """
        res, meta = db.cypher_query(query)
        # head - список номеров вершин для матрицы
        if exclude_zeros:  # Убрать нули
            head = list(set(id1 for id1, id2, r, res_a in res))
            head.sort()
        else:
            head = [node.order_id for node in self.analyzer]

        if len(head) == 0:
            return None, None
        return head, res

    def get_matrix(self, algorithm_name: str, exclude_zeros=False, min_val=0):
        """Получить матрицу, пригодную для обработки в MatrixWidget

        :param algorithm_name: имя алгоритма
        :type algorithm_name: str
        """
        head, res = self.get_node_id_list(algorithm_name, exclude_zeros,
                                          min_val)
        if not head:
            return [], []
        # Оптимизация для O(n)
        head_rev = list(range(max(head) + 1))
        for i, id_ in enumerate(head):
            head_rev[id_] = i

        # Сама матрица
        matrix = [[(0, None) for _ in range(len(head))]
                  for _ in range(len(head))]
        if res:
            for id1, id2, r, result in res:
                if r['intersection'] > min_val or not exclude_zeros:
                    matrix[head_rev[id1]][head_rev[id2]] = r['intersection'], \
                            (id1, id2, r)

        for i in range(len(matrix)):
            matrix[i][i] = (1, None)

        return matrix, head

    def get_node_list(self, head):
        """Получение """
        # query = f"""
        #     MATCH (n:TextNode)
        #     WHERE n.order_id in {str(head)}
        #     return n.alg_results
        #     ORDER BY n.order_id
        # """
        # res, meta = db.cypher_query(query)
        # return [json.loads(res_[0]) for res_ in res if res_[0]]
        if not head:
            return []
        return [self.analyzer[i] for i in head]

    def get_node_label(self, id):
        return self.analyzer[id].label

    def get_node_label_list(self, head):
        if not head:
            return []
        return [self.analyzer[i].label for i in head]

    def _download_results(self):
        nodes = GlobalResults.nodes.all()
        if len(nodes) > 0:
            node = nodes[0]
            self.accs = list(node.accs)
            self.stats = dict(node.stats)

    def _upload_results(self, accs=None, stats=None):
        accs = self.accs if accs is None else accs
        stats = self.stats if stats is None else stats
        self.stats = stats
        self.accs = accs

        nodes = GlobalResults.nodes.all()
        if self.stats is not None and self.accs is not None:
            if len(nodes) == 0:
                node = GlobalResults()
            else:
                node = nodes[0]
            node.accs = self.accs
            node.stats = self.stats
            node.save()
        else:
            self._clear_results()

    def _clear_results(self):
        for node in GlobalResults.nodes.all():
            node.delete()
        self.stats = None
        self.accs = None

    def clear_db(self):
        """Очистить  БД"""
        self.analyzer.clear()
        self.clear_results()

    def upload_db(self):
        """Загрузить изменения в БД"""
        thread = self.analyzer.UploadDBThread(self.analyzer)
        thread.run()
        thread.wait()
        self._upload_results()

    def clear_results(self):
        """Удалить результаты из БД"""
        thread = self.ClearResultsThread(self)
        thread.run()
        thread.wait()
        self._upload_results()
