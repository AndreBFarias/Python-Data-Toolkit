# data_toolkit.py
import os
import sys
sys.path.insert(0, os.path.abspath('ui'))
import customtkinter as ctk
from PIL import Image, ImageTk
from datetime import datetime
import pandas as pd
from unidecode import unidecode

from config_manager import ConfigManager
from ui import theme
from ui.dbt_assistant_tab import DBTAssistantTab
from ui.etl_preparer_tab import ETLPreparerTab
from ui.segmenter_tab import SegmenterTab
from ui.cleaner_tab import CleanerTab
from ui.anonymizer_tab import AnonymizerTab
from ui.unifier_tab import UnifierTab
from ui.profiler_tab import ProfilerTab
from ui.comparer_tab import ComparerTab
from ui.visualizer_tab import VisualizerTab
from ui.settings_tab import SettingsTab
from ui.geolocalizador_tab import GeolocalizadorTab
from ui.anonymizer_tab import *
from ui.base_tab import *
from ui.cleaner_tab import *
from ui.comparer_tab import *
from ui.custom_widgets import *
from ui.dbt_assistant_tab import *
from ui.etl_preparer_tab import *
from ui.profiler_tab import *
from ui.segmenter_tab import *
from ui.unifier_tab import *
from ui.visualizer_tab import *

class DataToolkitApp(ctk.CTk):
    def __init__(self):
        super().__init__(className='Data-Toolkit')
        
        theme.initialize_fonts()
        self.title("Data Toolkit")
        self.geometry("1400x900")  # Tamanho fixo aumentado
        self.minsize(1400, 900)    # Mínimo igual ao fixo
        self.maxsize(1400, 900)    # Máximo igual ao fixo
        self.resizable(False, False)  # Desativar redimensionamento
        ctk.set_appearance_mode("dark")
        self.config_manager = ConfigManager()
        self.tabs = {}
        self.current_tab_frame = None
        self.current_tab_button = None
        
        # Adicionar frame principal para as abas
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, minsize=400, weight=1)  # Sidebar fixa em 400 pixels
        self.grid_columnconfigure(1, minsize=1000, weight=3)  # Content frame com largura mínima
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Pre-carregar DataFrame IBGE
        ibge_path = os.path.join(os.path.dirname(__file__), "dicionario-municipios.csv")
        self.df_ibge = pd.read_csv(ibge_path)
        self.df_ibge['nome_normalized'] = self.df_ibge['nome'].apply(lambda x: unidecode(str(x).lower()) if pd.notna(x) else '')
        
        self.create_widgets()
        self.load_icon()

    def run(self):
        self.mainloop()

    def create_widgets(self):
        self.configure(fg_color=theme.colors["background"])
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=400, corner_radius=0, fg_color=theme.colors["sidebar"])
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        tab_definitions = self.get_tab_definitions()
        self.sidebar_frame.grid_rowconfigure(len(tab_definitions) + 2, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="Data Toolkit", font=theme.fonts["title"], text_color=theme.colors["accent"]).grid(row=0, column=0, pady=(20, 10), padx=20)
        self.tab_buttons = []
        
        for idx, (TabClass, title) in enumerate(tab_definitions, start=1):
            button = ctk.CTkButton(self.sidebar_frame, text=title, font=theme.fonts["h1"], command=lambda t=title: self.select_tab(t),
                                 fg_color="transparent", text_color=theme.colors["foreground"], hover_color=theme.colors["comment"],
                                 corner_radius=theme.CORNER_RADIUS, width=350)  # Largura dos botões mantida
            button.grid(row=idx, column=0, sticky="ew", padx=25, pady=10)
            self.tab_buttons.append(button)
            tab_frame_instance = TabClass(self.content_frame, self)
            tab_frame_instance.grid(row=0, column=0, sticky="nsew", padx=theme.padding["app"] + 10, pady=theme.padding["app"] + 10)
            tab_frame_instance.grid_remove()
            self.tabs[title] = tab_frame_instance
        
        try:
            logo_image = ctk.CTkImage(Image.open("assets/icon.png"), size=(156, 156))
            logo_label = ctk.CTkLabel(self.sidebar_frame, image=logo_image, text="")
            logo_label.grid(row=len(tab_definitions) + 3, column=0, pady=20)
        except Exception as e:
            self.log(f"ERRO ao carregar logo da sidebar: {e}")

        if self.tab_buttons:
            first_tab_title = self.get_tab_definitions()[0][1]
            self.select_tab(first_tab_title)

#2
    def get_tab_definitions(self):
        # Ordem lógica de fluxo de trabalho
        tab_order = [
            (ProfilerTab, "Analisador"),       # 1. Veja o que você tem
            (CleanerTab, "Limpador"),          # 2. Limpe os dados
            (UnifierTab, "Unificador"),        # 3. Junte várias fontes
            (ETLPreparerTab, "Preparador ETL"),  # 4. Prepare Schemas
            (GeolocalizadorTab, "Geolocalizador"), # 5. Enriqueça
            (AnonymizerTab, "Anonimizador"),   # 6. Proteja dados sensíveis
            (SegmenterTab, "Divisor"),         # 7. Quebre para entrega
            (ComparerTab, "Comparador"),       # 8. Compare versões
            (VisualizerTab, "Visualizador"),   # 9. Gere gráficos
            (DBTAssistantTab, "Assistente dbt"), # 10. Ferramenta específica
            (SettingsTab, "Configurações")     # 11. Sempre por último
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
        # Garantir largura fixa e proporção consistente
        self.sidebar_frame.configure(width=400)  # Forçar largura fixa da sidebar
        self.content_frame.configure(width=1000)  # Ajustar largura fixa do content_frame
        new_button.configure(fg_color=theme.colors["accent"], text_color=theme.colors["background"], hover_color=theme.colors["pink"])
        self.current_tab_button = new_button

    def load_icon(self):
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, "assets", "icon.png")
            image = Image.open(icon_path)
            resized_image = image.resize((256, 256), Image.Resampling.LANCZOS)
            self.icon_photo = ImageTk.PhotoImage(resized_image)
            self.iconphoto(False, self.icon_photo)
        except Exception as e:
            self.log(f"ERRO: Ícone não encontrado ou falha ao carregar: {e}")

    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

if __name__ == "__main__":
    # Garante que o diretório de trabalho seja o do script
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    app = DataToolkitApp()
    app.run() # O comando correto, dirigido ao maestro.
