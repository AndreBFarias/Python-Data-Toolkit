import os
import json

class ConfigManager:
    def __init__(self, app_name="DataToolkit", config_file="config.json"):
        self.app_name = app_name
        self.config_file = config_file
        self.config_path = self._get_config_path()
        self.config = self.load_config()

    def _get_config_path(self):
        config_dir = os.path.join(os.path.expanduser("~"), ".config", self.app_name)
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, self.config_file)

    def _get_default_config(self):
        return {
            "gemini_api_key": "",
            "csv_separator": ",",
            "dbt_project_path": "",
            "log_level": "INFO"
        }

    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            default_config = self._get_default_config()
            self.save_config(default_config)
            return default_config

    def save_config(self, config_data=None):
        data_to_save = config_data if config_data is not None else self.config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)

    def get(self, key):
        return self.config.get(key)

    def set(self, key, value):
        self.config[key] = value
