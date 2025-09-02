import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import sys
from datetime import datetime

# Importa as classes das abas
from ui.segmenter_tab import SegmenterTab
from ui.cleaner_tab import CleanerTab
from ui.anonymizer_tab import AnonymizerTab
from ui.unifier_tab import UnifierTab
from ui.profiler_tab import ProfilerTab
from ui.comparer_tab import ComparerTab
from ui.visualizer_tab import VisualizerTab
from ui.etl_preparer_tab import ETLPreparerTab
from ui.dbt_assistant_tab import DBTAssistantTab # Nova Guilda

class DataToolkitApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURAÇÕES GERAIS DA JANELA ---
        self.title("Data Toolkit")
        self.geometry("1200x900") # Aumentado para a nova aba
        self.minsize(1000, 700)

        # Paleta de Cores
        self.BG_COLOR = "#1e1e2e"
        self.ALT_BG = "#181825"
        self.FG_COLOR = "#cdd6f4"
        self.ACCENT_COLOR = "#cba6f7"
        self.COMMENT_COLOR = "#6c7086"

        self.configure(background=self.BG_COLOR)
        
        self.apply_styles()
        self.create_widgets()
        self.load_icon()

    def run(self):
        self.mainloop()

    def apply_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure('.', background=self.BG_COLOR, foreground=self.FG_COLOR, borderwidth=0, lightcolor=self.BG_COLOR, darkcolor=self.BG_COLOR)
        style.configure('TFrame', background=self.BG_COLOR)
        style.configure('TLabel', background=self.BG_COLOR, foreground=self.FG_COLOR, padding=5, font=('Inter', 10))
        style.configure('TSpinbox', arrowcolor=self.FG_COLOR, fieldbackground=self.ALT_BG, background=self.ACCENT_COLOR, foreground=self.FG_COLOR, borderwidth=0)
        style.map('TSpinbox', fieldbackground=[('readonly', self.ALT_BG)])
        
        style.configure('TButton', background=self.ALT_BG, foreground=self.FG_COLOR, padding=10, relief='flat', borderwidth=0, font=('Inter', 10, 'bold'))
        style.map('TButton', background=[('active', self.COMMENT_COLOR)])
        style.configure('Accent.TButton', background=self.ACCENT_COLOR, foreground=self.BG_COLOR)
        style.map('Accent.TButton', background=[('active', self.FG_COLOR)])

        style.configure('TNotebook', background=self.BG_COLOR, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.ALT_BG, foreground=self.COMMENT_COLOR, padding=[12, 8], font=('Inter', 10, 'bold'), borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', self.BG_COLOR), ('active', self.COMMENT_COLOR)], foreground=[('selected', self.ACCENT_COLOR)])
        
        style.configure('TLabelframe', background=self.BG_COLOR, borderwidth=1, relief='solid')
        style.configure('TLabelframe.Label', background=self.BG_COLOR, foreground=self.COMMENT_COLOR, font=('Inter', 9))
        style.configure('TRadiobutton', background=self.BG_COLOR, foreground=self.FG_COLOR, indicatorcolor=self.ALT_BG, padding=5)
        style.map('TRadiobutton', indicatorcolor=[('selected', self.ACCENT_COLOR)])
        style.configure('TCheckbutton', background=self.BG_COLOR, foreground=self.FG_COLOR, indicatorcolor=self.ALT_BG, padding=5)
        style.map('TCheckbutton', indicatorcolor=[('selected', self.ACCENT_COLOR)])
        style.configure('Treeview', fieldbackground=self.ALT_BG, background=self.ALT_BG, foreground=self.FG_COLOR, rowheight=25)
        style.configure('Treeview.Heading', background=self.BG_COLOR, foreground=self.ACCENT_COLOR, font=('Inter', 10, 'bold'), relief='flat')
        style.map('Treeview.Heading', background=[('active', self.COMMENT_COLOR)])

    def create_widgets(self):
        main_container = ttk.Frame(self, padding=15)
        main_container.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(main_container, style='TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Adiciona as abas
        self.add_tab(DBTAssistantTab, "Assistente dbt")
        self.add_tab(ETLPreparerTab, "Preparador ETL")
        self.add_tab(SegmenterTab, "Segmentador")
        self.add_tab(CleanerTab, "Limpador")
        self.add_tab(AnonymizerTab, "Anonimizador")
        self.add_tab(UnifierTab, "Unificador")
        self.add_tab(ProfilerTab, "Analisador")
        self.add_tab(ComparerTab, "Comparador")
        self.add_tab(VisualizerTab, "Visualizador")
        
    def add_tab(self, TabClass, title):
        tab_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab_frame, text=title)
        TabClass(tab_frame, self)

    def load_icon(self):
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, "assets", "icon.png")
            
            original_image = Image.open(icon_path)
            resized_image = original_image.resize((256, 256), Image.Resampling.LANCZOS)
            
            self.icon_photo = ImageTk.PhotoImage(resized_image)
            self.iconphoto(True, self.icon_photo)

        except Exception as e:
            self.log(f"ERRO: Ícone não encontrado ou falha ao carregar: {e}")

    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


