class SupremeSettings:
    settings = {
        'size_value': 20,
        'vertex_weight': 250,
        'n': 100
    }

    def __init__(self):
        self.initialise_settings()

    @classmethod
    def __getitem__(cls, setting_names):
        result = {}
        for setting in setting_names:
            try:
                result[setting] = cls.settings[setting]
            except KeyError:
                # TODO KeyError Exception throw
                pass
        return result

    @classmethod
    def __setitem__(cls, key, value):
        cls.settings[key] = value

    def initialise_settings(self):
        # TODO вытащить настройки из интерфейса
        pass
