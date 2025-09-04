# geolocalizador_tab.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from unidecode import unidecode
from .base_tab import BaseTab
from ui import theme

class GeolocalizadorTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.df_ibge = app_instance.df_ibge  # DataFrame IBGE pré-carregado
        self.user_df = None
        self.result_df = None
        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure([0, 1, 2, 3, 4, 5], weight=1)

        # Frame de arquivo
        file_frame = ctk.CTkFrame(self, fg_color=theme.colors["sidebar"])
        file_frame.grid(row=0, column=0, sticky="ew", padx=theme.padding["frame"], pady=theme.padding["frame"])
        file_frame.columnconfigure(1, weight=1)

        self.btn_select_file = ctk.CTkButton(file_frame, text="Selecionar Arquivo...", font=theme.fonts["button"], 
                                            command=self.handle_file_selection, fg_color=theme.colors["comment"])
        self.btn_select_file.grid(row=0, column=0, padx=theme.padding["widget_x"], pady=theme.padding["widget_y"])
        self.lbl_filepath = ctk.CTkLabel(file_frame, text="Nenhum arquivo selecionado.", font=theme.fonts["body"], 
                                         text_color=theme.colors["white"] if not self.filepath else theme.colors["comment"])
        self.lbl_filepath.grid(row=0, column=1, padx=theme.padding["widget_x"], pady=theme.padding["widget_y"], sticky="w")

        # Frame de configuração
        config_frame = ctk.CTkFrame(self, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        config_frame.grid(row=1, column=0, sticky='nsew', padx=theme.padding["frame"], pady=theme.padding["frame"])
        config_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(config_frame, text="Enriquecer com Dados do IBGE", font=theme.fonts["h1"]).grid(row=0, column=0, columnspan=2, sticky='w', padx=theme.padding["widget_x"], pady=theme.padding["widget_y"])

        # Separador CSV
        ctk.CTkLabel(config_frame, text="Separador CSV:", font=theme.fonts["body"]).grid(row=1, column=0, sticky='w', padx=theme.padding["widget_x"], pady=theme.padding["widget_y"])
        self.separator_var = ctk.StringVar(value=self.app.config_manager.get("csv_separator") or ",")
        ctk.CTkComboBox(config_frame, values=[",", ";"], variable=self.separator_var, font=theme.fonts["body"], width=50).grid(row=1, column=1, sticky='w', padx=theme.padding["widget_x"], pady=theme.padding["widget_y"])

        # Seleção de coluna e tipo de join
        label_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        label_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=theme.padding["widget_x"], pady=theme.padding["widget_y"])
        ctk.CTkLabel(label_frame, text="Selecione a coluna com nomes de municípios:", font=theme.fonts["body"]).pack(side='left')
        self.column_combo = ctk.CTkComboBox(label_frame, values=[], font=theme.fonts["body"], state="disabled", text_color=theme.colors["white"])
        self.column_combo.pack(side='left', padx=(theme.padding["widget_x"], 0))

        join_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        join_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=theme.padding["widget_x"], pady=theme.padding["widget_y"])
        ctk.CTkLabel(join_frame, text="Tipo de Join:", font=theme.fonts["body"]).pack(side='left')
        self.join_var = ctk.StringVar(value="left")
        ctk.CTkRadioButton(join_frame, text="Left Join", variable=self.join_var, value="left", font=theme.fonts["body"]).pack(side='left', padx=theme.padding["widget_x"])
        ctk.CTkRadioButton(join_frame, text="Outer Join", variable=self.join_var, value="outer", font=theme.fonts["body"]).pack(side='left', padx=theme.padding["widget_x"])

        # Frame de botões
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=theme.padding["frame"], pady=theme.padding["frame"])
        self.btn_enrich = ctk.CTkButton(button_frame, text="Geoposicionar Agora!", font=theme.fonts["button"], command=self.enrich_data,
                                       fg_color=theme.colors["green"], text_color="black", state="disabled")
        self.btn_enrich.pack(side='left', padx=theme.padding["widget_x"])
        self.btn_save = ctk.CTkButton(button_frame, text="Salvar Resultado", font=theme.fonts["button"], command=self.save_result,
                                     fg_color=theme.colors["green"], text_color="black", state="disabled")
        self.btn_save.pack(side='left', padx=theme.padding["widget_x"])

        # Frame de resumo (inicialmente oculto)
        self.summary_frame = ctk.CTkFrame(self, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        self.summary_frame.grid(row=3, column=0, sticky='nsew', padx=theme.padding["frame"], pady=theme.padding["frame"])
        self.summary_frame.grid_remove()
        ctk.CTkLabel(self.summary_frame, text="Mapeamento Concluído!", font=theme.fonts["h1"]).grid(row=0, column=0, sticky='w', padx=theme.padding["widget_x"], pady=theme.padding["widget_y"])
        self.main_metric = ctk.CTkLabel(self.summary_frame, text="", font=theme.fonts["body"])
        self.main_metric.grid(row=1, column=0, sticky='w', padx=theme.padding["widget_x"], pady=theme.padding["widget_y"])
        self.diag_quick = ctk.CTkLabel(self.summary_frame, text="", font=theme.fonts["body"])
        self.diag_quick.grid(row=2, column=0, sticky='w', padx=theme.padding["widget_x"], pady=theme.padding["widget_y"])

        # Frame de tabelas
        table_frame = ctk.CTkFrame(self, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        table_frame.grid(row=4, column=0, sticky='nsew', padx=theme.padding["frame"], pady=theme.padding["frame"])
        table_frame.columnconfigure([0, 1], weight=1)
        table_frame.rowconfigure([0, 1], weight=1)

        self.user_text = ctk.CTkTextbox(table_frame, height=200, wrap='none', font=theme.fonts["body"], corner_radius=8, 
                                        fg_color=theme.colors["background"], border_color=theme.colors["comment"], border_width=1)
        self.user_text.grid(row=0, column=0, sticky='nsew', padx=theme.padding["widget_x"], pady=theme.padding["widget_y"])
        self.ibge_text = ctk.CTkTextbox(table_frame, height=200, wrap='none', font=theme.fonts["body"], corner_radius=8, 
                                        fg_color=theme.colors["background"], border_color=theme.colors["comment"], border_width=1)
        self.ibge_text.grid(row=0, column=1, sticky='nsew', padx=theme.padding["widget_x"], pady=theme.padding["widget_y"])
        self.result_text = ctk.CTkTextbox(table_frame, height=200, wrap='none', font=theme.fonts["body"], corner_radius=8, 
                                          fg_color=theme.colors["background"], border_color=theme.colors["comment"], border_width=1)
        self.result_text.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=theme.padding["widget_x"], pady=theme.padding["widget_y"])

    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath):
            self.user_df = self.carregar_dataframe(self.filepath)
            if self.user_df is not None:
                self.column_combo.configure(values=list(self.user_df.columns), state="normal")
                self.btn_enrich.configure(state="normal")
                self.display_tables()

    def display_tables(self):
        self.user_text.delete('1.0', ctk.END)
        self.ibge_text.delete('1.0', ctk.END)
        self.result_text.delete('1.0', ctk.END)

        if self.user_df is not None:
            self.user_text.insert('1.0', self.user_df.head(10).to_string(index=False))

        if self.df_ibge is not None:
            self.ibge_text.insert('1.0', self.df_ibge.head(10).to_string(index=False))

        if self.result_df is not None:
            self.result_text.insert('1.0', self.result_df.head(10).to_string(index=False))

    def enrich_data(self):
        if self.user_df is None or not self.column_combo.get():
            messagebox.showwarning("Aviso", "Selecione um arquivo e uma coluna primeiro.")
            return

        selected_column = self.column_combo.get()
        user_normalized = self.user_df[selected_column].apply(lambda x: unidecode(str(x).lower()) if pd.notna(x) else '')
        ibge_normalized = self.df_ibge['nome_normalized']

        self.result_df = self.user_df.merge(self.df_ibge, how=self.join_var.get(), left_on=user_normalized, right_on=ibge_normalized)
        total_rows = len(self.user_df)
        matched_rows = len(self.result_df)
        unmatched = total_rows - matched_rows

        self.summary_frame.grid()
        self.main_metric.configure(text=f"{matched_rows} de {total_rows} linhas foram geoposicionadas com sucesso.")
        self.diag_quick.configure(text=f"{unmatched} linhas não encontradas. Causa provável: nomes de municípios com grafia incorreta ou antigos.")

        self.display_tables()
        self.btn_save.configure(state="normal")
        self.app.log(f"Enriquecimento com dados IBGE concluído ({self.join_var.get()} join).")

    def save_result(self):
        if self.result_df is None:
            messagebox.showwarning("Aviso", "Nenhum resultado para salvar.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Salvar Resultado",
            defaultextension=".csv",
            filetypes=[("Planilhas Excel e CSV", "*.xlsx *.xls *.csv"), ("Todos os arquivos", "*.*")],
            initialfile=f"enriched_{os.path.splitext(os.path.basename(self.filepath))[0]}"
        )
        if output_path:
            try:
                if output_path.endswith(('.csv')):
                    self.result_df.to_csv(output_path, index=False)
                else:
                    self.result_df.to_excel(output_path, index=False)
                messagebox.showinfo("Sucesso", f"Arquivo salvo em: {output_path}")
                self.app.log(f"Resultado salvo em {output_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar arquivo: {e}")
                self.app.log(f"ERRO: {e}")
