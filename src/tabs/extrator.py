import os
import threading
import pandas as pd
import customtkinter as ctk
from tkinter import messagebox
import io

from src.ui.base_tab import BaseTab
from src.ui import theme


try:
    import tabula
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False

try:
    from unstructured.partition.auto import partition
    from unstructured.documents.elements import Table
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


class ExtratorTab(BaseTab):
    def __init__(self, master, app):
        super().__init__(master, app)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) 
        
        self.create_ui()
        
    def create_ui(self):
        
        self.frame_file = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_file.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        self.btn_import = ctk.CTkButton(self.frame_file, text="Selecionar Arquivo (PDF/DOCX)", 
                                      command=lambda: self.selecionar_arquivo(self.lbl_file, 'filepath', filetypes=[("Documentos (PDF, DOCX, DOC)", "*.pdf *.docx *.doc *.md *.txt"), ("Todos os arquivos", "*.*")]),
                                      font=theme.fonts["button"], height=theme.sizing["button_height"])
        self.btn_import.pack(side="left", padx=(0, 10))
        
        self.lbl_file = ctk.CTkLabel(self.frame_file, text="Nenhum arquivo selecionado", font=theme.fonts["body"])
        self.lbl_file.pack(side="left")

        
        self.frame_options = ctk.CTkFrame(self, fg_color=theme.colors["sidebar"])
        self.frame_options.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.frame_options.grid_columnconfigure(0, weight=1)
        self.frame_options.grid_columnconfigure(1, weight=1)
        
        
        self.lbl_method = ctk.CTkLabel(self.frame_options, text="Método de Extração", font=theme.fonts["h1"])
        self.lbl_method.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.method_var = ctk.StringVar(value="tabula")
        
        self.radio_tabula = ctk.CTkRadioButton(self.frame_options, text="Tabula (Rápido - Tabelas PDF)", 
                                             variable=self.method_var, value="tabula", font=theme.fonts["body"])
        self.radio_tabula.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.radio_unstructured = ctk.CTkRadioButton(self.frame_options, text="Unstructured (Inteligente - PDF/DOCX)", 
                                                   variable=self.method_var, value="unstructured", font=theme.fonts["body"])
        self.radio_unstructured.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        self.radio_pdfplumber = ctk.CTkRadioButton(self.frame_options, text="PDFPlumber (Empilhar Tabelas)", 
                                                 variable=self.method_var, value="pdfplumber", font=theme.fonts["body"])
        self.radio_pdfplumber.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="w")

        
        self.lbl_output = ctk.CTkLabel(self.frame_options, text="Opções de Saída", font=theme.fonts["h1"])
        self.lbl_output.grid(row=0, column=1, padx=20, pady=(10, 5), sticky="w")
        
        self.single_sheet_var = ctk.BooleanVar(value=False)
        self.chk_single_sheet = ctk.CTkCheckBox(self.frame_options, text="Salvar tudo em uma única aba", 
                                              variable=self.single_sheet_var, font=theme.fonts["body"])
        self.chk_single_sheet.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        
        
        self.btn_run = ctk.CTkButton(self.frame_options, text="Iniciar Extração", 
                                   command=self.run_extraction_thread,
                                   font=theme.fonts["button"], height=50, fg_color=theme.colors["green"], text_color=theme.colors["background"])
        self.btn_run.grid(row=2, column=1, rowspan=2, padx=20, pady=10, sticky="nsew")

        
        self.txt_log = ctk.CTkTextbox(self, font=theme.fonts["code"])
        self.txt_log.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.txt_log.insert("1.0", "Aguardando início...\n")

    def log_message(self, message):
        def _update():
            self.txt_log.insert("end", f"[{pd.Timestamp.now().strftime('%H:%M:%S')}] {message}\n")
            self.txt_log.see("end")
        self.after(0, _update)
        self.app.log(message)

    def run_extraction_thread(self):
        if not self.filepath:
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro.")
            return
            
        method = self.method_var.get()
        
        
        if method == "tabula" and not TABULA_AVAILABLE:
            messagebox.showerror("Erro", "Biblioteca 'tabula-py' não instalada.")
            return
        if method == "unstructured" and not UNSTRUCTURED_AVAILABLE:
            messagebox.showerror("Erro", "Biblioteca 'unstructured' não instalada.")
            return
        if method == "pdfplumber" and not PDFPLUMBER_AVAILABLE:
            messagebox.showerror("Erro", "Biblioteca 'pdfplumber' não instalada.")
            return

        self.btn_run.configure(state="disabled", text="Processando...")
        self.log_message(f"Iniciando extração com método: {method}")
        
        thread = threading.Thread(target=self.run_extraction, args=(method,))
        thread.start()

    def run_extraction(self, method):
        try:
            if method == "tabula":
                self.extract_tabula()
            elif method == "unstructured":
                self.extract_unstructured()
            elif method == "pdfplumber":
                self.extract_pdfplumber()
        except Exception as e:
            self.log_message(f"ERRO FATAL: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro durante a extração:\n{e}")
        finally:
            self.btn_run.configure(state="normal", text="Iniciar Extração")

    def extract_tabula(self):
        if not self.filepath.lower().endswith('.pdf'):
            self.log_message("AVISO: Tabula funciona melhor com PDFs.")
            
        self.log_message("Lendo tabelas com Tabula...")
        try:
            tables = tabula.read_pdf(self.filepath, pages='all', multiple_tables=True)
            
            if not tables:
                self.log_message("Nenhuma tabela encontrada.")
                return

            self.log_message(f"Encontradas {len(tables)} tabelas.")
            
            
            output_dfs = {}
            if self.single_sheet_var.get():
                
                combined_df = pd.DataFrame()
                for i, df in enumerate(tables):
                    df_named = df.copy()
                    df_named.insert(0, "Tabela_Origem", f"Tabela {i+1}")
                    combined_df = pd.concat([combined_df, df_named], ignore_index=True)
                output_dfs["todas_tabelas"] = combined_df
            else:
                for i, df in enumerate(tables):
                    output_dfs[f"tabela_{i+1}"] = df
            
            self.save_results(output_dfs)
            
        except Exception as e:
            raise e

    def extract_unstructured(self):
        self.log_message("Analisando documento com Unstructured (pode demorar)...")
        try:
            elements = partition(filename=self.filepath, strategy="auto")
            
            
            text_elements = [el for el in elements if not isinstance(el, Table)]
            full_text = "\n\n".join([str(el) for el in text_elements])
            
            if full_text:
                self.log_message("Texto extraído. Salvando arquivo de texto...")
                txt_path = os.path.splitext(self.filepath)[0] + "_texto.txt"
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(full_text)
                self.log_message(f"Texto salvo em: {os.path.basename(txt_path)}")
            
            
            table_elements = [el for el in elements if isinstance(el, Table)]
            if not table_elements:
                self.log_message("Nenhuma tabela encontrada pelo Unstructured.")
                return

            self.log_message(f"Encontradas {len(table_elements)} tabelas.")
            
            output_dfs = {}
            all_tables = []
            
            for i, table_el in enumerate(table_elements):
                html = table_el.metadata.text_as_html
                if html:
                    try:
                        df = pd.read_html(io.StringIO(html))[0]
                        all_tables.append(df)
                        if not self.single_sheet_var.get():
                            output_dfs[f"tabela_{i+1}"] = df
                    except:
                        self.log_message(f"Falha ao converter tabela {i+1} de HTML.")
            
            if self.single_sheet_var.get() and all_tables:
                 combined_df = pd.concat(all_tables, ignore_index=True)
                 output_dfs["todas_tabelas"] = combined_df
            
            if output_dfs:
                self.save_results(output_dfs)
            else:
                self.log_message("Nenhuma tabela válida extraída.")

        except Exception as e:
            raise e

    def extract_pdfplumber(self):
        if not self.filepath.lower().endswith('.pdf'):
            self.log_message("PDFPlumber requer arquivo PDF.")
            return

        self.log_message("Processando com PDFPlumber (Empilhamento)...")
        
        all_data = []
        master_header = None
        
        with pdfplumber.open(self.filepath) as pdf:
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    
                    cleaned_table = []
                    for row in table:
                        cleaned_row = [str(cell).strip() if cell else None for cell in row]
                        if any(cleaned_row):
                            cleaned_table.append(cleaned_row)
                    
                    if not cleaned_table: continue
                    
                    if master_header is None:
                        master_header = cleaned_table[0]
                        all_data.extend(cleaned_table[1:])
                        self.log_message(f"Cabeçalho mestre definido na página {i+1}")
                    else:
                        
                        if len(cleaned_table[0]) == len(master_header):
                            if cleaned_table[0] == master_header:
                                all_data.extend(cleaned_table[1:])
                            else:
                                all_data.extend(cleaned_table)
        
        if all_data and master_header:
            df = pd.DataFrame(all_data, columns=master_header)
            self.save_results({"tabelas_empilhadas": df})
        else:
            self.log_message("Nenhum dado extraído.")

    def save_results(self, dfs_dict):
        self.log_message("Salvando resultados...")
        
        
        initial_dir = self.app.config_manager.get("default_export_path") or os.path.expanduser("~")
        initial_filename = f"extracao_{os.path.splitext(os.path.basename(self.filepath))[0]}.xlsx"
        
        save_path = ctk.filedialog.asksaveasfilename(
            title="Salvar Extração",
            initialdir=initial_dir,
            initialfile=initial_filename,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if save_path:
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                for sheet_name, df in dfs_dict.items():
                    
                    safe_sheet_name = sheet_name[:31]
                    df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
            
            self.log_message(f"Salvo com sucesso em: {save_path}")
            messagebox.showinfo("Sucesso", f"Extração concluída!\nSalvo em: {save_path}")
        else:
            self.log_message("Salvamento cancelado pelo usuário.")
