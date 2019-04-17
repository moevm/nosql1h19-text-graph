class SupremeSettings:
    settings = {
        'size_value': 20,
        'vertex_weight': 250,
        'n': 100
    }

    def __init__(self):
        self.initialise_settings()

    def get_settings(self, setting_names):
        result = {}
        for setting in setting_names:
            if setting in self.settings.keys():
                result[setting] = self.settings[setting]
        return result

    def initialise_settings(self):
        """TODO вытащить настройки из интерфейса"""
        pass
