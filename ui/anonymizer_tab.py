import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from .base_tab import BaseTab
from ui import theme

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
        self.style_treeview()

    def create_widgets(self):
        # --- Layout ---
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

#4
        # --- SEÇÃO: ARQUIVO DE ORIGEM ---
        file_frame = ctk.CTkFrame(self, fg_color=theme.colors["sidebar"])
        file_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
#4
        self.btn_select_file = ctk.CTkButton(file_frame, text="Selecionar Arquivo...", font=theme.fonts["button"], command=self.handle_file_selection, fg_color=theme.colors["comment"])
        self.btn_select_file.grid(row=0, column=0, padx=15, pady=15)
#4
        self.lbl_filepath = ctk.CTkLabel(file_frame, text="Nenhum arquivo selecionado.", font=theme.fonts["body"], text_color=theme.colors["comment"])
        self.lbl_filepath.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        # --- SEÇÃO: CONFIGURAÇÃO ---
        config_frame = ctk.CTkFrame(self, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        config_frame.grid(row=1, column=0, sticky='nsew', padx=5)
        config_frame.columnconfigure(0, weight=1, minsize=250)
        config_frame.columnconfigure(1, weight=2)
        config_frame.rowconfigure(0, weight=1)
        
        # --- COLUNA ESQUERDA ---
        left_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky='nsew', padx=15, pady=15)
        
        ctk.CTkLabel(left_frame, text="1. Selecione a Coluna:", font=theme.fonts["body"]).pack(anchor='w', pady=(0, 5))
        self.column_var = ctk.StringVar()
        self.column_combo = ctk.CTkComboBox(left_frame, variable=self.column_var, state='disabled', button_color=theme.colors["comment"], fg_color=theme.colors["background"], border_color=theme.colors["comment"])
        self.column_combo.pack(fill='x', pady=(0, 15))

        ctk.CTkLabel(left_frame, text="2. Escolha o Método:", font=theme.fonts["body"]).pack(anchor='w', pady=(0, 5))
        self.method_var = ctk.StringVar(value='fake_name')
        
        methods = {"Nome Falso": "fake_name", "Email Falso": "fake_email", "CPF Falso": "fake_cpf", "Hashing (SHA256)": "hash_sha256", "Numeração Sequencial": "sequential"}
        for text, value in methods.items():
            ctk.CTkRadioButton(left_frame, text=text, variable=self.method_var, value=value, font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"]).pack(anchor='w', pady=3)
        
        self.btn_add_map = ctk.CTkButton(left_frame, text="Adicionar à Fila ➔", font=theme.fonts["button"], command=self.add_to_map, state='disabled', fg_color=theme.colors["comment"])
        self.btn_add_map.pack(fill='x', pady=(20, 0))

        # --- COLUNA DIREITA ---
        right_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky='nsew', padx=15, pady=15)
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(right_frame, text="3. Fila de Anonimização:", font=theme.fonts["body"]).grid(row=0, column=0, sticky='w', pady=(0,5))
        
        tree_frame = ctk.CTkFrame(right_frame, fg_color=theme.colors["background"])
        tree_frame.grid(row=1, column=0, sticky='nsew')
        tree_columns = ("column", "method")
        self.tree = ttk.Treeview(tree_frame, columns=tree_columns, show="headings", height=8)
        self.tree.heading("column", text="Coluna")
        self.tree.heading("method", text="Método Aplicado")
        self.tree.column("column", width=150)
        self.tree.pack(fill='both', expand=True, padx=1, pady=1)

        self.btn_remove_map = ctk.CTkButton(right_frame, text="Remover Selecionado da Fila", font=theme.fonts["button"], command=self.remove_from_map, state='disabled', fg_color="transparent", border_width=1, border_color=theme.colors["comment"])
        self.btn_remove_map.grid(row=2, column=0, sticky='ew', pady=(10,0))
        
        # --- AÇÃO ---
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=15)
        action_frame.columnconfigure(0, weight=1)
        self.btn_process = ctk.CTkButton(action_frame, text="Processar e Salvar", command=self.processar, font=theme.fonts["button"], state='disabled', fg_color=theme.colors["green"], text_color=theme.colors["background"], hover_color="#81F9A1")
        self.btn_process.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=theme.colors["background"], foreground=theme.colors["foreground"], fieldbackground=theme.colors["background"], rowheight=25, borderwidth=0)
        style.map("Treeview", background=[('selected', theme.colors["accent"])])
        style.configure("Treeview.Heading", background=theme.colors["sidebar"], foreground=theme.colors["accent"], font=theme.fonts["button"], relief="flat", borderwidth=0)
        style.map("Treeview.Heading", background=[('active', theme.colors["comment"])])

    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:
                self.column_combo.configure(values=list(self.df.columns), state='readonly')
                self.btn_add_map.configure(state='normal')

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
        self.btn_remove_map.configure(state='normal' if has_items else 'disabled')
        self.btn_process.configure(state='normal' if has_items else 'disabled')

    def processar(self):
        if not self.anonymization_map or self.df is None:
#4
            messagebox.showerror("Erro", "Configure a fila de anonimização e carregue um arquivo primeiro.")
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
