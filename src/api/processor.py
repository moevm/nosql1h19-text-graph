from typing import List, Pattern
from api.algorithm import AbstractAlgorithm, DictionaryAlgorithm, DummyAlgorithm
from api import FragmentsAnalyzer
from logger import log
from loading_wrapper import LoadingThread
from neomodel import db


class TextProcessor:
    """Класс, выполняющие основные операции по работе с фрагментами.
    Внесение изменений в фрагменты требует явного выполнения синхронизации.
    Таким образом в БД не будут занесены ошибочные данные"""

    # TODO Подумать над объединенем TextProcessor и TextAnalyzer

    class PreprocessThread(LoadingThread):
        def __init__(self, proc, parent=None):
            super().__init__(parent)
            self.proc = proc
            self.operation = 'Выполнение предобработки'
            self.setInterval(len(proc.analyzer))

        def run(self):
            for index, algorithm in enumerate(self.proc.algorithms):
                self.updateStatus.emit(f'Обработка алгоритма {algorithm.name}')
                log.info(f'Preprocessing for {algorithm}')
                for index, node in enumerate(self.proc.analyzer):
                    self.checkPercent(index)
                    if not node.alg_results:
                        node.alg_results = algorithm.preprocess(node.text)
                    else:
                        node.alg_results = {
                            **node.alg_results,
                            **algorithm.preprocess(node.text)
                        }
            self.loadingDone.emit()

    class ProcessThread(LoadingThread):
        def __init__(self, proc, parent=None):
            super().__init__(parent)
            self.proc = proc
            self.operation = 'Выполнение алгоритмов'
            self.setInterval(len(proc.analyzer))

        def run(self):
            log.info('Started processing')
            for i in range(len(self.proc.analyzer)):
                for j in range(i + 1, len(self.proc.analyzer)):
                    node1 = self.proc.analyzer[i]
                    node2 = self.proc.analyzer[j]
                    for algorithm in self.proc.algorithms:
                        result = algorithm.compare(node1.alg_results,
                                                   node2.alg_results)
                        if result["intersection"] > 0:
                            node1.link.connect(
                                node2, {
                                    "algorithm_name": algorithm.name,
                                    "intersection": result["intersection"],
                                    "data": result["data"]
                                }
                            )
                self.checkPercent(i)
            self.loadingDone.emit()

    class ClearResultsThread(LoadingThread):
        def __init__(self, proc, parent=None):
            super().__init__(parent)
            self.operation = 'Очистка результатов'
            self.proc = proc
            self.setInterval(len(self.proc.analyzer))

        def run(self):
            for index, node in enumerate(self.proc.analyzer):
                node.link.disconnect_all()
                self.checkPercent(index)
            self.loadingDone.emit()

    def __init__(self, algorithm_classes=None):
        super().__init__()
        if not algorithm_classes:
            self.algorithm_classes = [DictionaryAlgorithm]
        else:
            self.algorithm_classes = algorithm_classes
        self.algorithms: List[AbstractAlgorithm] = []
        self.analyzer = FragmentsAnalyzer()
        self.analyzer.download_db()
        self.set_up_algorithms()

    def set_up_algorithms(self):
        """Инициализация алгоритмов"""
        self.algorithms = []
        for algorithm_class in self.algorithm_classes:
            self.algorithms.append(algorithm_class())

    def parse_file(self, filename: str, regex: Pattern):
        """Считать файл и вытащить из него все фрагменты

        :param filename:
        :type filename: str
        """
        self.analyzer.set_separator(regex)
        self.analyzer.read_file(filename)
        self.upload_db()

    def do_preprocess(self):
        thread = self.PreprocessThread(self)
        thread.run()
        thread.wait()

    def do_process(self):
        thread = self.ProcessThread(self)
        thread.run()
        thread.wait()

    def get_matrix(self, algorithm_name: str, exclude_zeros=False, min_val=0):
        """Получить матрицу, пригодную для обработки в MatrixWidget

        :param algorithm_name: имя алгоритма
        :type algorithm_name: str
        """
        if (len(self.analyzer)) == 0:
            return [], []

        query = f"""
            MATCH (n:TextNode)-[r:ALG]-(n2:TextNode)
            WHERE r.algorithm_name = '{algorithm_name}'
            RETURN n.order_id, n2.order_id, r, n.alg_results
        """
        res, meta = db.cypher_query(query)
        # head - список номеров вершин для матрицы
        if exclude_zeros:  # Убрать нули
            head = list(set(id1 for id1, id2, r, res_a in res
                            if r['intersection'] > min_val))
            head.sort()
        else:
            head = [node.order_id for node in self.analyzer]

        if len(head) == 0:
            return [], []
        # Оптимизация для O(n)
        head_rev = list(range(max(head) + 1))
        for i, id_ in enumerate(head):
            head_rev[id_] = i

        # Сама матрица
        matrix = [[(0, None) for _ in range(len(head))]
                  for _ in range(len(head))]
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
        return [self.analyzer[i] for i in head]

    def clear_db(self):
        """Очистить  БД"""
        self.analyzer.clear()

    def upload_db(self):
        """Загрузить изменения в БД"""
        thread = self.analyzer.UploadDBThread(self.analyzer)
        thread.run()
        thread.wait()

    def clear_results(self):
        """Удалить результаты из БД"""
        thread = self.ClearResultsThread(self)
        thread.run()
        thread.wait()
