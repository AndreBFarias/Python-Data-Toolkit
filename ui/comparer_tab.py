import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox, Listbox
import pandas as pd
from .base_tab import BaseTab
from ui import theme

class ComparerTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.df1 = None
        self.df2 = None
        self.filepath1 = None
        self.filepath2 = None
        self.create_widgets()
        self.style_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        top_files_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_files_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(0, 15))
        top_files_frame.columnconfigure(0, weight=1)
        top_files_frame.columnconfigure(1, weight=1)

        file1_frame = ctk.CTkFrame(top_files_frame, fg_color=theme.colors["sidebar"])
        file1_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 7))
        self.btn_select_file1 = ctk.CTkButton(file1_frame, text="Selecionar Ficheiro Antigo (Base)...", font=theme.fonts["button"], command=self.handle_file1_selection, fg_color=theme.colors["comment"])
        self.btn_select_file1.pack(padx=15, pady=15, fill='x')
        self.lbl_filepath1 = ctk.CTkLabel(file1_frame, text="Nenhum arquivo.", font=theme.fonts["body"], text_color=theme.colors["comment"])
        self.lbl_filepath1.pack(padx=15, pady=(0, 15), anchor='w')

        file2_frame = ctk.CTkFrame(top_files_frame, fg_color=theme.colors["sidebar"])
        file2_frame.grid(row=0, column=1, sticky='nsew', padx=(7, 0))
        self.btn_select_file2 = ctk.CTkButton(file2_frame, text="Selecionar Ficheiro Novo (Comparação)...", font=theme.fonts["button"], command=self.handle_file2_selection, fg_color=theme.colors["comment"])
        self.btn_select_file2.pack(padx=15, pady=15, fill='x')
        self.lbl_filepath2 = ctk.CTkLabel(file2_frame, text="Nenhum arquivo.", font=theme.fonts["body"], text_color=theme.colors["comment"])
        self.lbl_filepath2.pack(padx=15, pady=(0, 15), anchor='w')

        config_action_frame = ctk.CTkFrame(self, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        config_action_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=(0, 15))
        config_action_frame.columnconfigure(0, weight=1)
        
        ctk.CTkLabel(config_action_frame, text="Configuração da Comparação", font=theme.fonts["h1"]).grid(row=0, column=0, sticky='w', padx=15, pady=(15, 5))
        ctk.CTkLabel(config_action_frame, text="Selecione a(s) coluna(s) chave para identificação das linhas (Ex: ID, CPF):", font=theme.fonts["body"]).grid(row=1, column=0, sticky='w', padx=15, pady=(0,5))
        
        self.key_listbox = Listbox(config_action_frame, selectmode="multiple", height=5, exportselection=False,
                                   background=theme.colors["background"], foreground=theme.colors["foreground"], 
                                   selectbackground=theme.colors["accent"], relief='flat', borderwidth=0,
                                   highlightthickness=0, selectborderwidth=0, font=theme.fonts["body"])
        self.key_listbox.grid(row=2, column=0, sticky='ew', padx=15, pady=(0,15))
        
        self.btn_process = ctk.CTkButton(config_action_frame, text="Comparar Arquivos", command=self.processar, font=theme.fonts["button"], state='disabled',
                                         fg_color=theme.colors["accent"], text_color=theme.colors["background"], hover_color=theme.colors["pink"])
        self.btn_process.grid(row=3, column=0, sticky='ew', padx=15, pady=(0,15))

        self.results_frame = ctk.CTkFrame(self, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        self.results_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=0)
        self.results_frame.grid_propagate(False)
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self.results_frame, text="Resultados da Comparação", font=theme.fonts["h1"]).grid(row=0, column=0, sticky='w', padx=15, pady=(15, 10))

    def style_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=theme.colors["background"],
                        foreground=theme.colors["foreground"],
                        fieldbackground=theme.colors["background"],
                        rowheight=25,
                        borderwidth=0)
        style.map("Treeview", background=[('selected', theme.colors["accent"])])
        style.configure("Treeview.Heading",
                        background=theme.colors["sidebar"],
                        foreground=theme.colors["accent"],
                        font=theme.fonts["button"],
                        relief="flat",
                        borderwidth=0)
        style.map("Treeview.Heading", background=[('active', theme.colors["comment"])])

    def handle_file1_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath1, target_path_attr='filepath1'):
            self.df1 = self.carregar_dataframe(self.filepath1)
            self.update_key_columns()

    def handle_file2_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath2, target_path_attr='filepath2'):
            self.df2 = self.carregar_dataframe(self.filepath2)
            self.update_key_columns()

    def update_key_columns(self):
        self.key_listbox.delete(0, "end")
        if self.df1 is not None and self.df2 is not None:
            common_columns = sorted(list(set(self.df1.columns) & set(self.df2.columns)))
            for col in common_columns:
                self.key_listbox.insert("end", col)
            self.btn_process.configure(state='normal')
            self.app.log("Ambos os ficheiros carregados. Colunas chave em comum atualizadas.")
        else:
            self.btn_process.configure(state='disabled')

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
            removed_data = merged[merged['_merge'] == 'left_only']
            removed_cols_map = {f'{col}_antigo': col for col in df1_copy.columns if col not in key_columns}
            removed = removed_data[key_columns + list(removed_cols_map.keys())].rename(columns=removed_cols_map)
            added_data = merged[merged['_merge'] == 'right_only']
            added_cols_map = {f'{col}_novo': col for col in df2_copy.columns if col not in key_columns}
            added = added_data[key_columns + list(added_cols_map.keys())].rename(columns=added_cols_map)
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
            if isinstance(widget, ctk.CTkLabel): continue
            widget.destroy()
            
        tab_view = ctk.CTkTabview(self.results_frame, text_color=theme.colors["foreground"], 
                                  fg_color=theme.colors["background"],
                                  segmented_button_fg_color=theme.colors["background"],
                                  segmented_button_selected_color=theme.colors["accent"],
                                  segmented_button_unselected_color=theme.colors["sidebar"],
                                  segmented_button_selected_hover_color=theme.colors["pink"])
        tab_view.grid(row=1, column=0, sticky='nsew', padx=15, pady=(0,15))

        tab_view.add(f"Adicionados ({len(added)})")
        tab_view.add(f"Removidos ({len(removed)})")
        tab_view.add(f"Modificados ({len(modified)})")

        self._create_result_tab(tab_view.tab(f"Adicionados ({len(added)})"), added)
        self._create_result_tab(tab_view.tab(f"Removidos ({len(removed)})"), removed)
        self._create_result_tab(tab_view.tab(f"Modificados ({len(modified)})"), modified)
        
    def _create_result_tab(self, tab_frame, df):
        if df.empty:
            ctk.CTkLabel(tab_frame, text="Nenhum item encontrado.", font=theme.fonts["body"]).pack(pady=20)
            return

        tree_container = ctk.CTkFrame(tab_frame, fg_color=theme.colors["background"])
        tree_container.pack(fill='both', expand=True, padx=1, pady=1)

        tree = ttk.Treeview(tree_container, columns=list(df.columns), show="headings")
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        for _, row in df.iterrows():
            tree.insert("", "end", values=[str(v) for v in row.fillna('')])
        
        tree.pack(fill='both', expand=True)
