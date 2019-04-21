from PyQt5.QtWidgets import QMainWindow
from api import TextProcessor
from ui_compiled.mainwindow import Ui_MainWindow
from .fragments_window import FragmentsWindow
from ui.widgets import FragmentsList, AlgorithmResults
from .loading_dialog import LoadingWrapper


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.actionCloseProject.triggered.connect(self.removeProject)
        self.actionNew.triggered.connect(self.setNewProject)
        self.actionChangeFragments.triggered.connect(self.editFragments)
        self.actionClear.triggered.connect(self.clearResults)
        self.actionStartProcess.triggered.connect(self.startAlgorithm)

        self.en_project = [  # Включить, когда есть проект
            self.actionCloseProject,
            # self.actionSave,  # TODO
            self.actionChangeFragments,
            self.actionClear
        ]

        self.en_algorithm_results = [  # Включить, когда есть результаты
            self.dictIntersectTab,
            self.namesIntersectTab,
            self.dictThresholdSlider  # FIXME в mainwindow.ui что-то сломалось
        ]

        self.en_process_fragments = [  # Включить, когда загружены фрагменты
            self.actionStartProcess,
            self.actionClear,
            self.startProcessButton,
        ]

        self.processor = None  # Обработчик текста
        self.fragments_list = None  # Виджет с фрагментами
        self.tabs = []  # Вкладки с результатами алгоритмов

        self.removeProject()

    def initalizeAlgorithms(self):
        while self.mainTab.count() > 1:
            self.mainTab.removeTab(self.mainTab.count() - 1)
        self.tabs.clear()
        for algorithm in self.processor.algorithms:
            tab = AlgorithmResults(algorithm, self.processor)
            self.tabs.append(tab)
            self.mainTab.addTab(tab, algorithm.name)

    def updateEnabled(self):
        """Установить enabled для виджетов, action'ов и т.п. """
        if self.processor is None:
            [item.setEnabled(False) for item in self.en_algorithm_results]
            [item.setEnabled(False) for item in self.en_process_fragments]
            [item.setEnabled(False) for item in self.en_project]
        else:
            [item.setEnabled(True) for item in self.en_project]
            if len(self.processor.analyzer) > 0:
                [item.setEnabled(True) for item in self.en_process_fragments]

    def removeProject(self):
        """Удаление проекта"""
        self.mainTab.hide()
        self.infoLabel.show()
        if self.processor:
            self.processor = None
        self.updateEnabled()

    def setNewProject(self):
        """Установка нового проекта"""
        self.mainTab.setCurrentIndex(0)
        self.mainTab.show()
        self.infoLabel.hide()

        if self.fragments_list:
            self.fragmentsWidgetLayout.removeWidget(self.fragments_list)
        self.fragments_list = FragmentsList(self)
        self.fragmentsWidgetLayout.addWidget(self.fragments_list)
        self.fragments_list.update()

        self.processor = TextProcessor()
        self.initalizeAlgorithms()
        self.updateEnabled()
        self.editFragments()

    def editFragments(self):
        """Запустить редактирование фрагментов"""
        self.fragments = FragmentsWindow(self.processor, self)
        self.fragments.show()
        self.fragments.fragmentsChanged.connect(self.fragments_list.update)
        self.fragments.fragmentsChanged.connect(self.updateResults)
        self.fragments.fragmentsChanged.connect(self.updateEnabled)

    def startAlgorithm(self):
        """Запустить алгоритм"""
        self.thread = self.processor.PreprocessThread(self.processor)
        self.loading = LoadingWrapper(self.thread)
        self.loading.loadingDone.connect(self._continueAlgorithm)
        self.loading.start()

    def _continueAlgorithm(self):
        """Продолжить выполнение алгоритма"""
        # TODO Сюда впихнуть промежуточные настройки
        self.thread = self.processor.ProcessThread(self.processor)
        self.loading = LoadingWrapper(self.thread)
        self.loading.loadingDone.connect(self.uploadDB)
        self.loading.start()

    def uploadDB(self):
        self.thread = self.processor.analyzer.UploadDBThread(
            self.processor.analyzer)
        self.loading = LoadingWrapper(self.thread)
        self.loading.loadingDone.connect(self.updateResults)
        self.loading.loadingDone.connect(self.fragments_list.update)
        self.loading.start()

    def updateResults(self):
        [item.setEnabled(True) for item in self.en_algorithm_results]
        [tab.updateResults() for tab in self.tabs]

    def clearResults(self):
        self.thread = self.processor.ClearResultsThread(self.processor)
        self.loading = LoadingWrapper(self.thread)
        self.loading.loadingDone.connect(self.uploadDB)
        self.loading.start()
