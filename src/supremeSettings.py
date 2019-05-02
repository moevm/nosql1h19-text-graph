import pprint


class SupremeSettings:
    settings = {
        'vertex_size_value': 20,
        'edge_width': 2,
        'graphmodule_timer_interval': 20,
        'graphmodule_gravity_enabled': False,
        'graphmodule_gravity': 10.,
        'graphmodule_graph_scale': 500,
        'dictionary_words_num': 100,
        'dictionary_min_words': 1,
        'diff_lines': True,
        'result_auto_update': False,
        'dictionary_exclude_list': [],
        'processor_min_intersection': 0.,
        'processor_analyze': True
    }

    settings_gui = {
        'Отображение графа': {
            'vertex_size_value': 'Размер вершины',
            'edge_width': 'Ширина стрелок',
            'graphmodule_graph_scale': 'Масштабирование layout-ов',
        },
        'Расчёт гравитации': {
            'graphmodule_gravity_enabled': 'Включить гравитацию',
            'graphmodule_timer_interval': 'Частота расчёта гравитации (мс)',
            'graphmodule_gravity': 'Сила притяжения вершин к центру'
        },
        'Общие настройки анализа': {
            'processor_min_intersection': 'Минимальный вес ребра [0-1]',
            'processor_analyze': 'Провести подсчёт общих результатов'
        },
        'Алгоритм работы со словарями': {
            'dictionary_words_num': 'Сколько слов запоминать',
            'dictionary_min_words': 'Минимальная частота',
            'dictionary_exclude_list': 'Исключить слова'
        },
        'Алгоритм сравнения строк': {
            'diff_lines': 'Построчное сравнение (быстрее)'
        },
        'Основное окно': {
            'result_auto_update': 'Автоматически обновлять результаты'
        }
    }

    def __init__(self):
        self.initialise_settings()

    def check_settings(self):
        for area, settings in self.settings_gui.items():
            for setting, description in settings.items():
                try:
                    self.__getitem__(setting)
                except KeyError:
                    raise KeyError(f'Description for non-existing \
                                   setting {setting}')

    @classmethod
    def __getitem__(cls, setting_name):
        return cls.settings[setting_name]

    @classmethod
    def __setitem__(cls, key, value):
        cls.settings[key] = value

    def initialise_settings(self):
        # TODO вытащить настройки из интерфейса
        pass

    def __str__(self):
        pp = pprint.PrettyPrinter(indent=4)
        return pp.pformat(self.settings)
