import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from unidecode import unidecode
from .base_tab import BaseTab
from ui import theme

class IntegratorTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.df_ibge = app_instance.df_ibge  # DataFrame IBGE pré-carregado
        self.user_df = None
        self.result_df = None
        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        file_frame = ctk.CTkFrame(self, fg_color=theme.colors["sidebar"])
        file_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)

        self.btn_select_file = ctk.CTkButton(file_frame, text="Selecionar Arquivo...", font=theme.fonts["button"], command=self.handle_file_selection, fg_color=theme.colors["comment"])
        self.btn_select_file.grid(row=0, column=0, padx=15, pady=15)
        self.lbl_filepath = ctk.CTkLabel(file_frame, text="Nenhum arquivo selecionado.", font=theme.fonts["body"], text_color=theme.colors["comment"])
        self.lbl_filepath.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        config_frame = ctk.CTkFrame(self, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        config_frame.grid(row=1, column=0, sticky='nsew', padx=5)
        config_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(config_frame, text="Enriquecimento Geográfico", font=theme.fonts["h1"]).pack(anchor='w', padx=15, pady=(15, 10))
        ctk.CTkLabel(config_frame, text="Selecione a coluna com nomes de municípios:", font=theme.fonts["body"]).pack(anchor='w', pady=(0, 5))
        self.column_combo = ctk.CTkComboBox(config_frame, state="disabled", font=theme.fonts["body"])
        self.column_combo.pack(fill='x', padx=15, pady=(0, 15))

        self.btn_enrich = ctk.CTkButton(config_frame, text="Enriquecer com Dados do IBGE", font=theme.fonts["button"], command=self.enrich_data, state="disabled", fg_color=theme.colors["green"])
        self.btn_enrich.pack(padx=15, pady=(0, 15))

        self.result_table = ctk.CTkTextbox(config_frame, height=200, wrap='none', state='disabled', font=theme.fonts["body"], corner_radius=8, fg_color=theme.colors["background"], border_color=theme.colors["comment"], border_width=1)
        self.result_table.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        self.btn_save = ctk.CTkButton(config_frame, text="Salvar Resultado", font=theme.fonts["button"], command=self.save_result, state="disabled", fg_color=theme.colors["green"])
        self.btn_save.pack(padx=15, pady=(0, 15))

    def handle_file_selection(self):
        initial_dir = self.app.config_manager.get("default_import_path") or os.path.expanduser("~")
        filepath = filedialog.askopenfilename(
            title="Selecionar Arquivo",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=initial_dir
        )
        if filepath:
            self.filepath = filepath
            self.lbl_filepath.configure(text=os.path.basename(filepath))
            self.user_df = self.carregar_dataframe(filepath)
            if self.user_df is not None:
                self.column_combo.configure(values=list(self.user_df.columns), state="readonly")
                self.btn_enrich.configure(state="normal")
            self.app.log(f"Arquivo selecionado: {filepath}")

    def carregar_dataframe(self, file_path):
        try:
            self.app.log(f"Carregando {os.path.basename(file_path)}...")
            csv_separator = self.app.config_manager.get("csv_separator") or ','
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path, sep=csv_separator)
            else:
                df = pd.read_excel(file_path)
            self.app.log("Arquivo carregado com sucesso.")
            return df
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar arquivo: {e}")
            self.app.log(f"ERRO: {e}")
            return None

    def enrich_data(self):
        if self.user_df is None or not self.column_combo.get():
            messagebox.showwarning("Aviso", "Selecione um arquivo e uma coluna primeiro.")
            return

        selected_column = self.column_combo.get()
        user_normalized = self.user_df[selected_column].apply(lambda x: unidecode(str(x).lower()) if pd.notna(x) else '')
        ibge_normalized = self.df_ibge['nome'].apply(lambda x: unidecode(str(x).lower()) if pd.notna(x) else '')

        self.result_df = self.user_df.merge(self.df_ibge, how='left', left_on=user_normalized, right_on=ibge_normalized)
        self.display_result()
        self.btn_save.configure(state="normal")
        self.app.log("Enriquecimento com dados IBGE concluído.")

    def display_result(self):
        self.result_table.configure(state='normal')
        self.result_table.delete('1.0', ctk.END)
        self.result_table.insert('1.0', self.result_df.to_string(index=False))
        self.result_table.configure(state='disabled')

    def save_result(self):
        if self.result_df is None:
            messagebox.showwarning("Aviso", "Nenhum resultado para salvar.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Salvar Resultado",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"enriched_{os.path.splitext(os.path.basename(self.filepath))[0]}"
        )
        if output_path:
            try:
                if output_path.endswith('.csv'):
                    self.result_df.to_csv(output_path, index=False)
                else:
                    self.result_df.to_excel(output_path, index=False)
                messagebox.showinfo("Sucesso", f"Arquivo salvo em: {output_path}")
                self.app.log(f"Resultado salvo em {output_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar arquivo: {e}")
                self.app.log(f"ERRO: {e}")