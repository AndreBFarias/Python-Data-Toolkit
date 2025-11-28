import customtkinter as ctk
from tkinter import messagebox, filedialog
from src.ui.base_tab import BaseTab
from src.ui import theme
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.config import ConfigManager

class SettingsTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.config_manager = self.app.config_manager
        
        self.create_widgets()
        self.load_settings_to_ui()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)

        api_frame = ctk.CTkFrame(self, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        api_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15), padx=5)
        api_frame.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(api_frame, text="Configurações de API", font=theme.fonts["h1"]).grid(row=0, column=0, columnspan=2, sticky='w', padx=15, pady=(10,5))
        ctk.CTkLabel(api_frame, text="Chave API (Gemini):", font=theme.fonts["body"]).grid(row=1, column=0, sticky='w', padx=15, pady=(5, 15))
        self.api_key_var = ctk.StringVar()
        ctk.CTkEntry(api_frame, textvariable=self.api_key_var, show='*', fg_color=theme.colors["background"], border_color=theme.colors["comment"]).grid(row=1, column=1, sticky='ew', padx=15, pady=(5, 15))
        ctk.CTkLabel(api_frame, text="Modelo Gemini:", font=theme.fonts["body"]).grid(row=2, column=0, sticky='w', padx=15, pady=(5, 15))
        self.model_var = ctk.StringVar(value="gemini-2.5-flash")
        self.model_dropdown = ctk.CTkComboBox(api_frame, variable=self.model_var, 
                                            values=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite", "gemini-3-pro-preview"],
                                            state="readonly", width=200,
                                            fg_color=theme.colors["background"], border_color=theme.colors["comment"])
        self.model_dropdown.grid(row=2, column=1, sticky='w', padx=15, pady=(5, 15))


        path_frame = ctk.CTkFrame(self, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        path_frame.grid(row=2, column=0, sticky='ew', pady=(0, 15), padx=5)
        path_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(path_frame, text="Pastas Padrão", font=theme.fonts["h1"]).grid(row=0, column=0, columnspan=3, sticky='w', padx=15, pady=(10,5))
        
        self.import_path_var = ctk.StringVar()
        ctk.CTkLabel(path_frame, text="Pasta de Importação:", font=theme.fonts["body"]).grid(row=1, column=0, sticky='w', padx=15, pady=(5, 5))
        ctk.CTkEntry(path_frame, textvariable=self.import_path_var, state='readonly', fg_color=theme.colors["background"], border_color=theme.colors["comment"]).grid(row=1, column=1, sticky='ew', padx=10, pady=(5,5))
        ctk.CTkButton(path_frame, text="Selecionar...", font=theme.fonts["button"], width=100, command=self._select_import_path, fg_color=theme.colors["comment"]).grid(row=1, column=2, padx=(0,15), pady=(5,5))

        self.export_path_var = ctk.StringVar()
        ctk.CTkLabel(path_frame, text="Pasta de Exportação:", font=theme.fonts["body"]).grid(row=2, column=0, sticky='w', padx=15, pady=(5, 15))
        ctk.CTkEntry(path_frame, textvariable=self.export_path_var, state='readonly', fg_color=theme.colors["background"], border_color=theme.colors["comment"]).grid(row=2, column=1, sticky='ew', padx=10, pady=(5,15))
        ctk.CTkButton(path_frame, text="Selecionar...", font=theme.fonts["button"], width=100, command=self._select_export_path, fg_color=theme.colors["comment"]).grid(row=2, column=2, padx=(0,15), pady=(5,15))

        general_frame = ctk.CTkFrame(self, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        general_frame.grid(row=3, column=0, sticky='ew', pady=(0, 20), padx=5)
        general_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(general_frame, text="Configurações Gerais", font=theme.fonts["h1"]).grid(row=0, column=0, columnspan=2, sticky='w', padx=15, pady=(10,5))
        
        self.csv_separator_var = ctk.StringVar()
        ctk.CTkLabel(general_frame, text="Separador CSV:", font=theme.fonts["body"]).grid(row=1, column=0, sticky='w', padx=15, pady=(5,15))
        ctk.CTkEntry(general_frame, textvariable=self.csv_separator_var, width=50, fg_color=theme.colors["background"], border_color=theme.colors["comment"]).grid(row=1, column=1, sticky='w', padx=10, pady=(5,15))
        
        self.log_level_var = ctk.StringVar()
        ctk.CTkLabel(general_frame, text="Nível de Log:", font=theme.fonts["body"]).grid(row=2, column=0, sticky='w', padx=15, pady=(5,15))
        ctk.CTkComboBox(general_frame, variable=self.log_level_var, values=['DEBUG', 'INFO', 'WARNING', 'ERROR'], state='readonly', button_color=theme.colors["comment"], fg_color=theme.colors["background"], border_color=theme.colors["comment"]).grid(row=2, column=1, sticky='w', padx=10, pady=(5,15))

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=4, column=0, sticky='e', pady=(10, 0), padx=5)
        
        ctk.CTkButton(action_frame, text="Restaurar Padrões", font=theme.fonts["button"], command=self.restore_defaults,
                      fg_color="transparent", border_width=2, border_color=theme.colors["comment"],
                      hover_color=theme.colors["sidebar"]).pack(side='left', padx=(0, 10))
        ctk.CTkButton(action_frame, text="Salvar Alterações", font=theme.fonts["button"], command=self.save_settings,
                      fg_color=theme.colors["green"], text_color=theme.colors["background"], 
                      hover_color="#81F9A1").pack(side='left')

    def _select_import_path(self):
        path = filedialog.askdirectory(title="Selecione a pasta padrão para importação")
        if path:
            self.import_path_var.set(path)

    def _select_export_path(self):
        path = filedialog.askdirectory(title="Selecione a pasta padrão para exportação")
        if path:
            self.export_path_var.set(path)

    def load_settings_to_ui(self):
        self.api_key_var.set(self.config_manager.get("gemini_api_key"))
        self.model_var.set(self.config_manager.get("gemini_model") or "gemini-2.5-flash")
        self.import_path_var.set(self.config_manager.get("default_import_path"))
        self.export_path_var.set(self.config_manager.get("default_export_path"))
        self.csv_separator_var.set(self.config_manager.get("csv_separator"))
        self.log_level_var.set(self.config_manager.get("log_level"))

    def save_settings(self):
        self.config_manager.set("gemini_api_key", self.api_key_var.get())
        self.config_manager.set("gemini_model", self.model_var.get())
        self.config_manager.set("default_import_path", self.import_path_var.get())
        self.config_manager.set("default_export_path", self.export_path_var.get())
        self.config_manager.set("csv_separator", self.csv_separator_var.get())
        self.config_manager.set("log_level", self.log_level_var.get())
        
        self.app.config_manager.save_config()
        messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")

    def restore_defaults(self):
        default_config = self.config_manager._get_default_config()
        self.config_manager.save_config(default_config)
        self.config_manager.config = default_config
        self.load_settings_to_ui()
        messagebox.showinfo("Sucesso", "Configurações restauradas para os valores padrão.")
