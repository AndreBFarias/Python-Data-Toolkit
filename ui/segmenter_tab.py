import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from .base_tab import BaseTab

class SegmenterTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.column_vars = []
        self.column_combos = []
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

        # --- SEÇÃO: CONFIGURAÇÃO DA SEGMENTAÇÃO ---
        config_frame = ttk.LabelFrame(main_frame, text="Configuração da Segmentação", padding=(15, 10))
        config_frame.pack(fill='both', expand=True, pady=(0, 20))

        # Colunas de Segmentação
        self.cols_frame = ttk.Frame(config_frame)
        self.cols_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(self.cols_frame, text="Dividir com base nas colunas:").pack(anchor='w')
        self.add_column_selector()

        self.btn_add_column = ttk.Button(config_frame, text="+ Adicionar outra coluna para agrupar", command=self.add_column_selector, state='disabled')
        self.btn_add_column.pack(anchor='w', pady=(0, 20))

        # Opções Avançadas
        adv_options_frame = ttk.Frame(config_frame)
        adv_options_frame.pack(fill='x')
        
        self.group_small_var = tk.BooleanVar()
        self.group_small_check = ttk.Checkbutton(adv_options_frame, text="Agrupar categorias com menos de", variable=self.group_small_var, state='disabled')
        self.group_small_check.pack(side='left', anchor='w')

        self.threshold_var = tk.IntVar(value=10)
        self.threshold_spinbox = ttk.Spinbox(adv_options_frame, from_=1, to=1000, textvariable=self.threshold_var, width=5, state='disabled')
        self.threshold_spinbox.pack(side='left', anchor='w', padx=5)
        ttk.Label(adv_options_frame, text="linhas num ficheiro 'Outros'").pack(side='left', anchor='w')

        # Nomenclatura dos Ficheiros de Saída
        naming_frame = ttk.LabelFrame(config_frame, text="Nomenclatura dos Ficheiros de Saída", padding=10)
        naming_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Label(naming_frame, text="Prefixo:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.prefix_var = tk.StringVar()
        ttk.Entry(naming_frame, textvariable=self.prefix_var).grid(row=0, column=1, sticky='ew')
        
        ttk.Label(naming_frame, text="Sufixo:").grid(row=0, column=2, sticky='w', padx=(10, 5))
        self.suffix_var = tk.StringVar()
        ttk.Entry(naming_frame, textvariable=self.suffix_var).grid(row=0, column=3, sticky='ew')
        naming_frame.columnconfigure(1, weight=1)
        naming_frame.columnconfigure(3, weight=1)

        # --- SEÇÃO: FORMATO DE SAÍDA E AÇÃO ---
        action_frame = ttk.LabelFrame(main_frame, text="Formato de Saída e Ação", padding=(15, 10))
        action_frame.pack(fill='x', pady=(0, 10))
        
        output_format_frame = ttk.Frame(action_frame)
        output_format_frame.pack(fill='x', pady=(0,15))
        ttk.Label(output_format_frame, text="Formato de Saída:").pack(side='left', padx=(0,10))
        self.output_format_var = tk.StringVar(value='xlsx')
        ttk.Radiobutton(output_format_frame, text="Excel (.xlsx)", variable=self.output_format_var, value='xlsx').pack(side='left', padx=5)
        ttk.Radiobutton(output_format_frame, text="CSV (.csv)", variable=self.output_format_var, value='csv').pack(side='left', padx=5)

        buttons_frame = ttk.Frame(action_frame)
        buttons_frame.pack(fill='x')
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)

        self.btn_preview = ttk.Button(buttons_frame, text="Pré-visualizar Segmentação", command=self.preview_segmentation, state='disabled')
        self.btn_preview.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.btn_process = ttk.Button(buttons_frame, text="Processar e Salvar", command=self.processar, style='Accent.TButton', state='disabled')
        self.btn_process.grid(row=0, column=1, sticky='ew', padx=(5, 0))
        
        self.progress_bar = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill='x', pady=(10,0))
    
    def add_column_selector(self):
        frame = ttk.Frame(self.cols_frame)
        frame.pack(fill='x', pady=2)
        var = tk.StringVar()
        combo = ttk.Combobox(frame, textvariable=var, state='disabled', width=40, postcommand=self.populate_column_combos)
        combo.pack(side='left', fill='x', expand=True)
        self.column_vars.append(var)
        self.column_combos.append(combo)

    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:
                self.app.log("Ficheiro carregado. Pode configurar a segmentação.")
                self.enable_controls()
                self.populate_column_combos()
            else:
                self.disable_controls()

    def enable_controls(self):
        self.btn_add_column.config(state='normal')
        self.group_small_check.config(state='normal')
        self.threshold_spinbox.config(state='normal')
        self.btn_preview.config(state='normal')
        self.btn_process.config(state='normal')
        for combo in self.column_combos:
            combo.config(state='readonly')
            
    def disable_controls(self):
        self.btn_add_column.config(state='disabled')
        self.group_small_check.config(state='disabled')
        self.threshold_spinbox.config(state='disabled')
        self.btn_preview.config(state='disabled')
        self.btn_process.config(state='disabled')
        for combo in self.column_combos:
            combo.config(state='disabled')
        for var in self.column_vars:
            var.set('')

    def populate_column_combos(self):
        if self.df is None: return
        columns = list(self.df.columns)
        for combo in self.column_combos:
            combo['values'] = columns

    def _get_selected_columns(self):
        return [var.get() for var in self.column_vars if var.get()]

    def _get_groups(self):
        if self.df is None:
            return None, "Nenhum ficheiro carregado."
        selected_columns = self._get_selected_columns()
        if not selected_columns:
            return None, "Selecione pelo menos uma coluna para segmentar."
        try:
            return self.df.groupby(selected_columns), None
        except KeyError:
            return None, "Uma ou mais colunas selecionadas não foram encontradas. Recarregue o ficheiro."

    def preview_segmentation(self):
        groups, error = self._get_groups()
        if error:
            messagebox.showwarning("Aviso", error)
            return

        total_groups = len(groups)
        summary = f"A segmentação irá gerar {total_groups} ficheiros.\n\n"
        summary += "Primeiras 15 categorias (e contagem de linhas):\n" + "="*40 + "\n"
        
        for i, (name, group) in enumerate(groups):
            if i >= 15:
                summary += f"\n... e mais {total_groups - 15} categorias."
                break
            summary += f"- {name}: {len(group)} linhas\n"
            
        messagebox.showinfo("Pré-visualização da Segmentação", summary)
        self.app.log("Pré-visualização da segmentação gerada com sucesso.")

    def processar(self):
        groups, error = self._get_groups()
        if error:
            messagebox.showerror("Erro", error)
            return

        output_folder = filedialog.askdirectory(title="Selecione a pasta para salvar os ficheiros")
        if not output_folder:
            return

        self.progress_bar['maximum'] = len(groups)
        self.progress_bar['value'] = 0

        prefix = self.prefix_var.get()
        suffix = self.suffix_var.get()
        
        small_groups_df = pd.DataFrame()
        threshold = self.threshold_var.get() if self.group_small_var.get() else 0
        file_extension = self.output_format_var.get().lower()

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
                    safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()
                    
                    filepath = os.path.join(output_folder, f"{safe_filename}.{file_extension}")
                    self.salvar_dataframe_por_tipo(group, filepath, file_extension)

                self.progress_bar.step()
                self.app.update_idletasks() # CORREÇÃO: Usar self.app em vez de self.app.root

            if not small_groups_df.empty:
                filename = "_".join(filter(None, [prefix, "Outros", suffix]))
                filepath = os.path.join(output_folder, f"{filename}.{file_extension}")
                self.salvar_dataframe_por_tipo(small_groups_df, filepath, file_extension)

            messagebox.showinfo("Sucesso", f"Processo concluído! Ficheiros salvos em:\n{output_folder}")
            self.app.log(f"Segmentação concluída. Ficheiros salvos em {output_folder}")
        except Exception as e:
            messagebox.showerror("Erro no Processamento", f"Ocorreu um erro:\n{e}")
            self.app.log(f"ERRO durante a segmentação: {e}")
        finally:
            self.progress_bar['value'] = 0


