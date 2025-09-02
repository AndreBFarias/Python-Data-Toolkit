import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .base_tab import BaseTab

class VisualizerTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.fig = None
        self.canvas = None
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- SEÇÃO: FICHEIRO DE ORIGEM ---
        file_frame = ttk.LabelFrame(main_frame, text="Ficheiro de Origem", padding=(15, 10))
        file_frame.pack(fill='x', pady=(0, 20))
        self.btn_select_file = ttk.Button(file_frame, text="Selecionar Arquivo para Visualização...", command=self.handle_file_selection)
        self.btn_select_file.pack(side="left", padx=(0, 10))
        self.lbl_filepath = ttk.Label(file_frame, text="Nenhum arquivo selecionado.")
        self.lbl_filepath.pack(side="left", fill='x', expand=True)

        # --- SEÇÃO PRINCIPAL: CONFIGURAÇÃO E VISUALIZAÇÃO ---
        viz_main_frame = ttk.Frame(main_frame)
        viz_main_frame.pack(fill='both', expand=True, pady=(0, 10))
        viz_main_frame.columnconfigure(1, weight=1) # A área do gráfico expande
        viz_main_frame.rowconfigure(0, weight=1)

        # Painel de Controlo (Esquerda)
        controls_frame = ttk.LabelFrame(viz_main_frame, text="Configuração do Gráfico", padding=(15, 10))
        controls_frame.grid(row=0, column=0, sticky='ns', padx=(0, 20))

        # Seletor de Tipo de Gráfico
        ttk.Label(controls_frame, text="Tipo de Gráfico:", font=('Inter', 10, 'bold')).pack(anchor='w', pady=(0,5))
        self.chart_type_var = tk.StringVar()
        self.chart_type_combo = ttk.Combobox(controls_frame, textvariable=self.chart_type_var, state='disabled',
                                             values=["Barras", "Linha", "Pizza", "Dispersão", "Histograma"])
        self.chart_type_combo.pack(fill='x', pady=(0, 20))
        self.chart_type_combo.bind("<<ComboboxSelected>>", self.on_chart_type_change)

        # Frame dinâmico para as opções de cada gráfico
        self.dynamic_options_frame = ttk.Frame(controls_frame)
        self.dynamic_options_frame.pack(fill='x', expand=True)
        
        # Botão de Gerar/Atualizar
        self.btn_generate = ttk.Button(controls_frame, text="Gerar Gráfico", command=self.generate_chart, state='disabled')
        self.btn_generate.pack(fill='x', pady=(20, 0))
        
        # Área do Gráfico (Direita)
        canvas_outer_frame = ttk.LabelFrame(viz_main_frame, text="Visualização", padding=(15, 10))
        canvas_outer_frame.grid(row=0, column=1, sticky='nsew')
        self.canvas_frame = ttk.Frame(canvas_outer_frame) # Frame interno para o canvas
        self.canvas_frame.pack(fill='both', expand=True)

        # --- SEÇÃO: AÇÃO ---
        action_frame = ttk.LabelFrame(main_frame, text="Ação", padding=(15, 10))
        action_frame.pack(fill='x', pady=(10, 0))
        self.btn_save = ttk.Button(action_frame, text="Salvar Gráfico Como Imagem...", command=self.save_chart, state='disabled', style='Accent.TButton')
        self.btn_save.pack(fill='x')

    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:
                self.chart_type_combo.config(state='readonly')
                self.app.log("Ficheiro carregado. Selecione um tipo de gráfico.")

    def on_chart_type_change(self, event=None):
        for widget in self.dynamic_options_frame.winfo_children():
            widget.destroy()

        chart_type = self.chart_type_var.get()
        self.btn_generate.config(state='normal')
        
        # Cria as comboboxes necessárias para cada tipo de gráfico
        if chart_type in ["Barras", "Linha", "Dispersão"]:
            self.create_combo("Eixo X:", "x_col_var")
            self.create_combo("Eixo Y:", "y_col_var")
        elif chart_type == "Pizza":
            self.create_combo("Coluna de Rótulos:", "label_col_var")
            self.create_combo("Coluna de Valores:", "value_col_var")
        elif chart_type == "Histograma":
            self.create_combo("Coluna:", "hist_col_var")
    
    def create_combo(self, label_text, var_name):
        frame = ttk.Frame(self.dynamic_options_frame)
        frame.pack(fill='x', pady=5)
        ttk.Label(frame, text=label_text).pack(anchor='w')
        var = tk.StringVar()
        setattr(self, var_name, var)
        combo = ttk.Combobox(frame, textvariable=var, state='readonly', values=list(self.df.columns))
        combo.pack(fill='x')
        
    def generate_chart(self):
        if self.df is None: return
        
        chart_type = self.chart_type_var.get()
        if not chart_type:
            messagebox.showwarning("Aviso", "Selecione um tipo de gráfico.")
            return

        # Limpa o canvas anterior
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        plt.close('all')

        # Configura a estética do Seaborn
        sns.set_theme(style="whitegrid", rc={
            "axes.facecolor": self.app.ALT_BG,
            "figure.facecolor": self.app.BG_COLOR,
            "grid.color": "#44475a",
            "xtick.color": self.app.FG_COLOR,
            "ytick.color": self.app.FG_COLOR,
            "axes.labelcolor": self.app.FG_COLOR,
            "axes.edgecolor": "#44475a",
            "text.color": self.app.FG_COLOR,
        })
        
        self.fig, ax = plt.subplots()

        try:
            if chart_type == "Barras":
                x, y = self.x_col_var.get(), self.y_col_var.get()
                sns.barplot(data=self.df, x=x, y=y, ax=ax, color=self.app.ACCENT_COLOR)
            elif chart_type == "Linha":
                x, y = self.x_col_var.get(), self.y_col_var.get()
                sns.lineplot(data=self.df, x=x, y=y, ax=ax, color=self.app.ACCENT_COLOR)
            elif chart_type == "Pizza":
                labels, values = self.label_col_var.get(), self.value_col_var.get()
                data = self.df.groupby(labels)[values].sum()
                ax.pie(data, labels=data.index, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
            elif chart_type == "Dispersão":
                x, y = self.x_col_var.get(), self.y_col_var.get()
                sns.scatterplot(data=self.df, x=x, y=y, ax=ax, color=self.app.ACCENT_COLOR)
            elif chart_type == "Histograma":
                col = self.hist_col_var.get()
                sns.histplot(data=self.df, x=col, kde=True, ax=ax, color=self.app.ACCENT_COLOR)

            plt.tight_layout()
            
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill='both', expand=True)
            self.btn_save.config(state='normal')
            self.app.log(f"Gráfico '{chart_type}' gerado com sucesso.")

        except Exception as e:
            messagebox.showerror("Erro ao Gerar Gráfico", f"Não foi possível gerar o gráfico:\n{e}")
            self.app.log(f"ERRO ao gerar gráfico: {e}")

    def save_chart(self):
        if not self.fig:
            messagebox.showwarning("Aviso", "Nenhum gráfico para salvar.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Salvar Gráfico",
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All files", "*.*")],
        )
        if filepath:
            try:
                self.fig.savefig(filepath, facecolor=self.fig.get_facecolor(), dpi=150)
                messagebox.showinfo("Sucesso", f"Gráfico salvo com sucesso em:\n{filepath}")
                self.app.log(f"Gráfico salvo em {filepath}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o gráfico:\n{e}")

