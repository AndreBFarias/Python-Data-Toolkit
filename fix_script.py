import os
import sys

def run_fix():
    print("Iniciando o script de correção...")
    
    # Define o caminho base do projeto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ui_dir = os.path.join(script_dir, "ui")

    if not os.path.exists(ui_dir):
        print(f"Erro: O diretório 'ui' não foi encontrado em {script_dir}")
        return

    # --- 1. Corrige o arquivo base_tab.py ---
    print("\nCorrigindo base_tab.py...")
    base_tab_path = os.path.join(ui_dir, "base_tab.py")

    corrected_base_tab_content = """#1
# import tkinter as tk # LINHA ANTIGA COMENTADA
# from tkinter import ttk, filedialog, messagebox # LINHA ANTIGA COMENTADA
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os

#2
# class BaseTab(ttk.Frame): # LINHA ANTIGA COMENTADA
class BaseTab(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master, fg_color="transparent") # O fg_color='transparent' faz com que a aba assuma a cor do frame de conteúdo
        self.app = app_instance
        self.df = None
        self.filepath = None
        # self.pack(fill=tk.BOTH, expand=True) # LINHA ANTIGA COMENTADA - O layout agora é controlado pelo grid na classe principal

#4
    def selecionar_arquivo(self, label_widget, target_path_attr='filepath'):
        # Utiliza o caminho de importação padrão se estiver definido nas configurações
        initial_dir = self.app.config_manager.get("default_import_path") or os.path.expanduser("~")
        
        filepath = filedialog.askopenfilename(
            title="Selecionar Arquivo",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=initial_dir
        )
        if filepath:
            setattr(self, target_path_attr, filepath)
            # Assumindo que label_widget agora é um ctk.CTkLabel, o método de config é .configure()
            label_widget.configure(text=os.path.basename(filepath))
            self.app.log(f"Arquivo selecionado: {filepath}")
            return True
        return False

    def carregar_dataframe(self, file_path):
        if not file_path:
            return None
        
        try:
            self.app.log(f"Carregando {os.path.basename(file_path)}...")
            # Usa o separador de CSV das configurações
            csv_separator = self.app.config_manager.get("csv_separator") or ','
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path, sep=csv_separator)
            else:
                df = pd.read_excel(file_path)
            self.app.log("Arquivo carregado com sucesso.")
            return df
        except Exception as e:
            messagebox.showerror("Erro ao Carregar Arquivo", f"Não foi possível ler o arquivo:\\n{e}")
            self.app.log(f"ERRO ao carregar {file_path}: {e}")
            return None

    def salvar_dataframe(self, df_to_save, is_unifier=False):
        if df_to_save is None:
            messagebox.showwarning("Aviso", "Não há dados para salvar.")
            return False

        # Utiliza o caminho de exportação padrão se estiver definido
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
            messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso em:\\n{filepath}")
            return True
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo:\\n{e}")
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
"""
    
    with open(base_tab_path, "w", encoding="utf-8") as f:
        f.write(corrected_base_tab_content)
    print("✅ base_tab.py corrigido com sucesso!")

    # --- 2. Corrige a lógica nas outras abas ---
    tab_files = [
        "anonymizer_tab.py", "cleaner_tab.py", "comparer_tab.py", 
        "etl_preparer_tab.py", "profiler_tab.py", "segmenter_tab.py", 
        "unifier_tab.py", "visualizer_tab.py"
    ]

    for filename in tab_files:
        filepath = os.path.join(ui_dir, filename)
        if not os.path.exists(filepath):
            print(f"❌ Erro: {filename} não encontrado.")
            continue
            
        print(f"\nCorrigindo {filename}...")
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Encontra e substitui o trecho de código incorreto
        old_line = "self.selecionar_arquivo(self.lbl_filepath)"
        new_logic = """        if self.selecionar_arquivo(self.lbl_filepath):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:
"""
        # A lógica de substituição varia um pouco por causa do identation de cada arquivo
        if old_line in content:
            new_content = content.replace(old_line, new_logic)
            
            # Ajustes adicionais para cada arquivo
            if filename == "profiler_tab.py":
                # Profiller_tab tem a lógica logo depois
                old_logic = """        self.selecionar_arquivo(self.lbl_filepath)
        self.df = self.carregar_dataframe(self.filepath)
        if self.df is not None:
            self.run_profile()"""
                new_content = new_content.replace(old_logic, new_logic + "                self.run_profile()")
            elif filename == "unifier_tab.py":
                old_logic = """    def handle_folder_selection(self):
        initial_dir = self.app.config_manager.get("default_import_path") or os.path.expanduser("~")
        folder_path = filedialog.askdirectory(initialdir=initial_dir)
        if folder_path:
            self.folder_path = folder_path
            self.lbl_folderpath.configure(text=folder_path)
            self.app.log(f"Pasta de origem selecionada: {folder_path}")"""
                new_logic = """    def handle_folder_selection(self):
        initial_dir = self.app.config_manager.get("default_import_path") or os.path.expanduser("~")
        folder_path = filedialog.askdirectory(initialdir=initial_dir)
        if folder_path:
            self.folder_path = folder_path
            self.lbl_folderpath.configure(text=folder_path)
            self.app.log(f"Pasta de origem selecionada: {folder_path}")"""
                new_content = new_content.replace(old_logic, new_logic)
            elif filename == "comparer_tab.py":
                old_logic_file1 = """    def handle_file1_selection(self):
        self.selecionar_arquivo(self.lbl_filepath1, target_path_attr='filepath1')
        self.df1 = self.carregar_dataframe(self.filepath1)
        self.update_key_columns()"""
                new_logic_file1 = """    def handle_file1_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath1, target_path_attr='filepath1'):
            self.df1 = self.carregar_dataframe(self.filepath1)
            self.update_key_columns()"""
                old_logic_file2 = """    def handle_file2_selection(self):
        self.selecionar_arquivo(self.lbl_filepath2, target_path_attr='filepath2')
        self.df2 = self.carregar_dataframe(self.filepath2)
        self.update_key_columns()"""
                new_logic_file2 = """    def handle_file2_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath2, target_path_attr='filepath2'):
            self.df2 = self.carregar_dataframe(self.filepath2)
            self.update_key_columns()"""
                new_content = new_content.replace(old_logic_file1, new_logic_file1)
                new_content = new_content.replace(old_logic_file2, new_logic_file2)
            else:
                old_logic_default = """    def handle_file_selection(self):
        self.selecionar_arquivo(self.lbl_filepath)
        self.df = self.carregar_dataframe(self.filepath)
        if self.df is not None:"""
                new_content = new_content.replace(old_logic_default, new_logic)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ {filename} corrigido com sucesso!")
        else:
            print(f"✅ {filename} já parece estar corrigido. Ignorando.")

    print("\nProcesso de correção finalizado. Todos os ficheiros afetados foram verificados e corrigidos.")


if __name__ == "__main__":
    run_fix()
