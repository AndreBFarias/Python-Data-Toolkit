import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from src.ui.base_tab import BaseTab
from src.ui import theme

class ProfilerTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.create_widgets()
        self.style_treeview()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        file_frame = ctk.CTkFrame(self, fg_color=theme.colors["sidebar"])
        file_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)


        self.btn_select_file = ctk.CTkButton(file_frame, text="Selecionar Arquivo para Análise...", font=theme.fonts["button"], command=self.handle_file_selection, fg_color=theme.colors["comment"])
        self.btn_select_file.grid(row=0, column=0, padx=15, pady=15)

        self.lbl_filepath = ctk.CTkLabel(file_frame, text="Nenhum arquivo selecionado.", font=theme.fonts["body"], text_color=theme.colors["comment"])
        self.lbl_filepath.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        results_frame = ctk.CTkFrame(self, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        results_frame.grid(row=1, column=0, sticky='nsew', padx=5)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(3, weight=1)
        
        ctk.CTkLabel(results_frame, text="Resultados da Análise", font=theme.fonts["h1"]).grid(row=0, column=0, sticky='w', padx=15, pady=(15, 10))
        
        self.summary_text = ctk.CTkTextbox(results_frame, height=110, wrap='word', state='disabled', 
                                           font=theme.fonts["body"], corner_radius=8, fg_color=theme.colors["background"],
                                           border_color=theme.colors["comment"], border_width=1)
        self.summary_text.grid(row=1, column=0, sticky='ew', padx=15, pady=(0, 15))

        ctk.CTkLabel(results_frame, text="Detalhes por Coluna:", font=theme.fonts["body"]).grid(row=2, column=0, sticky='w', padx=15, pady=(0, 5))
        
        tree_frame_container = ctk.CTkFrame(results_frame, fg_color=theme.colors["background"])
        tree_frame_container.grid(row=3, column=0, sticky='nsew', padx=15, pady=(0, 15))
        
        tree_columns = ("column", "type", "nulls", "uniques", "mean", "std", "min", "max")
        self.tree = ttk.Treeview(tree_frame_container, columns=tree_columns, show="headings")
        
        headings = {
            "column": "Coluna", "type": "Tipo de Dado", "nulls": "% Nulos", 
            "uniques": "Valores Únicos", "mean": "Média", "std": "Desvio Padrão",
            "min": "Mínimo", "max": "Máximo"
        }
        
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100, anchor='center')

        self.tree.pack(fill='both', expand=True, padx=1, pady=1)

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=15)
        action_frame.columnconfigure(0, weight=1)
        
        self.btn_export = ctk.CTkButton(action_frame, text="Exportar Relatório", command=self.export_report, font=theme.fonts["button"], state='disabled', 
                                        fg_color=theme.colors["green"], text_color=theme.colors["background"], hover_color="#81F9A1")
        self.btn_export.grid(row=0, column=0, sticky='ew', padx=0, pady=0)

    def style_treeview(self):
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
                        font=("Roboto", 13, "bold"),
                        relief="flat",
                        borderwidth=0)
        style.map("Treeview.Heading", background=[('active', theme.colors["comment"])])
    
    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:
                self.run_profile()

    def run_profile(self):
        if self.df is None: return

        self.app.log("Iniciando análise do arquivo...")

        self.summary_text.configure(state='normal')
        self.summary_text.delete('1.0', ctk.END)
        for i in self.tree.get_children():
            self.tree.delete(i)

        rows, cols = self.df.shape
        total_cells = self.df.size
        total_nulls = self.df.isnull().sum().sum()
        null_percentage = (total_nulls / total_cells) * 100 if total_cells > 0 else 0
        memory_usage = self.df.memory_usage(deep=True).sum() / (1024 * 1024)

        summary = (
            f"Dimensões: {rows} linhas, {cols} colunas\n"
            f"Total de Células: {total_cells}\n"
            f"Células Vazias: {total_nulls} ({null_percentage:.2f}%)\n"
            f"Uso de Memória (aprox.): {memory_usage:.2f} MB"
        )
        self.summary_text.insert('1.0', summary)
        self.summary_text.configure(state='disabled')

        for column in self.df.columns:
            col_data = self.df[column]
            dtype = col_data.dtype
            nulls = col_data.isnull().sum()
            null_perc = (nulls / rows) * 100 if rows > 0 else 0
            uniques = col_data.nunique()
            
            stats = {
                "column": column,
                "type": str(dtype),
                "nulls": f"{null_perc:.2f}%",
                "uniques": uniques,
                "mean": "-", "std": "-", "min": "-", "max": "-"
            }

            if pd.api.types.is_numeric_dtype(dtype):
                stats["mean"] = f"{col_data.mean():.2f}"
                stats["std"] = f"{col_data.std():.2f}"
                stats["min"] = f"{col_data.min():.2f}"
                stats["max"] = f"{col_data.max():.2f}"

            self.tree.insert("", "end", values=tuple(stats.values()))
        
        self.btn_export.configure(state='normal')
        self.app.log("Análise concluída com sucesso.")

    def export_report(self):
        if self.df is None:
            messagebox.showwarning("Aviso", "Nenhum dado para exportar.")
            return

        report_path = filedialog.asksaveasfilename(
            title="Salvar Relatório de Análise",
            defaultextension=".txt",

            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],

            initialfile=f"analise_{os.path.splitext(os.path.basename(self.filepath))[0]}.txt"
        )

        if not report_path:
            return

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("RELATÓRIO DE ANÁLISE DE DADOS\n")
                f.write("="*40 + "\n\n")

                f.write("ARQUIVO ANALISADO:\n")
                f.write(f"{self.filepath}\n\n")
                f.write("SUMÁRIO GERAL:\n")
                f.write(self.summary_text.get('1.0', ctk.END) + "\n")
                
                f.write("DETALHES POR COLUNA:\n")
                headers = [self.tree.heading(col)["text"] for col in self.tree['columns']]
                f.write("\t".join(headers) + "\n")
                f.write("="*80 + "\n")
                for child_id in self.tree.get_children():
                    values = self.tree.item(child_id)['values']
                    f.write("\t".join(map(str, values)) + "\n")


            messagebox.showinfo("Sucesso", f"Relatório salvo com sucesso em:\n{report_path}")
            self.app.log(f"Relatório de análise exportado para {report_path}")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o relatório:\n{e}")
