import unittest
import pandas as pd
from unidecode import unidecode
from ui.integrator_tab import IntegratorTab

class TestIntegratorTab(unittest.TestCase):
    def setUp(self):
        # Simula um app_instance básico
        class MockApp:
            def __init__(self):
                self.config_manager = MockConfigManager()
                self.df_ibge = pd.DataFrame({
                    'nome': ['São Paulo', 'Rio de Janeiro'],
                    'nome_normalized': ['sao paulo', 'rio de janeiro'],
                    'sigla_uf': ['SP', 'RJ']
                })
            def log(self, message):
                pass

        class MockConfigManager:
            def get(self, key):
                return ',' if key == 'csv_separator' else None

        self.app = MockApp()
        self.tab = IntegratorTab(None, self.app)
        self.tab.user_df = pd.DataFrame({'cidade': ['São paulo', 'rio De Janeiro']})

    def test_enrich_data_success(self):
        self.tab.column_combo = MockComboBox('cidade')
        self.tab.enrich_data()
        self.assertIsNotNone(self.tab.result_df)
        self.assertEqual(len(self.tab.result_df), 2)
        self.assertIn('sigla_uf', self.tab.result_df.columns)

    def test_enrich_data_no_column(self):
        self.tab.column_combo = MockComboBox('')
        with self.assertRaises(messagebox.showwarning):
            self.tab.enrich_data()
        self.assertIsNone(self.tab.result_df)

class MockComboBox:
    def __init__(self, value):
        self._value = value
    def get(self):
        return self._value

if __name__ == '__main__':
    unittest.main()