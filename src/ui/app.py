import os
import sys
import customtkinter as ctk
from PIL import Image, ImageTk
from datetime import datetime
import pandas as pd
from unidecode import unidecode

from src.core.config import ConfigManager
from src.core.logger import Logger
from src.ui import theme
from src.core.data import MUNICIPIOS_DATA


from src.tabs.profiler import ProfilerTab
from src.tabs.cleaner import CleanerTab
from src.tabs.unifier import UnifierTab
from src.tabs.etl_preparer import ETLPreparerTab
from src.tabs.geolocalizador import GeolocalizadorTab
from src.tabs.anonymizer import AnonymizerTab
from src.tabs.segmenter import SegmenterTab
from src.tabs.comparer import ComparerTab
from src.tabs.visualizer import VisualizerTab
from src.tabs.settings import SettingsTab
from src.tabs.extrator import ExtratorTab
from src.tabs.auxiliador import AuxiliadorTab

class DataToolkitApp(ctk.CTk):
    def __init__(self):
        super().__init__(className='Data-Toolkit')
        
        theme.initialize_fonts()
        self.geometry("1400x900")
        self.minsize(1400, 900)
        self.maxsize(1400, 900)
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        
        self.config_manager = ConfigManager()
        self.logger = Logger(log_level=self.config_manager.get("log_level") or "INFO")
        self.logger.info("Application starting...")
        
        self.title("Data Toolkit")
        self.tabs = {}
        self.current_tab_frame = None
        self.current_tab_button = None
        
        
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, minsize=400, weight=1)
        self.grid_columnconfigure(1, minsize=1000, weight=3)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        
        self.df_ibge = pd.DataFrame(MUNICIPIOS_DATA)
        self.df_ibge['nome_normalized'] = self.df_ibge['nome'].apply(lambda x: unidecode(str(x).lower()) if pd.notna(x) else '')
        
        self.create_widgets()
        self.load_icon()

    def create_widgets(self):
        self.configure(fg_color=theme.colors["background"])
        
        self.sidebar_frame = ctk.CTkFrame(self, width=400, corner_radius=0, fg_color=theme.colors["sidebar"])
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        tab_definitions = self.get_tab_definitions()
        self.sidebar_frame.grid_rowconfigure(len(tab_definitions) + 2, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="Data Toolkit", font=theme.fonts["title"], text_color=theme.colors["accent"]).grid(row=0, column=0, pady=(20, 10), padx=20)
        self.tab_buttons = []
        
        for idx, (TabClass, title) in enumerate(tab_definitions, start=1):
            try:
                button = ctk.CTkButton(self.sidebar_frame, text=title, font=theme.fonts["h1"], command=lambda t=title: self.select_tab(t),
                                     fg_color="transparent", text_color=theme.colors["foreground"], hover_color=theme.colors["comment"],
                                     corner_radius=theme.CORNER_RADIUS, width=350)
                button.grid(row=idx, column=0, sticky="ew", padx=25, pady=10)
                self.tab_buttons.append(button)
                
                
                tab_frame_instance = TabClass(self.content_frame, self)
                tab_frame_instance.grid(row=0, column=0, sticky="nsew", padx=theme.padding["app"] + 10, pady=theme.padding["app"] + 10)
                tab_frame_instance.grid_remove()
                self.tabs[title] = tab_frame_instance
            except Exception as e:
                print(f"ERROR initializing tab {title}: {e}")
                import traceback
                traceback.print_exc()
        
        try:
            
            assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
            logo_path = os.path.join(assets_path, "icon.png")
            if os.path.exists(logo_path):
                logo_image = ctk.CTkImage(Image.open(logo_path), size=(156, 156))
                logo_label = ctk.CTkLabel(self.sidebar_frame, image=logo_image, text="")
                logo_label.grid(row=len(tab_definitions) + 3, column=0, pady=20)
        except Exception as e:
            self.log(f"ERRO ao carregar logo da sidebar: {e}")

        if self.tab_buttons:
            first_tab_title = self.get_tab_definitions()[0][1]
            self.select_tab(first_tab_title)

    def get_tab_definitions(self):
        tab_order = [
            (ProfilerTab, "Analisador"),
            (CleanerTab, "Limpador"),
            (UnifierTab, "Unificador"),
            (ETLPreparerTab, "Preparador ETL"),
            (GeolocalizadorTab, "Geolocalizador"),
            (AnonymizerTab, "Anonimizador"),
            (SegmenterTab, "Divisor"),
            (ComparerTab, "Comparador"),
            (VisualizerTab, "Visualizador"),
            (ExtratorTab, "Extrator"),
            (AuxiliadorTab, "Auxiliador IA"),
            (SettingsTab, "Configurações")
        ]
        return tab_order

    def select_tab(self, title):
        if self.current_tab_button:
            self.current_tab_button.configure(fg_color="transparent", text_color=theme.colors["foreground"])
        if self.current_tab_frame:
            self.current_tab_frame.grid_remove()
        
        new_tab_frame = self.tabs[title]
        new_tab_frame.grid()
        self.current_tab_frame = new_tab_frame
        
        button_index = [t[1] for t in self.get_tab_definitions()].index(title)
        new_button = self.tab_buttons[button_index]
        
        self.sidebar_frame.configure(width=400)
        self.content_frame.configure(width=1000)
        new_button.configure(fg_color=theme.colors["accent"], text_color=theme.colors["background"], hover_color=theme.colors["pink"])
        self.current_tab_button = new_button

    def load_icon(self):
        try:
            assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
            icon_path = os.path.join(assets_path, "icon.png")
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
                resized_image = image.resize((256, 256), Image.Resampling.LANCZOS)
                self.icon_photo = ImageTk.PhotoImage(resized_image)
                self.iconphoto(False, self.icon_photo)
        except Exception as e:
            self.log(f"ERRO: Ícone não encontrado ou falha ao carregar: {e}")

    def log(self, message, level="info"):
        if level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "debug":
            self.logger.debug(message)
        else:
            self.logger.info(message)
