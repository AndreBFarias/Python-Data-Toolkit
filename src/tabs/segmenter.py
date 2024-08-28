import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from src.ui.base_tab import BaseTab
from src.ui import theme

class SegmenterTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.column_vars = []
        self.column_combos = []
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

        ctk.CTkLabel(config_frame, text="Configuração da Divisão", font=theme.fonts["h1"]).pack(anchor='w', padx=15, pady=(15, 10))
        self.cols_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        self.cols_frame.pack(fill='x', padx=15, pady=(0, 5))
        ctk.CTkLabel(self.cols_frame, text="Dividir com base nas colunas:", font=theme.fonts["body"]).pack(anchor='w', pady=(0,5))
        self.add_column_selector()

        self.btn_add_column = ctk.CTkButton(config_frame, text="+ Adicionar outra coluna para agrupar", font=theme.fonts["body"], command=self.add_column_selector, state='disabled', fg_color="transparent", border_width=1, border_color=theme.colors["comment"])
        self.btn_add_column.pack(anchor='w', padx=15, pady=(0, 15))

        adv_options_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        adv_options_frame.pack(fill='x', padx=15, pady=5)
        
        self.group_small_var = ctk.BooleanVar()
        self.group_small_check = ctk.CTkCheckBox(adv_options_frame, text="Agrupar categorias com menos de", variable=self.group_small_var, state='disabled', font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"])
        self.group_small_check.pack(side='left', anchor='w')

        self.threshold_var = ctk.IntVar(value=10)
        self.threshold_entry = ctk.CTkEntry(adv_options_frame, textvariable=self.threshold_var, width=60, state='disabled', fg_color=theme.colors["background"], border_color=theme.colors["comment"])
        self.threshold_entry.pack(side='left', anchor='w', padx=5)

        ctk.CTkLabel(adv_options_frame, text="linhas num arquivo 'Outros'", font=theme.fonts["body"]).pack(side='left', anchor='w')

        naming_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        naming_frame.pack(fill='x', padx=15, pady=(20, 15))
        naming_frame.columnconfigure(1, weight=1)
        naming_frame.columnconfigure(3, weight=1)

        ctk.CTkLabel(naming_frame, text="Nomenclatura dos Arquivos de Saída:", font=theme.fonts["body"]).grid(row=0, column=0, columnspan=4, sticky='w', pady=(0,10))
        
        ctk.CTkLabel(naming_frame, text="Prefixo:", font=theme.fonts["body"]).grid(row=1, column=0, sticky='w', padx=(0, 5))
        self.prefix_var = ctk.StringVar()
        ctk.CTkEntry(naming_frame, textvariable=self.prefix_var, fg_color=theme.colors["background"], border_color=theme.colors["comment"]).grid(row=1, column=1, sticky='ew')
        
        ctk.CTkLabel(naming_frame, text="Sufixo:", font=theme.fonts["body"]).grid(row=1, column=2, sticky='w', padx=(15, 5))
        self.suffix_var = ctk.StringVar()
        ctk.CTkEntry(naming_frame, textvariable=self.suffix_var, fg_color=theme.colors["background"], border_color=theme.colors["comment"]).grid(row=1, column=3, sticky='ew')

        action_frame = ctk.CTkFrame(self, fg_color=theme.colors["sidebar"])
        action_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=15)
        action_frame.columnconfigure(0, weight=1)
        
        output_format_frame = ctk.CTkFrame(action_frame)
        output_format_frame.pack(fill='x', padx=15, pady=15)
        ctk.CTkLabel(output_format_frame, text="Formato de Saída:", font=theme.fonts["body"]).pack(side='left', padx=(0,10))
        self.output_format_var = ctk.StringVar(value='xlsx')
        ctk.CTkRadioButton(output_format_frame, text="Excel (.xlsx)", variable=self.output_format_var, value='xlsx', font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"]).pack(side='left', padx=5)
        ctk.CTkRadioButton(output_format_frame, text="CSV (.csv)", variable=self.output_format_var, value='csv', font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"]).pack(side='left', padx=5)

        buttons_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        buttons_frame.pack(fill='x', padx=15, pady=(0,15))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)

        self.btn_preview = ctk.CTkButton(buttons_frame, text="Pré-visualizar Divisão", font=theme.fonts["button"], command=self.preview_segmentation, state='disabled', fg_color="transparent", border_width=2, border_color=theme.colors["comment"])
        self.btn_preview.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.btn_process = ctk.CTkButton(buttons_frame, text="Processar e Salvar", command=self.processar, font=theme.fonts["button"], state='disabled', fg_color=theme.colors["green"], text_color=theme.colors["background"], hover_color="#81F9A1")
        self.btn_process.grid(row=0, column=1, sticky='ew', padx=(5, 0))
        
        self.progress_bar = ctk.CTkProgressBar(self, orientation='horizontal', progress_color=theme.colors["green"])
        self.progress_bar.grid(row=3, column=0, sticky="ew", padx=5, pady=(0,10))
        self.progress_bar.set(0)
    
    def add_column_selector(self):
        frame = ctk.CTkFrame(self.cols_frame, fg_color="transparent")
        frame.pack(fill='x', pady=2)
        var = ctk.StringVar()
        combo = ctk.CTkComboBox(frame, variable=var, state='disabled', command=self.populate_column_combos, button_color=theme.colors["comment"], fg_color=theme.colors["background"], border_color=theme.colors["comment"])
        combo.pack(side='left', fill='x', expand=True)
        self.column_vars.append(var)
        self.column_combos.append(combo)

    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:

                self.app.log("Arquivo carregado. Pode configurar a divisão.")
                self.enable_controls()
                self.populate_column_combos(None)
            else:
                self.disable_controls()

    def enable_controls(self):
        self.btn_add_column.configure(state='normal')
        self.group_small_check.configure(state='normal')
        self.threshold_entry.configure(state='normal')
        self.btn_preview.configure(state='normal')
        self.btn_process.configure(state='normal')
        for combo in self.column_combos:
            combo.configure(state='readonly')
            
    def disable_controls(self):
        self.btn_add_column.configure(state='disabled')
        self.group_small_check.configure(state='disabled')
        self.threshold_entry.configure(state='disabled')
        self.btn_preview.configure(state='disabled')
        self.btn_process.configure(state='disabled')
        for combo in self.column_combos:
            combo.configure(state='disabled')
        for var in self.column_vars:
            var.set('')

    def populate_column_combos(self, choice):
        if self.df is None: return
        columns = list(self.df.columns)
        for combo in self.column_combos:
            combo.configure(values=columns)

    def _get_selected_columns(self):
        return [var.get() for var in self.column_vars if var.get()]

    def _get_groups(self):
        if self.df is None:

            return None, "Nenhum arquivo carregado."
        selected_columns = self._get_selected_columns()
        if not selected_columns:
            return None, "Selecione pelo menos uma coluna para dividir."
        try:
            return self.df.groupby(selected_columns), None
        except KeyError:

            return None, "Uma ou mais colunas selecionadas não foram encontradas. Recarregue o arquivo."

    def preview_segmentation(self):
        groups, error = self._get_groups()
        if error:
            messagebox.showwarning("Aviso", error)
            return
        total_groups = len(groups)

        summary = f"A divisão irá gerar {total_groups} arquivos.\n\n"
        summary += "Primeiras 15 categorias (e contagem de linhas):\n" + "="*40 + "\n"
        for i, (name, group) in enumerate(groups):
            if i >= 15:
                summary += f"\n... e mais {total_groups - 15} categorias."
                break
            summary += f"- {name}: {len(group)} linhas\n"
        messagebox.showinfo("Pré-visualização da Divisão", summary)
        self.app.log("Pré-visualização da divisão gerada com sucesso.")

    def processar(self):
        groups, error = self._get_groups()
        if error:
            messagebox.showerror("Erro", error)
            return

        output_folder = filedialog.askdirectory(title="Selecione a pasta para salvar os arquivos")
        if not output_folder:
            return
        num_groups = len(groups)
        self.progress_bar.set(0)
        prefix = self.prefix_var.get()
        suffix = self.suffix_var.get()
        small_groups_df = pd.DataFrame()
        threshold = self.threshold_var.get() if self.group_small_var.get() else 0
        file_extension = self.output_format_var.get().lower()
        processed_count = 0
        try:
            for name, group in groups:
                if self.group_small_var.get() and len(group) < threshold:
                    small_groups_df = pd.concat([small_groups_df, group], ignore_index=True)
                else:
                    filename_parts = [prefix]
                    if isinstance(name, tuple):
                        filename_parts.extend(str(part) for part in name)
                    else:
                        filename_parts.append(str(name))
                    filename_parts.append(suffix)
                    filename = "_".join(filter(None, filename_parts))
                    safe_filename = "".join([c for c in filename if c.isalnum() or c in (' ', '-', '_')]).rstrip()
                    filepath = os.path.join(output_folder, f"{safe_filename}.{file_extension}")
                    self.salvar_dataframe_por_tipo(group, filepath, file_extension)
                processed_count += 1
                self.progress_bar.set(processed_count / num_groups)
                self.app.update_idletasks()
            if not small_groups_df.empty:
                filename = "_".join(filter(None, [prefix, "Outros", suffix]))
                filepath = os.path.join(output_folder, f"{filename}.{file_extension}")
                self.salvar_dataframe_por_tipo(small_groups_df, filepath, file_extension)

            self.app.log(f"Divisão concluída. Arquivos salvos em {output_folder}")
        except Exception as e:
            messagebox.showerror("Erro no Processamento", f"Ocorreu um erro:\n{e}")
            self.app.log(f"ERRO durante a divisão: {e}")
        finally:
            self.progress_bar.set(0)
