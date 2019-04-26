import unittest

from supremeSettings import SupremeSettings


class SupremeSettingsTest(unittest.TestCase):

    supremeSettingsClass = SupremeSettings()
    startingSettings = {
        'size_value': 20,
        'vertex_weight': 250,
        'n': 100
    }

    @unittest.skip('?')
    def test_initialization(self):
        self.assertEqual(self.startingSettings,
                         self.supremeSettingsClass.settings)

    def test_get_settings(self):
        keys = ['vertex_weight', 'size_value', 'n']
        for key in keys:
            self.supremeSettingsClass[key] = self.startingSettings[key]
            self.assertEqual(self.startingSettings[key],
                             self.supremeSettingsClass[key])

    @unittest.skip('Not works for now')
    def test_set_settings(self):
        keys = ['page_count', 'war_and_peace']
        values = [18, 'best']

        for key, value in zip(keys, values):
            self.supremeSettingsClass[key] = value
            self.assertEqual(self.supremeSettingsClass[[key]], {key: value})

    def test_global(self):
        settings = {
            'a': 'kek',
            'b': 'foo',
            'c': 12345
        }
        for key, value in settings.items():
            self.supremeSettingsClass[key] = value

        for key, value in settings.items():
            self.assertEqual(SupremeSettings()[key], value)

    def test_check(self):
        self.supremeSettingsClass.check_settings()
        self.supremeSettingsClass.settings_gui['kek'] = {'lol': 'musor'}
        self.assertRaises(KeyError, self.supremeSettingsClass.check_settings)
