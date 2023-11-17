import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
from .base_tab import BaseTab
from ui import theme

class CleanerTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        file_frame = ctk.CTkFrame(self, fg_color=theme.colors["sidebar"])
        file_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)

        self.btn_select_file = ctk.CTkButton(file_frame, text="Selecionar Arquivo para Limpeza...", font=theme.fonts["button"], command=self.handle_file_selection, fg_color=theme.colors["comment"])
        self.btn_select_file.grid(row=0, column=0, padx=15, pady=15)
        self.lbl_filepath = ctk.CTkLabel(file_frame, text="Nenhum arquivo selecionado.", font=theme.fonts["body"], text_color=theme.colors["comment"])
        self.lbl_filepath.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        ops_frame = ctk.CTkFrame(self, fg_color="transparent")
        ops_frame.grid(row=1, column=0, sticky='nsew', padx=5)
        ops_frame.columnconfigure(0, weight=1)
        ops_frame.columnconfigure(1, weight=2)
        
        general_ops_frame = ctk.CTkFrame(ops_frame, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        general_ops_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        ctk.CTkLabel(general_ops_frame, text="Ações Gerais", font=theme.fonts["h1"]).pack(anchor='w', padx=15, pady=(15, 10))
        self.remove_duplicates_var = ctk.BooleanVar()
        ctk.CTkCheckBox(general_ops_frame, text="Remover linhas duplicadas", variable=self.remove_duplicates_var, font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"]).pack(anchor='w', padx=20, pady=5)
        self.remove_empty_rows_var = ctk.BooleanVar()
        ctk.CTkCheckBox(general_ops_frame, text="Remover linhas totalmente vazias", variable=self.remove_empty_rows_var, font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"]).pack(anchor='w', padx=20, pady=5)
        self.strip_whitespace_var = ctk.BooleanVar()
        ctk.CTkCheckBox(general_ops_frame, text="Remover espaços (início/fim das células)", variable=self.strip_whitespace_var, font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"]).pack(anchor='w', padx=20, pady=(5, 20))

        specific_ops_frame = ctk.CTkFrame(ops_frame, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        specific_ops_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        specific_ops_frame.columnconfigure(0, weight=1)
        
        ctk.CTkLabel(specific_ops_frame, text="Ações Específicas por Coluna", font=theme.fonts["h1"]).grid(row=0, column=0, columnspan=2, sticky='w', padx=15, pady=(15, 10))
        
        self.col_var = ctk.StringVar()
        self.col_combo = ctk.CTkComboBox(specific_ops_frame, variable=self.col_var, state='disabled', command=self.update_column_list, button_color=theme.colors["comment"], fg_color=theme.colors["background"], border_color=theme.colors["comment"])
        self.col_combo.grid(row=1, column=0, columnspan=2, sticky='ew', padx=15, pady=(10, 15))

        case_frame = ctk.CTkFrame(specific_ops_frame, fg_color="transparent")
        case_frame.grid(row=2, column=0, columnspan=2, sticky='w', padx=15, pady=5)
        ctk.CTkLabel(case_frame, text="Capitalização:", font=theme.fonts["body"]).pack(side='left', anchor='w', padx=(0,10))
        self.case_var = ctk.StringVar(value="none")
        cases = {"Nenhum": "none", "MAIÚSCULAS": "upper", "minúsculas": "lower", "Título": "title"}
        for text, value in cases.items():
            ctk.CTkRadioButton(case_frame, text=text, variable=self.case_var, value=value, font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"]).pack(side='left', padx=5)

        replace_frame = ctk.CTkFrame(specific_ops_frame, fg_color="transparent")
        replace_frame.grid(row=3, column=0, columnspan=2, sticky='ew', padx=15, pady=(10, 20))
        replace_frame.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(replace_frame, text="Localizar:", font=theme.fonts["body"], width=10).grid(row=0, column=0, sticky='w')
        self.find_var = ctk.StringVar()
        ctk.CTkEntry(replace_frame, textvariable=self.find_var, fg_color=theme.colors["background"], border_color=theme.colors["comment"]).grid(row=0, column=1, sticky='ew', padx=(10,0))

        ctk.CTkLabel(replace_frame, text="Substituir por:", font=theme.fonts["body"], width=10).grid(row=1, column=0, sticky='w', pady=(10,0))
        self.replace_var = ctk.StringVar()
        ctk.CTkEntry(replace_frame, textvariable=self.replace_var, fg_color=theme.colors["background"], border_color=theme.colors["comment"]).grid(row=1, column=1, sticky='ew', padx=(10,0), pady=(10,0))

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=15)
        action_frame.columnconfigure(0, weight=1)
        
        self.btn_process = ctk.CTkButton(action_frame, text="Aplicar Limpeza e Salvar Como...", font=theme.fonts["button"], command=self.processar, state='disabled', fg_color=theme.colors["green"], text_color=theme.colors["background"], hover_color="#81F9A1")
        self.btn_process.grid(row=0, column=0, sticky="ew")

    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:
                self.btn_process.configure(state='normal')
                self.col_combo.configure(state='readonly')
                self.update_column_list(None)

    def update_column_list(self, choice):
        if self.df is not None:
            self.col_combo.configure(values=list(self.df.columns))

    def processar(self):
        if self.df is None:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")
            return
        df_clean = self.df.copy()
        self.app.log("Iniciando processo de limpeza...")
        if self.remove_duplicates_var.get():
            before = len(df_clean)
            df_clean.drop_duplicates(inplace=True)
            after = len(df_clean)
            self.app.log(f"Removidas {before - after} linhas duplicadas.")
        if self.remove_empty_rows_var.get():
            before = len(df_clean)
            df_clean.dropna(how='all', inplace=True)
            after = len(df_clean)
            self.app.log(f"Removidas {before - after} linhas vazias.")
        if self.strip_whitespace_var.get():
            for col in df_clean.select_dtypes(include=['object']).columns:
                df_clean[col] = df_clean[col].str.strip()
            self.app.log("Espaços em branco removidos do início/fim das células de texto.")
        selected_col = self.col_var.get()
        if selected_col:
            case_action = self.case_var.get()
            if case_action != "none":
                if pd.api.types.is_string_dtype(df_clean[selected_col]):
                    if case_action == 'upper': df_clean[selected_col] = df_clean[selected_col].str.upper()
                    elif case_action == 'lower': df_clean[selected_col] = df_clean[selected_col].str.lower()
                    elif case_action == 'title': df_clean[selected_col] = df_clean[selected_col].str.title()
                    self.app.log(f"Capitalização '{case_action}' aplicada à coluna '{selected_col}'.")
                else:
                     self.app.log(f"Aviso: Ação de capitalização só pode ser aplicada a colunas de texto. '{selected_col}' não foi alterada.")
            find_text = self.find_var.get()
            if find_text:
                replace_text = self.replace_var.get()
                if pd.api.types.is_string_dtype(df_clean[selected_col]):
                    count = df_clean[selected_col].str.contains(find_text, na=False).sum()
                    df_clean[selected_col] = df_clean[selected_col].str.replace(find_text, replace_text, regex=False)
                    self.app.log(f"Substituição realizada em {count} células da coluna '{selected_col}'.")
                else:
                    self.app.log(f"Aviso: Ação de substituição só pode ser aplicada a colunas de texto. '{selected_col}' não foi alterada.")
        self.app.log("Limpeza concluída.")
        self.salvar_dataframe(df_clean)
