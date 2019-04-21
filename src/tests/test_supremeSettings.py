import unittest

from supremeSettings import SupremeSettings


class SupremeSettingsTest(unittest.TestCase):

    supremeSettingsClass = SupremeSettings()
    startingSettings = {
        'size_value': 20,
        'vertex_weight': 250,
        'n': 100
    }

    def test_initialization(self):
        self.assertEqual(self.startingSettings, self.supremeSettingsClass.settings)

    def test_get_settings(self):
        keys = ['vertex_weight', 'size_value', 'n']
        self.assertEqual(self.startingSettings, self.supremeSettingsClass[keys])

    def test_set_settings(self):
        keys = ['page_count', 'war_and_peace']
        values = [18, 'best']

        for key, value in zip(keys, values):
            self.supremeSettingsClass[key] = value
            self.assertEqual(self.supremeSettingsClass[[key]], {key: value})
