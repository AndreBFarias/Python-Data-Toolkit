import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from .base_tab import BaseTab

class CleanerTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- SEÇÃO: FICHEIRO DE ORIGEM ---
        file_frame = ttk.LabelFrame(main_frame, text="Ficheiro de Origem", padding=(15, 10))
        file_frame.pack(fill='x', pady=(0, 20))

        self.btn_select_file = ttk.Button(file_frame, text="Selecionar Arquivo para Limpeza...", command=self.handle_file_selection)
        self.btn_select_file.pack(side="left", padx=(0, 10))
        self.lbl_filepath = ttk.Label(file_frame, text="Nenhum arquivo selecionado.")
        self.lbl_filepath.pack(side="left", fill='x', expand=True)

        # --- SEÇÃO: OPERAÇÕES DE LIMPEZA ---
        ops_frame = ttk.LabelFrame(main_frame, text="Operações de Limpeza", padding=(15, 10))
        ops_frame.pack(fill='both', expand=True, pady=(0, 20))
        ops_frame.columnconfigure(0, weight=1)
        ops_frame.columnconfigure(1, weight=2)

        # Ações Gerais (na esquerda)
        general_ops_frame = ttk.Frame(ops_frame)
        general_ops_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 20))
        
        ttk.Label(general_ops_frame, text="Ações Gerais (aplicadas a todo o ficheiro):", font=('Inter', 10, 'bold')).pack(anchor='w', pady=(0,10))

        self.remove_duplicates_var = tk.BooleanVar()
        ttk.Checkbutton(general_ops_frame, text="Remover linhas duplicadas", variable=self.remove_duplicates_var).pack(anchor='w', pady=2)

        self.remove_empty_rows_var = tk.BooleanVar()
        ttk.Checkbutton(general_ops_frame, text="Remover linhas totalmente vazias", variable=self.remove_empty_rows_var).pack(anchor='w', pady=2)
        
        self.strip_whitespace_var = tk.BooleanVar()
        ttk.Checkbutton(general_ops_frame, text="Remover espaços em branco (início/fim das células)", variable=self.strip_whitespace_var).pack(anchor='w', pady=2)

        # Ações Específicas (na direita)
        specific_ops_frame = ttk.Frame(ops_frame)
        specific_ops_frame.grid(row=0, column=1, sticky='nsew')
        
        ttk.Label(specific_ops_frame, text="Ações Específicas (aplicadas a uma coluna):", font=('Inter', 10, 'bold')).pack(anchor='w', pady=(0,10))
        
        self.col_var = tk.StringVar()
        self.col_combo = ttk.Combobox(specific_ops_frame, textvariable=self.col_var, state='disabled', postcommand=self.update_column_list)
        self.col_combo.pack(fill='x', pady=(0, 15))

        # Capitalização
        case_frame = ttk.Frame(specific_ops_frame)
        case_frame.pack(fill='x', pady=(0,10))
        ttk.Label(case_frame, text="Alterar Capitalização:").pack(side='left', anchor='w', padx=(0,10))
        self.case_var = tk.StringVar(value="none")
        cases = {"Nenhum": "none", "MAIÚSCULAS": "upper", "minúsculas": "lower", "Título": "title"}
        for text, value in cases.items():
            ttk.Radiobutton(case_frame, text=text, variable=self.case_var, value=value).pack(side='left', padx=3)

        # Substituição
        replace_frame = ttk.Frame(specific_ops_frame)
        replace_frame.pack(fill='x', pady=(0,10))
        ttk.Label(replace_frame, text="Substituir Texto:").pack(anchor='w')
        
        find_frame = ttk.Frame(replace_frame)
        find_frame.pack(fill='x', pady=2)
        ttk.Label(find_frame, text="Localizar:", width=10).pack(side='left')
        self.find_var = tk.StringVar()
        ttk.Entry(find_frame, textvariable=self.find_var).pack(side='left', fill='x', expand=True)

        replace_with_frame = ttk.Frame(replace_frame)
        replace_with_frame.pack(fill='x', pady=2)
        ttk.Label(replace_with_frame, text="Substituir por:", width=10).pack(side='left')
        self.replace_var = tk.StringVar()
        ttk.Entry(replace_with_frame, textvariable=self.replace_var).pack(side='left', fill='x', expand=True)

        # --- SEÇÃO: AÇÃO ---
        action_frame = ttk.LabelFrame(main_frame, text="Ação", padding=(15, 10))
        action_frame.pack(fill='x', pady=(0, 10))
        
        self.btn_process = ttk.Button(action_frame, text="Aplicar Limpeza e Salvar Como...", command=self.processar, style='Accent.TButton', state='disabled')
        self.btn_process.pack(fill='x')

    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:
                self.btn_process.config(state='normal')
                self.col_combo.config(state='readonly')

    def update_column_list(self):
        if self.df is not None:
            self.col_combo['values'] = list(self.df.columns)

    def processar(self):
        if self.df is None:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")
            return
        
        df_clean = self.df.copy()
        self.app.log("Iniciando processo de limpeza...")

        # Ações Gerais
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

        # Ações Específicas
        selected_col = self.col_var.get()
        if selected_col:
            # Capitalização
            case_action = self.case_var.get()
            if case_action != "none":
                if pd.api.types.is_string_dtype(df_clean[selected_col]):
                    if case_action == 'upper': df_clean[selected_col] = df_clean[selected_col].str.upper()
                    elif case_action == 'lower': df_clean[selected_col] = df_clean[selected_col].str.lower()
                    elif case_action == 'title': df_clean[selected_col] = df_clean[selected_col].str.title()
                    self.app.log(f"Capitalização '{case_action}' aplicada à coluna '{selected_col}'.")
                else:
                     self.app.log(f"Aviso: Ação de capitalização só pode ser aplicada a colunas de texto. '{selected_col}' não foi alterada.")
            
            # Substituição
            find_text = self.find_var.get()
            if find_text:
                replace_text = self.replace_var.get()
                if pd.api.types.is_string_dtype(df_clean[selected_col]):
                    count = df_clean[selected_col].str.contains(find_text).sum()
                    df_clean[selected_col] = df_clean[selected_col].str.replace(find_text, replace_text, regex=False)
                    self.app.log(f"Substituição realizada em {count} células da coluna '{selected_col}'.")
                else:
                    self.app.log(f"Aviso: Ação de substituição só pode ser aplicada a colunas de texto. '{selected_col}' não foi alterada.")

        self.app.log("Limpeza concluída.")
        if self.salvar_dataframe(df_clean):
            messagebox.showinfo("Sucesso", "Arquivo limpo salvo com sucesso!")

