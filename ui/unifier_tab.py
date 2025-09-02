import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import glob
from .base_tab import BaseTab
from ui import theme

class UnifierTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.folder_path = None
        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        folder_frame = ctk.CTkFrame(self, fg_color=theme.colors["sidebar"])
        folder_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(0, 15))
        folder_frame.columnconfigure(1, weight=1)

        self.btn_select_folder = ctk.CTkButton(folder_frame, text="Selecionar Pasta com os Arquivos...", font=theme.fonts["button"], command=self.handle_folder_selection, fg_color=theme.colors["comment"])
        self.btn_select_folder.grid(row=0, column=0, padx=15, pady=15)
        self.lbl_folderpath = ctk.CTkLabel(folder_frame, text="Nenhuma pasta selecionada.", font=theme.fonts["body"], text_color=theme.colors["comment"])
        self.lbl_folderpath.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        config_frame = ctk.CTkFrame(self, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        config_frame.grid(row=1, column=0, sticky='nsew', padx=5)
        config_frame.columnconfigure(0, weight=1)
        
        ctk.CTkLabel(config_frame, text="Configuração da Unificação", font=theme.fonts["h1"]).pack(anchor='w', padx=15, pady=(15, 10))
        
        pattern_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        pattern_frame.pack(fill='x', padx=15, pady=10)
        ctk.CTkLabel(pattern_frame, text="Padrão do nome do ficheiro (ex: `relatorio_*.xlsx`):", font=theme.fonts["body"]).pack(anchor='w', pady=(0,5))
        self.file_pattern_var = ctk.StringVar(value="*.*")
        ctk.CTkEntry(pattern_frame, textvariable=self.file_pattern_var, fg_color=theme.colors["background"], border_color=theme.colors["comment"]).pack(fill='x')

        options_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        options_frame.pack(fill='x', padx=15, pady=10)
        self.recursive_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(options_frame, text="Procurar em subpastas (recursivamente)", variable=self.recursive_var, font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"]).pack(anchor='w')
        
        self.add_source_col_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(options_frame, text="Adicionar coluna com nome do ficheiro de origem", variable=self.add_source_col_var, font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"]).pack(anchor='w', pady=(5,0))

        header_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        header_frame.pack(fill='x', padx=15, pady=(10, 20))
        ctk.CTkLabel(header_frame, text="Estratégia de união de colunas:", font=theme.fonts["body"]).pack(anchor='w', pady=(0,5))
        self.header_strategy_var = ctk.StringVar(value="union")
        ctk.CTkRadioButton(header_frame, text="União (manter todas as colunas de todos os ficheiros)", variable=self.header_strategy_var, value="union", font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"]).pack(anchor='w')
        ctk.CTkRadioButton(header_frame, text="Interseção (manter apenas colunas presentes em TODOS os ficheiros)", variable=self.header_strategy_var, value="intersection", font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"]).pack(anchor='w', pady=(5,0))
        
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=15)
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        
        self.btn_preview = ctk.CTkButton(action_frame, text="Pré-visualizar Unificação", command=self.preview_unification, font=theme.fonts["button"], fg_color="transparent", border_width=2, border_color=theme.colors["comment"])
        self.btn_preview.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.btn_process = ctk.CTkButton(action_frame, text="Unificar e Salvar Ficheiro", command=self.processar, font=theme.fonts["button"], fg_color=theme.colors["green"], text_color=theme.colors["background"], hover_color="#81F9A1")
        self.btn_process.grid(row=0, column=1, sticky='ew', padx=(5, 0))
        
        self.progress_bar = ctk.CTkProgressBar(self, orientation='horizontal', progress_color=theme.colors["green"])
        self.progress_bar.grid(row=3, column=0, sticky="ew", padx=5, pady=(0,10))
        self.progress_bar.set(0)

    def handle_folder_selection(self):
        initial_dir = self.app.config_manager.get("default_import_path") or os.path.expanduser("~")
        folder_path = filedialog.askdirectory(initialdir=initial_dir)
        if folder_path:
            self.folder_path = folder_path
            self.lbl_folderpath.configure(text=folder_path)
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
        num_files = len(files_to_process)
        self.progress_bar.set(0)
        self.app.log(f"Iniciando unificação de {num_files} ficheiros...")
        try:
            for i, f in enumerate(files_to_process):
                self.app.log(f" -> Lendo {os.path.basename(f)} ({i+1}/{num_files})...")
                try:
                    df = self.carregar_dataframe(f)
                    if df is None:
                        self.app.log(f"      - Aviso: Falha ao ler o ficheiro: {os.path.basename(f)}")
                        continue
                    if self.add_source_col_var.get():
                        df['ficheiro_origem'] = os.path.basename(f)
                    all_dfs.append(df)
                except Exception as e:
                    self.app.log(f"      - ERRO ao processar o ficheiro {os.path.basename(f)}: {e}")
                self.progress_bar.set((i + 1) / num_files)
                self.app.update_idletasks()
            if not all_dfs:
                messagebox.showerror("Erro", "Nenhum ficheiro pôde ser lido com sucesso.")
                self.progress_bar.set(0)
                return
            self.app.log("Concatenando todos os ficheiros...")
            join_strategy = 'outer' if self.header_strategy_var.get() == "union" else 'inner'
            final_df = pd.concat(all_dfs, ignore_index=True, sort=False, join=join_strategy)
            self.app.log(f"Unificação concluída. Dimensões finais: {final_df.shape[0]} linhas, {final_df.shape[1]} colunas.")
            self.salvar_dataframe(final_df, is_unifier=True)
        except Exception as e:
            messagebox.showerror("Erro no Processamento", f"Ocorreu um erro durante a unificação:\n{e}")
            self.app.log(f"ERRO durante a unificação: {e}")
        finally:
            self.progress_bar.set(0)
