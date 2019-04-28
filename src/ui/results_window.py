from PyQt5.QtWidgets import QMainWindow
from api import TextProcessor, Describer
from ui_compiled.mainwindow import Ui_MainWindow
from .fragments_window import FragmentsWindow
from ui.widgets import FragmentsList, AlgorithmResults
from .loading_dialog import LoadingWrapper
from .settings import SettingsDialog
from supremeSettings import SupremeSettings


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.settings = SupremeSettings()

        self.actionCloseProject.triggered.connect(self.remove_project)
        self.actionNew.triggered.connect(self.set_new_project)
        self.actionChangeFragments.triggered.connect(self.edit_fragments)
        self.actionClear.triggered.connect(self.clear_results)
        self.actionStartProcess.triggered.connect(self.start_algorithm)
        self.actionUpdateResults.triggered.connect(self.update_results)
        self.actionOpenParams.triggered.connect(self.open_settings)
        self.actionClearDB.triggered.connect(self.clear_db)

        self.en_project = [  # Включить, когда есть проект
            self.actionCloseProject,
            # self.actionSave,  # TODO
            self.actionChangeFragments,
            self.actionClear
        ]

        self.en_algorithm_results = [  # Включить, когда есть результаты
        ]

        self.en_process_fragments = [  # Включить, когда загружены фрагменты
            self.actionStartProcess,
            self.actionClear,
            self.startProcessButton,
            self.actionUpdateResults
        ]

        self.processor = None  # Обработчик текста
        self.fragments_list = None  # Виджет с фрагментами
        self.tabs = []  # Вкладки с результатами алгоритмов
        self.auto_update = SupremeSettings()['result_auto_update']
        self.accs = None
        self.stats = None

        self.remove_project()

    def initalize_algorithms(self):
        while self.mainTab.count() > 1:
            self.mainTab.removeTab(self.mainTab.count() - 1)
        self.tabs.clear()
        for algorithm in self.processor.algorithms:
            tab = AlgorithmResults(algorithm, self.processor)
            self.tabs.append(tab)
            self.mainTab.addTab(tab, algorithm.name)

    def update_enabled(self):
        """Установить enabled для виджетов, action'ов и т.п. """
        if self.processor is None:
            [item.setEnabled(False) for item in self.en_algorithm_results]
            [item.setEnabled(False) for item in self.en_process_fragments]
            [item.setEnabled(False) for item in self.en_project]
        else:
            [item.setEnabled(True) for item in self.en_project]
            if len(self.processor.analyzer) > 0:
                [item.setEnabled(True) for item in self.en_process_fragments]

    def open_settings(self):
        self.settings_dialog = SettingsDialog()
        self.settings_dialog.accepted.connect(self.on_settings_accepted)
        self.settings_dialog.show()

    def on_settings_accepted(self):
        pass

    def remove_project(self):
        """Удаление проекта"""
        self.mainTab.hide()
        self.infoLabel.show()
        if self.processor:
            self.processor = None
        self.accs = None
        self.stats = None
        self.update_enabled()

    def set_new_project(self):
        """Установка нового проекта"""
        self.mainTab.setCurrentIndex(0)
        self.mainTab.show()
        self.infoLabel.hide()

        if self.fragments_list:
            self.fragmentsWidgetLayout.removeWidget(self.fragments_list)
            self.fragments_list.deleteLater()
        self.accs = None
        self.stats = None

        self.fragments_list = FragmentsList(self)
        self.fragmentsWidgetLayout.addWidget(self.fragments_list)
        self.fragments_list.update()

        self.processor = TextProcessor()
        self.initalize_algorithms()
        self.update_enabled()
        self.edit_fragments()

    def edit_fragments(self):
        """Запустить редактирование фрагментов"""
        self.fragments = FragmentsWindow(self.processor, self)
        self.fragments.show()
        self.fragments.fragmentsChanged.connect(self.fragments_list.update)
        self.fragments.fragmentsChanged.connect(self.auto_update_results)
        self.fragments.fragmentsChanged.connect(self.update_enabled)

    def start_algorithm(self):
        """Запустить алгоритм"""
        self.thread = self.processor.PreprocessThread(self.processor)
        self.loading = LoadingWrapper(self.thread)
        self.loading.loadingDone.connect(self._continue_algorithm)
        self.loading.start()

    def _continue_algorithm(self):
        """Продолжить выполнение алгоритма"""
        # TODO Сюда впихнуть промежуточные настройки
        analyze = self.settings['processor_analyze']
        self.thread = self.processor.ProcessThread(self.processor, analyze)
        self.loading = LoadingWrapper(self.thread)
        if analyze:
            thread = self.thread
            self.loading.loadingDone.connect(
                lambda: self._set_results(thread.accs, thread.stats))
        self.loading.loadingDone.connect(self.upload_db)
        self.loading.start()

    def _set_results(self, accs=None, stats=None):
        if accs is not None:
            self.accs = accs
        if stats is not None:
            self.stats = stats
        desc = Describer(None, self.processor)
        results_html = desc.describe_results(self.accs, self.stats,
                                             all_algs=True)
        self.textBrowser.setHtml(results_html)

    def upload_db(self):
        self.thread = self.processor.analyzer.UploadDBThread(
            self.processor.analyzer)
        self.loading = LoadingWrapper(self.thread)
        self.loading.loadingDone.connect(self.auto_update_results)
        self.loading.loadingDone.connect(self.fragments_list.update)
        self.loading.start()

    def update_stats(self):
        thread = self.processor.DescribeThread(self.processor)
        thread.stats_ready.connect(
            lambda stats: self._set_results(None, stats))
        thread.run()

    def auto_update_results(self):
        [item.setEnabled(True) for item in self.en_algorithm_results]
        if self.stats is None:
            self.update_stats()
        else:
            self._set_results()
        if SupremeSettings()['result_auto_update']:
            [tab.update_results() for tab in self.tabs]

    def update_results(self):
        [item.setEnabled(True) for item in self.en_algorithm_results]
        [tab.update_results() for tab in self.tabs]

    def clear_results(self):
        self.accs = None
        self.stats = None
        self.thread = self.processor.ClearResultsThread(self.processor)
        self.loading = LoadingWrapper(self.thread)
        # В ClearResultsTread уже есть сохранение
        # self.loading.loadingDone.connect(self.upload_db)
        self.loading.start()

    def clear_db(self):
        self.thread = self.processor.analyzer.ClearDBThread(
            self.processor.analyzer)
        self.loading = LoadingWrapper(self.thread)
        self.loading.loadingDone.connect(self.remove_project)
        self.loading.start()
