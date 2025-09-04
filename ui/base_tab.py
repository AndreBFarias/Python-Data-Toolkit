# base_tab.py
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd
import os

class BaseTab(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master, fg_color="transparent")
        self.app = app_instance
        self.df = None
        self.filepath = None

    def selecionar_arquivo(self, label_widget, target_path_attr='filepath'):
        initial_dir = self.app.config_manager.get("default_import_path") or os.path.expanduser("~")
        
        filepath = filedialog.askopenfilename(
            title="Selecionar Arquivo",
            filetypes=[("Planilhas (CSV, Excel)", "*.csv *.xlsx *.xls"), ("Todos os arquivos", "*.*")],
            initialdir=initial_dir
        )
        if filepath:
            setattr(self, target_path_attr, filepath)
            label_widget.configure(text=os.path.basename(filepath))
            self.app.log(f"Arquivo selecionado: {filepath}")
            return True
        return False

    def carregar_dataframe(self, file_path):
        if not file_path:
            return None
        
        try:
            self.app.log(f"Carregando {os.path.basename(file_path)}...")
            csv_separator = self.app.config_manager.get("csv_separator") or ','
            
            if file_path.lower().endswith('.csv'):
                sep = simpledialog.askstring("Separador de CSV", "Qual o separador do arquivo CSV?", initialvalue=csv_separator)
                if sep is None: # Usuário cancelou
                    return None
                
                self.app.config_manager.set("csv_separator", sep)
                self.app.config_manager.save_config()
                
                # Tentativa inicial com UTF-8
                try:
                    df = pd.read_csv(file_path, sep=sep, encoding='utf-8', low_memory=False)
                    self.app.log(f"Arquivo carregado com sucesso (encoding: utf-8).")
                except UnicodeDecodeError:
                    # Fallback para Latin-1 em caso de falha
                    df = pd.read_csv(file_path, sep=sep, encoding='latin-1', low_memory=False)
                    self.app.log(f"Arquivo carregado com sucesso (fallback encoding: latin-1).")
            else:
                df = pd.read_excel(file_path)
            
            self.app.log("Arquivo carregado com sucesso.")
            return df
        except Exception as e:
            messagebox.showerror("Erro ao Carregar Arquivo", f"Não foi possível ler o arquivo:\n{e}")
            self.app.log(f"ERRO ao carregar {file_path}: {e}")
            return None

    def salvar_dataframe(self, df_to_save, is_unifier=False):
        if df_to_save is None:
            messagebox.showwarning("Aviso", "Não há dados para salvar.")
            return False

        initial_dir = self.app.config_manager.get("default_export_path") or os.path.expanduser("~")
        initial_filename = "UNIFICADO" if is_unifier else f"processado_{os.path.splitext(os.path.basename(self.filepath or 'arquivo'))[0]}"

        filepath = filedialog.asksaveasfilename(
            title="Salvar Arquivo Como",
            initialdir=initial_dir,
            initialfile=initial_filename,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )

        if not filepath:
            return False

        try:
            csv_separator = self.app.config_manager.get("csv_separator") or ','
            if filepath.lower().endswith('.csv'):
                df_to_save.to_csv(filepath, index=False, encoding='utf-8-sig', sep=csv_separator)
            else:
                df_to_save.to_excel(filepath, index=False)
            
            self.app.log(f"Arquivo salvo com sucesso em {filepath}")
            messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso em:\n{filepath}")
            return True
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{e}")
            self.app.log(f"ERRO ao salvar arquivo: {e}")
            return False
            
    def salvar_dataframe_por_tipo(self, df_to_save, filepath, file_extension):
        try:
            csv_separator = self.app.config_manager.get("csv_separator") or ','
            if file_extension == 'csv':
                df_to_save.to_csv(filepath, index=False, encoding='utf-8-sig', sep=csv_separator)
            else:
                df_to_save.to_excel(filepath, index=False)
            self.app.log(f" -> Arquivo salvo: {os.path.basename(filepath)}")
        except Exception as e:
            self.app.log(f" -> ERRO ao salvar {os.path.basename(filepath)}: {e}")
