import customtkinter as ctk
from PIL import Image, ImageTk
import os
import sys
from datetime import datetime

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

class DataToolkitApp(ctk.CTk):
    def __init__(self):
        super().__init__(className='Data-Toolkit')
        
        theme.initialize_fonts()
        self.title("Data Toolkit")
        self.geometry("1200x900")
        self.minsize(1000, 700)
        ctk.set_appearance_mode("dark")
        self.config_manager = ConfigManager()
        self.tabs = {}
        self.current_tab_frame = None
        self.current_tab_button = None
        self.create_widgets()
        self.load_icon()

    def run(self):
        self.mainloop()

    def create_widgets(self):
        self.configure(fg_color=theme.colors["background"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=theme.sizing["sidebar_width"], corner_radius=0, fg_color=theme.colors["sidebar"])
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        tab_definitions = self.get_tab_definitions()
        self.sidebar_frame.grid_rowconfigure(len(tab_definitions) + 2, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="Data Toolkit", font=theme.fonts["title"], text_color=theme.colors["accent"]).grid(row=0, column=0, padx=theme.padding["app"], pady=theme.padding["app"])

        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=theme.colors["background"])
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.tab_buttons = []
        tab_row = 1
        for TabClass, title in tab_definitions:
            button = ctk.CTkButton(self.sidebar_frame, text=title, command=lambda t=title: self.select_tab(t), height=theme.sizing["button_height"], corner_radius=theme.CORNER_RADIUS, fg_color="transparent", hover_color=theme.colors["comment"], text_color=theme.colors["foreground"], font=theme.fonts["button"], anchor="w")
            button.grid(row=tab_row, column=0, padx=theme.padding["widget_x"], pady=theme.padding["widget_y"], sticky="ew")
            self.tab_buttons.append(button)
            tab_frame_instance = TabClass(self.content_frame, self)
            tab_frame_instance.grid(row=0, column=0, sticky="nsew", padx=theme.padding["app"], pady=theme.padding["app"])
            tab_frame_instance.grid_remove()
            self.tabs[title] = tab_frame_instance
            tab_row += 1
        
        try:
            logo_image = ctk.CTkImage(Image.open("assets/icon.png"), size=(64, 64))
            logo_label = ctk.CTkLabel(self.sidebar_frame, image=logo_image, text="")
            logo_label.grid(row=len(tab_definitions) + 3, column=0, pady=20)
        except Exception as e:
            self.log(f"ERRO ao carregar logo da sidebar: {e}")

        if self.tab_buttons:
            first_tab_title = self.get_tab_definitions()[0][1]
            self.select_tab(first_tab_title)

    def get_tab_definitions(self):
        return [(DBTAssistantTab, "Assistente dbt"), (ETLPreparerTab, "Preparador ETL"), (SegmenterTab, "Divisor"), (CleanerTab, "Limpador"), (AnonymizerTab, "Anonimizador"), (UnifierTab, "Unificador"), (ProfilerTab, "Analisador"), (ComparerTab, "Comparador"), (VisualizerTab, "Visualizador"), (SettingsTab, "Configurações")]

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
