import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import glob
from .base_tab import BaseTab

class UnifierTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- SEÇÃO: PASTA DE ORIGEM ---
        folder_frame = ttk.LabelFrame(main_frame, text="Pasta de Origem", padding=(15, 10))
        folder_frame.pack(fill='x', pady=(0, 20))

        self.btn_select_folder = ttk.Button(folder_frame, text="Selecionar Pasta com os Arquivos...", command=self.handle_folder_selection)
        self.btn_select_folder.pack(side="left", padx=(0, 10))
        self.lbl_folderpath = ttk.Label(folder_frame, text="Nenhuma pasta selecionada.")
        self.lbl_folderpath.pack(side="left", fill='x', expand=True)

        # --- SEÇÃO: CONFIGURAÇÃO DA UNIFICAÇÃO ---
        config_frame = ttk.LabelFrame(main_frame, text="Configuração da Unificação", padding=(15, 10))
        config_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Filtro de Ficheiros
        pattern_frame = ttk.Frame(config_frame)
        pattern_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(pattern_frame, text="Padrão do nome do ficheiro (ex: `relatorio_*.xlsx`):").pack(anchor='w', pady=(0,5))
        self.file_pattern_var = tk.StringVar(value="*.*")
        ttk.Entry(pattern_frame, textvariable=self.file_pattern_var).pack(fill='x')

        # Opções Checkbox
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill='x', pady=(0, 15))
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Procurar em subpastas (recursivamente)", variable=self.recursive_var).pack(anchor='w')
        
        self.add_source_col_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Adicionar coluna com nome do ficheiro de origem", variable=self.add_source_col_var).pack(anchor='w')

        # Estratégia de Cabeçalho
        header_frame = ttk.Frame(config_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(header_frame, text="Estratégia de união de colunas:").pack(anchor='w', pady=(0,5))
        self.header_strategy_var = tk.StringVar(value="union")
        ttk.Radiobutton(header_frame, text="União (manter todas as colunas de todos os ficheiros)", variable=self.header_strategy_var, value="union").pack(anchor='w')
        ttk.Radiobutton(header_frame, text="Interseção (manter apenas colunas presentes em TODOS os ficheiros)", variable=self.header_strategy_var, value="intersection").pack(anchor='w')
        
        # --- SEÇÃO: AÇÃO ---
        action_frame = ttk.LabelFrame(main_frame, text="Ação", padding=(15, 10))
        action_frame.pack(fill='x', pady=(0, 10))
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        
        self.btn_preview = ttk.Button(action_frame, text="Pré-visualizar Unificação", command=self.preview_unification)
        self.btn_preview.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.btn_process = ttk.Button(action_frame, text="Unificar e Salvar Ficheiro", command=self.processar, style='Accent.TButton')
        self.btn_process.grid(row=0, column=1, sticky='ew', padx=(5, 0))
        
        # Barra de Progresso
        self.progress_bar = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill='x', pady=(10,0))

    def handle_folder_selection(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path = folder_path
            self.lbl_folderpath.config(text=folder_path)
            self.app.log(f"Pasta de origem selecionada: {folder_path}")

    def _scan_files(self):
        if not hasattr(self, 'folder_path') or not self.folder_path:
            messagebox.showwarning("Aviso", "Selecione uma pasta de origem primeiro.")
            return None
        
        pattern = self.file_pattern_var.get()
        recursive = self.recursive_var.get()
        
        search_path = os.path.join(self.folder_path, '**', pattern) if recursive else os.path.join(self.folder_path, pattern)
        
        files_found = glob.glob(search_path, recursive=recursive)
        
        files_found = [f for f in files_found if os.path.isfile(f) and not os.path.basename(f).startswith('UNIFICADO_')]
        
        return files_found

    def preview_unification(self):
        files_to_process = self._scan_files()
        if files_to_process is None: return

        if not files_to_process:
            messagebox.showinfo("Pré-visualização", "Nenhum ficheiro encontrado com os critérios especificados.")
            return
            
        summary = f"Pré-visualização da Unificação:\n\n{len(files_to_process)} ficheiros encontrados.\n\n"
        summary += "Ficheiros a serem processados (prévia):\n" + "="*40 + "\n"
        for f in files_to_process[:15]:
            summary += os.path.basename(f) + "\n"
        if len(files_to_process) > 15:
            summary += f"... e mais {len(files_to_process) - 15} ficheiro(s).\n"
            
        messagebox.showinfo("Pré-visualização da Unificação", summary)
        self.app.log("Pré-visualização gerada com sucesso.")

    def processar(self):
        files_to_process = self._scan_files()
        if files_to_process is None: return
        
        if not files_to_process:
            messagebox.showerror("Erro", "Nenhum ficheiro correspondente encontrado para unificar.")
            return

        all_dfs = []
        self.progress_bar['maximum'] = len(files_to_process)
        self.progress_bar['value'] = 0
        self.app.log(f"Iniciando unificação de {len(files_to_process)} ficheiros...")

        try:
            for i, f in enumerate(files_to_process):
                self.app.log(f" -> Lendo {os.path.basename(f)} ({i+1}/{len(files_to_process)})...")
                try:
                    if f.endswith('.csv'):
                        df = pd.read_csv(f)
                    elif f.endswith(('.xls', '.xlsx')):
                        df = pd.read_excel(f)
                    else:
                        self.app.log(f"      - Aviso: Formato de ficheiro ignorado: {os.path.basename(f)}")
                        continue
                        
                    if self.add_source_col_var.get():
                        df['ficheiro_origem'] = os.path.basename(f)
                    
                    all_dfs.append(df)
                except Exception as e:
                    self.app.log(f"      - ERRO ao ler o ficheiro {os.path.basename(f)}: {e}")
                
                self.progress_bar.step()
                self.app.update_idletasks() # CORREÇÃO: Usar self.app em vez de self.app.root

            if not all_dfs:
                messagebox.showerror("Erro", "Nenhum ficheiro pôde ser lido com sucesso.")
                self.progress_bar['value'] = 0
                return

            self.app.log("Concatenando todos os ficheiros...")
            join_strategy = 'outer' if self.header_strategy_var.get() == "union" else 'inner'
            final_df = pd.concat(all_dfs, ignore_index=True, sort=False, join=join_strategy)
            
            self.app.log(f"Unificação concluída. Dimensões finais: {final_df.shape[0]} linhas, {final_df.shape[1]} colunas.")
            
            if self.salvar_dataframe(final_df, is_unifier=True):
                 self.app.log("Ficheiro unificado salvo com sucesso.")

        except Exception as e:
            messagebox.showerror("Erro no Processamento", f"Ocorreu um erro durante a unificação:\n{e}")
            self.app.log(f"ERRO durante a unificação: {e}")
        finally:
            self.progress_bar['value'] = 0

