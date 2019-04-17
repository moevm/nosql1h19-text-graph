class SupremeSettings:
    settings = {
        'size_value': 20,
        'vertex_weight': 250,
        'n': 100
    }

    def __init__(self):
        self.initialise_settings()

    @staticmethod
    def get_settings(setting_names):
        result = {}
        for setting in setting_names:
            try:
                result[setting] = SupremeSettings.settings[setting]
            except KeyError:
                # TODO KeyError Exception throw
                pass
        return result

    @staticmethod
    def set_settings(settings_tuples):
        for pair in settings_tuples:
            SupremeSettings.settings[pair[0]] = pair[1]

    def initialise_settings(self):
        # TODO вытащить настройки из интерфейса
        pass
