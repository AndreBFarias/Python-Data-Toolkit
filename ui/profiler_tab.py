import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from .base_tab import BaseTab

class ProfilerTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- SEÇÃO: FICHEIRO DE ORIGEM ---
        file_frame = ttk.LabelFrame(main_frame, text="Ficheiro de Origem", padding=(15, 10))
        file_frame.pack(fill='x', pady=(0, 20))

        self.btn_select_file = ttk.Button(file_frame, text="Selecionar Arquivo para Análise...", command=self.handle_file_selection)
        self.btn_select_file.pack(side="left", padx=(0, 10))
        self.lbl_filepath = ttk.Label(file_frame, text="Nenhum arquivo selecionado.")
        self.lbl_filepath.pack(side="left", fill='x', expand=True)

        # --- SEÇÃO: RESULTADOS DA ANÁLISE ---
        results_frame = ttk.LabelFrame(main_frame, text="Resultados da Análise", padding=(15, 10))
        results_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Sumário Geral
        self.summary_text = tk.Text(results_frame, height=5, wrap='word', state='disabled', 
                                    bg=self.app.ALT_BG, fg=self.app.FG_COLOR, relief='flat',
                                    font=('Inter', 10))
        self.summary_text.pack(fill='x', pady=(0, 15))

        # Detalhes por Coluna
        ttk.Label(results_frame, text="Detalhes por Coluna:").pack(anchor='w', pady=(0, 5))
        
        tree_frame = ttk.Frame(results_frame)
        tree_frame.pack(fill='both', expand=True)

        tree_columns = ("column", "type", "nulls", "uniques", "mean", "std", "min", "max")
        self.tree = ttk.Treeview(tree_frame, columns=tree_columns, show="headings")
        
        headings = {
            "column": "Coluna", "type": "Tipo de Dado", "nulls": "% Nulos", 
            "uniques": "Valores Únicos", "mean": "Média", "std": "Desvio Padrão",
            "min": "Mínimo", "max": "Máximo"
        }
        
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100, anchor='center')

        # Scrollbars
        ysb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)

        ysb.pack(side='right', fill='y')
        xsb.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=True)

        # --- SEÇÃO: AÇÃO ---
        action_frame = ttk.LabelFrame(main_frame, text="Ação", padding=(15, 10))
        action_frame.pack(fill='x', pady=(0, 10))
        
        self.btn_export = ttk.Button(action_frame, text="Exportar Relatório", command=self.export_report, style='Accent.TButton', state='disabled')
        self.btn_export.pack(fill='x')

    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:
                self.run_profile()

    def run_profile(self):
        if self.df is None: return
        self.app.log("Iniciando análise do arquivo...")

        # Limpa widgets
        self.summary_text.config(state='normal')
        self.summary_text.delete('1.0', tk.END)
        for i in self.tree.get_children():
            self.tree.delete(i)

        # 1. Sumário Geral
        rows, cols = self.df.shape
        total_cells = self.df.size
        total_nulls = self.df.isnull().sum().sum()
        null_percentage = (total_nulls / total_cells) * 100 if total_cells > 0 else 0
        memory_usage = self.df.memory_usage(deep=True).sum() / (1024 * 1024) # Em MB

        summary = (
            f"Dimensões: {rows} linhas, {cols} colunas\n"
            f"Total de Células: {total_cells}\n"
            f"Células Vazias: {total_nulls} ({null_percentage:.2f}%)\n"
            f"Uso de Memória (aprox.): {memory_usage:.2f} MB"
        )
        self.summary_text.insert('1.0', summary)
        self.summary_text.config(state='disabled')

        # 2. Detalhes por Coluna
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
        
        self.btn_export.config(state='normal')
        self.app.log("Análise concluída com sucesso.")

    def export_report(self):
        if self.df is None:
            messagebox.showwarning("Aviso", "Nenhum dado para exportar.")
            return

        report_path = filedialog.asksaveasfilename(
            title="Salvar Relatório de Análise",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"analise_{os.path.basename(self.filepath)}.txt"
        )

        if not report_path:
            return

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("RELATÓRIO DE ANÁLISE DE DADOS\n")
                f.write("="*40 + "\n\n")
                f.write("FICHEIRO ANALISADO:\n")
                f.write(f"{self.filepath}\n\n")
                f.write("SUMÁRIO GERAL:\n")
                f.write(self.summary_text.get('1.0', tk.END) + "\n")
                
                f.write("DETALHES POR COLUNA:\n")
                # Cabeçalhos
                headers = [self.tree.heading(col)["text"] for col in self.tree['columns']]
                f.write("\t".join(headers) + "\n")
                f.write("="*80 + "\n")
                # Dados
                for child_id in self.tree.get_children():
                    values = self.tree.item(child_id)['values']
                    f.write("\t".join(map(str, values)) + "\n")

            messagebox.showinfo("Sucesso", f"Relatório salvo com sucesso em:\n{report_path}")
            self.app.log(f"Relatório de análise exportado para {report_path}")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o relatório:\n{e}")

