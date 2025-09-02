#1
import os
import json

#2
class ConfigManager:
    def __init__(self, app_name="DataToolkit", config_file="config.json"):
        self.app_name = app_name
        self.config_file = config_file
        self.config_path = self._get_config_path()
        self.config = self.load_config()

#3
    def _get_config_path(self):
        config_dir = os.path.join(os.path.expanduser("~"), ".config", self.app_name)
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, self.config_file)

#4
    def _get_default_config(self):
        return {
            "gemini_api_key": "",
            "csv_separator": ",",
            "dbt_project_path": "",
            "log_level": "INFO",
            # "default_import_path": "", # LINHA ANTIGA COMENTADA
            # "default_export_path": "" # LINHA ANTIGA COMENTADA
#1
            "default_import_path": "",
            "default_export_path": ""
        }

#5
    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                # Carrega a configuração existente
                config = json.load(f)
                # Verifica se as novas chaves existem, se não, adiciona-as
                default_config = self._get_default_config()
                updated = False
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                        updated = True
                if updated:
                    self.save_config(config)
                return config
        except (FileNotFoundError, json.JSONDecodeError):
            default_config = self._get_default_config()
            self.save_config(default_config)
            return default_config

#6
    def save_config(self, config_data=None):
        data_to_save = config_data if config_data is not None else self.config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)

#7
    def get(self, key):
        return self.config.get(key)

    def set(self, key, value):
        self.config[key] = value
