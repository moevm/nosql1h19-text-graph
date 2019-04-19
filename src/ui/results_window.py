from PyQt5.QtWidgets import QMainWindow

from api import TextProcessor
from ui_compiled.mainwindow import Ui_MainWindow
from .fragments_window import FragmentsWindow
from ui.widgets import FragmentsList


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.actionCloseProject.triggered.connect(self.removeProject)
        self.actionNew.triggered.connect(self.setNewProject)
        self.actionChangeFragments.triggered.connect(self.editFragments)

        self.en_project = [  # Включить, когда есть проект
            self.actionCloseProject,
            # self.actionSave,
            self.actionChangeFragments,
            self.actionClear
        ]

        self.en_algorithm_results = [  # Включить, когда есть результаты
            self.dictIntersectTab,
            self.namesIntersectTab
        ]

        self.en_process_fragments = [  # Включить, когда загружены фрагменты
            self.actionStartProcess,
            self.actionClear,
            self.startProcessButton,
        ]

        self.processor = None  # Обработчик текста
        self.fragments_list = None  # Виджет с фрагментами

        self.removeProject()

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
        self.updateEnabled()
        self.editFragments()

    def editFragments(self):
        self.fragments = FragmentsWindow(self.processor)
        self.fragments.show()
        self.fragments.fragmentsChanged.connect(self.fragments_list.update)
