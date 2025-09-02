import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from .base_tab import BaseTab

try:
    from faker import Faker
except ImportError:
    Faker = None

import hashlib

class AnonymizerTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.faker_instance = Faker('pt_BR') if Faker else None
        self.anonymization_map = {}
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- SEÇÃO: FICHEIRO DE ORIGEM ---
        file_frame = ttk.LabelFrame(main_frame, text="Ficheiro de Origem", padding=(15, 10))
        file_frame.pack(fill='x', pady=(0, 20))
        self.btn_select_file = ttk.Button(file_frame, text="Selecionar Arquivo...", command=self.handle_file_selection)
        self.btn_select_file.pack(side="left", padx=(0, 10))
        self.lbl_filepath = ttk.Label(file_frame, text="Nenhum arquivo selecionado.")
        self.lbl_filepath.pack(side="left", fill='x', expand=True)

        # --- SEÇÃO: CONFIGURAÇÃO DA ANONIMIZAÇÃO ---
        config_frame = ttk.LabelFrame(main_frame, text="Configuração da Anonimização", padding=(15, 10))
        config_frame.pack(fill='x', pady=(0, 20))
        
        config_grid = ttk.Frame(config_frame)
        config_grid.pack(fill='both', expand=True)
        config_grid.columnconfigure(0, weight=1, minsize=200)
        config_grid.columnconfigure(1, weight=2)
        
        # Coluna da Esquerda: Seleção de Colunas e Método
        left_frame = ttk.Frame(config_grid)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        ttk.Label(left_frame, text="1. Selecione a Coluna:").pack(anchor='w', pady=(0, 5))
        self.column_var = tk.StringVar()
        self.column_combo = ttk.Combobox(left_frame, textvariable=self.column_var, state='disabled')
        self.column_combo.pack(fill='x', pady=(0, 15))

        ttk.Label(left_frame, text="2. Escolha o Método:").pack(anchor='w', pady=(0, 5))
        self.method_var = tk.StringVar(value='fake_name')
        
        methods = {
            "Nome Falso": "fake_name", "Email Falso": "fake_email", "CPF Falso": "fake_cpf",
            "Hashing (SHA256)": "hash_sha256", "Numeração Sequencial": "sequential"
        }
        for text, value in methods.items():
            ttk.Radiobutton(left_frame, text=text, variable=self.method_var, value=value).pack(anchor='w')
        
        self.btn_add_map = ttk.Button(left_frame, text="Adicionar à Fila ➔", command=self.add_to_map, state='disabled')
        self.btn_add_map.pack(fill='x', pady=(20, 0))

        # Coluna da Direita: Fila de Anonimização
        right_frame = ttk.Frame(config_grid)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))

        ttk.Label(right_frame, text="3. Fila de Anonimização:").pack(anchor='w', pady=(0,5))
        
        tree_columns = ("column", "method")
        self.tree = ttk.Treeview(right_frame, columns=tree_columns, show="headings", height=8)
        self.tree.heading("column", text="Coluna")
        self.tree.heading("method", text="Método Aplicado")
        self.tree.column("column", width=150)
        self.tree.pack(fill='both', expand=True)

        self.btn_remove_map = ttk.Button(right_frame, text="Remover Selecionado da Fila", command=self.remove_from_map, state='disabled')
        self.btn_remove_map.pack(fill='x', pady=(10,0))
        
        # --- SEÇÃO: AÇÃO ---
        action_frame = ttk.LabelFrame(main_frame, text="Ação", padding=(15, 10))
        action_frame.pack(fill='x', pady=(0, 10))
        self.btn_process = ttk.Button(action_frame, text="Processar e Salvar", command=self.processar, style='Accent.TButton', state='disabled')
        self.btn_process.pack(fill='x')

    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:
                self.column_combo['values'] = list(self.df.columns)
                self.column_combo.config(state='readonly')
                self.btn_add_map.config(state='normal')

    def add_to_map(self):
        column = self.column_var.get()
        method = self.method_var.get()
        
        if not column:
            messagebox.showwarning("Aviso", "Selecione uma coluna primeiro.")
            return

        if column in self.anonymization_map:
            messagebox.showwarning("Aviso", f"A coluna '{column}' já está na fila. Remova-a primeiro se desejar alterar o método.")
            return
            
        if "fake" in method and not self.faker_instance:
            messagebox.showerror("Erro", "A biblioteca 'Faker' é necessária para este método. Instale-a com 'pip install Faker'.")
            return

        self.anonymization_map[column] = method
        self.update_treeview()
        self.app.log(f"Coluna '{column}' adicionada à fila de anonimização com o método '{method}'.")

    def remove_from_map(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione um item na fila para remover.")
            return
        
        for item_id in selected_items:
            column_to_remove = self.tree.item(item_id)['values'][0]
            if column_to_remove in self.anonymization_map:
                del self.anonymization_map[column_to_remove]
                self.app.log(f"Coluna '{column_to_remove}' removida da fila.")
        
        self.update_treeview()

    def update_treeview(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for column, method in self.anonymization_map.items():
            self.tree.insert("", "end", values=(column, method))
            
        has_items = bool(self.anonymization_map)
        self.btn_remove_map.config(state='normal' if has_items else 'disabled')
        self.btn_process.config(state='normal' if has_items else 'disabled')

    def processar(self):
        if not self.anonymization_map or self.df is None:
            messagebox.showerror("Erro", "Configure a fila de anonimização e carregue um ficheiro primeiro.")
            return
            
        df_copy = self.df.copy()
        
        try:
            for column, method in self.anonymization_map.items():
                self.app.log(f"Aplicando '{method}' na coluna '{column}'...")
                if method == 'fake_name':
                    df_copy[column] = [self.faker_instance.name() for _ in range(len(df_copy))]
                elif method == 'fake_email':
                    df_copy[column] = [self.faker_instance.email() for _ in range(len(df_copy))]
                elif method == 'fake_cpf':
                    df_copy[column] = [self.faker_instance.cpf() for _ in range(len(df_copy))]
                elif method == 'hash_sha256':
                    df_copy[column] = df_copy[column].astype(str).apply(lambda x: hashlib.sha256(x.encode()).hexdigest())
                elif method == 'sequential':
                    df_copy[column] = [f"ID_{i+1}" for i in range(len(df_copy))]
            
            self.app.log("Anonimização concluída.")
            self.salvar_dataframe(df_copy)
        except Exception as e:
            messagebox.showerror("Erro no Processamento", f"Ocorreu um erro: {e}")
            self.app.log(f"ERRO: {e}")

