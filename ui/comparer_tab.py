import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from .base_tab import BaseTab

class ComparerTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.df1 = None
        self.df2 = None
        self.filepath1 = None
        self.filepath2 = None
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Container para os seletores de ficheiro (usará grid internamente)
        top_files_frame = ttk.Frame(main_frame)
        top_files_frame.pack(fill='x', pady=(0, 20))
        top_files_frame.columnconfigure(0, weight=1)
        top_files_frame.columnconfigure(1, weight=1)

        # --- SEÇÃO: SELEÇÃO DE FICHEIROS ---
        file1_frame = ttk.LabelFrame(top_files_frame, text="Ficheiro Antigo (Base)", padding=(15, 10))
        file1_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        self.btn_select_file1 = ttk.Button(file1_frame, text="Selecionar Arquivo 1...", command=self.handle_file1_selection)
        self.btn_select_file1.pack(side="left", padx=(0, 10))
        self.lbl_filepath1 = ttk.Label(file1_frame, text="Nenhum arquivo.")
        self.lbl_filepath1.pack(side="left", fill='x', expand=True)

        file2_frame = ttk.LabelFrame(top_files_frame, text="Ficheiro Novo (Comparação)", padding=(15, 10))
        file2_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        self.btn_select_file2 = ttk.Button(file2_frame, text="Selecionar Arquivo 2...", command=self.handle_file2_selection)
        self.btn_select_file2.pack(side="left", padx=(0, 10))
        self.lbl_filepath2 = ttk.Label(file2_frame, text="Nenhum arquivo.")
        self.lbl_filepath2.pack(side="left", fill='x', expand=True)

        # --- SEÇÃO: CONFIGURAÇÃO ---
        config_frame = ttk.LabelFrame(main_frame, text="Configuração da Comparação", padding=(15, 10))
        config_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(config_frame, text="Selecione a(s) coluna(s) chave para identificação das linhas (Ex: ID, CPF):").pack(anchor='w', pady=(0,5))
        
        self.key_listbox = tk.Listbox(config_frame, selectmode=tk.MULTIPLE, height=5, exportselection=False,
                                       background=self.app.ALT_BG, foreground=self.app.FG_COLOR, 
                                       selectbackground=self.app.ACCENT_COLOR, relief='flat', borderwidth=0)
        self.key_listbox.pack(fill='x', expand=True)
        
        # --- SEÇÃO: AÇÃO ---
        action_frame = ttk.LabelFrame(main_frame, text="Ação", padding=(15, 10))
        action_frame.pack(fill='x')
        self.btn_process = ttk.Button(action_frame, text="Comparar Arquivos", command=self.processar, style='Accent.TButton', state='disabled')
        self.btn_process.pack(fill='x')

        # --- SEÇÃO: RESULTADOS ---
        self.results_frame = ttk.Frame(main_frame)
        self.results_frame.pack(fill='both', expand=True, pady=(20, 0))
        self.results_frame.rowconfigure(0, weight=1)
        self.results_frame.columnconfigure(0, weight=1)

    def handle_file1_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath1, target_path_attr='filepath1'):
            self.df1 = self.carregar_dataframe(self.filepath1)
            self.update_key_columns()

    def handle_file2_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath2, target_path_attr='filepath2'):
            self.df2 = self.carregar_dataframe(self.filepath2)
            self.update_key_columns()

    def update_key_columns(self):
        self.key_listbox.delete(0, tk.END)
        if self.df1 is not None and self.df2 is not None:
            common_columns = sorted(list(set(self.df1.columns) & set(self.df2.columns)))
            for col in common_columns:
                self.key_listbox.insert(tk.END, col)
            self.btn_process.config(state='normal')
            self.app.log("Ambos os ficheiros carregados. Colunas chave em comum atualizadas.")
        else:
            self.btn_process.config(state='disabled')

    def processar(self):
        selected_indices = self.key_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Erro", "Selecione pelo menos uma coluna chave para a comparação.")
            return
        
        key_columns = [self.key_listbox.get(i) for i in selected_indices]
        
        if self.df1 is None or self.df2 is None:
            messagebox.showerror("Erro", "Carregue ambos os arquivos antes de comparar.")
            return

        self.app.log(f"Iniciando comparação com base na(s) chave(s): {', '.join(key_columns)}")
        
        try:
            df1_copy = self.df1.copy()
            df2_copy = self.df2.copy()

            for col in key_columns:
                if not (col in df1_copy.columns and col in df2_copy.columns):
                    messagebox.showerror("Erro de Chave", f"A coluna chave '{col}' não foi encontrada em ambos os ficheiros.")
                    return
                df1_copy[col] = df1_copy[col].astype(str)
                df2_copy[col] = df2_copy[col].astype(str)

            merged = pd.merge(df1_copy, df2_copy, on=key_columns, how='outer', suffixes=('_antigo', '_novo'), indicator=True)

            # --- Linhas Removidas ---
            removed_data = merged[merged['_merge'] == 'left_only']
            removed_cols_map = {f'{col}_antigo': col for col in df1_copy.columns if col not in key_columns}
            removed = removed_data[key_columns + list(removed_cols_map.keys())].rename(columns=removed_cols_map)
            
            # --- Linhas Adicionadas ---
            added_data = merged[merged['_merge'] == 'right_only']
            added_cols_map = {f'{col}_novo': col for col in df2_copy.columns if col not in key_columns}
            added = added_data[key_columns + list(added_cols_map.keys())].rename(columns=added_cols_map)

            # --- Linhas Modificadas ---
            both = merged[merged['_merge'] == 'both'].copy()
            modified_list = []
            
            cols_to_compare = [col for col in df1_copy.columns if col in df2_copy.columns and col not in key_columns]

            for _, row in both.iterrows():
                is_modified = False
                modified_row_data = {k: row[k] for k in key_columns}
                
                for col in cols_to_compare:
                    col_old, col_new = f'{col}_antigo', f'{col}_novo'
                    val_old, val_new = row[col_old], row[col_new]
                    
                    if str(val_old) != str(val_new) and not (pd.isna(val_old) and pd.isna(val_new)):
                        is_modified = True
                        modified_row_data[col] = f"{val_old} -> {val_new}"
                    else:
                        modified_row_data[col] = val_old
                
                if is_modified:
                    modified_list.append(modified_row_data)

            modified = pd.DataFrame(modified_list)
            if not modified.empty:
                original_order = df1_copy.columns
                current_order = modified.columns
                new_order = [col for col in original_order if col in current_order]
                modified = modified[new_order]

            self.display_results(added, removed, modified)
            self.app.log("Comparação concluída.")

        except Exception as e:
            messagebox.showerror("Erro na Comparação", f"Ocorreu um erro inesperado: {e}")
            self.app.log(f"ERRO na comparação: {e}")

    def display_results(self, added, removed, modified):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        results_notebook = ttk.Notebook(self.results_frame, style='TNotebook')
        results_notebook.pack(fill='both', expand=True)

        self._create_result_tab(results_notebook, f"Adicionados ({len(added)})", added)
        self._create_result_tab(results_notebook, f"Removidos ({len(removed)})", removed)
        self._create_result_tab(results_notebook, f"Modificados ({len(modified)})", modified)
        
    def _create_result_tab(self, notebook, title, df):
        tab_frame = ttk.Frame(notebook, padding=10)
        notebook.add(tab_frame, text=title)

        if df.empty:
            ttk.Label(tab_frame, text="Nenhum item encontrado.").pack(pady=20)
            return

        tree = ttk.Treeview(tab_frame, columns=list(df.columns), show="headings")
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        for _, row in df.iterrows():
            tree.insert("", "end", values=[str(v) for v in row])
        
        tree.pack(fill='both', expand=True)


