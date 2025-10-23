import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .base_tab import BaseTab
from ui import theme

class VisualizerTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.fig = None
        self.canvas = None
        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        file_frame = ctk.CTkFrame(self, fg_color=theme.colors["sidebar"])
        file_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
#4
        self.btn_select_file = ctk.CTkButton(file_frame, text="Selecionar Arquivo para Visualização...", font=theme.fonts["button"], command=self.handle_file_selection, fg_color=theme.colors["comment"])
        self.btn_select_file.grid(row=0, column=0, padx=15, pady=15)
#4
        self.lbl_filepath = ctk.CTkLabel(file_frame, text="Nenhum arquivo selecionado.", font=theme.fonts["body"], text_color=theme.colors["comment"])
        self.lbl_filepath.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        viz_main_frame = ctk.CTkFrame(self, fg_color="transparent")
        viz_main_frame.grid(row=1, column=0, sticky='nsew', padx=5)
        viz_main_frame.columnconfigure(1, weight=1)
        viz_main_frame.rowconfigure(0, weight=1)

        controls_frame = ctk.CTkFrame(viz_main_frame, width=250, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        controls_frame.grid(row=0, column=0, sticky='nsw', padx=(0, 10))

        ctk.CTkLabel(controls_frame, text="Configuração do Gráfico", font=theme.fonts["h1"]).pack(anchor='w', padx=15, pady=(15,10))
        
        ctk.CTkLabel(controls_frame, text="Tipo de Gráfico:", font=theme.fonts["body"]).pack(anchor='w', padx=15, pady=(10,5))
        self.chart_type_var = ctk.StringVar()
        self.chart_type_combo = ctk.CTkComboBox(controls_frame, variable=self.chart_type_var, state='disabled',
                                             values=["Barras", "Linha", "Pizza", "Dispersão", "Histograma"],
                                             command=self.on_chart_type_change, button_color=theme.colors["comment"],
                                             fg_color=theme.colors["background"], border_color=theme.colors["comment"])
        self.chart_type_combo.pack(fill='x', padx=15, pady=(0, 20))

        self.dynamic_options_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        self.dynamic_options_frame.pack(fill='x', expand=True, padx=15)
        
        self.btn_generate = ctk.CTkButton(controls_frame, text="Gerar Gráfico", command=self.generate_chart, state='disabled', font=theme.fonts["button"], fg_color=theme.colors["comment"])
        self.btn_generate.pack(fill='x', padx=15, pady=20)
        
        canvas_outer_frame = ctk.CTkFrame(viz_main_frame, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        canvas_outer_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        ctk.CTkLabel(canvas_outer_frame, text="Visualização", font=theme.fonts["h1"]).pack(anchor='w', padx=15, pady=(15,10))
        self.canvas_frame = ctk.CTkFrame(canvas_outer_frame, fg_color=theme.colors["background"])
        self.canvas_frame.pack(fill='both', expand=True, padx=15, pady=(0,15))

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=15)
        action_frame.columnconfigure(0, weight=1)
        self.btn_save = ctk.CTkButton(action_frame, text="Salvar Gráfico Como Imagem...", command=self.save_chart, state='disabled', font=theme.fonts["button"], fg_color=theme.colors["green"], text_color=theme.colors["background"], hover_color="#81F9A1")
        self.btn_save.grid(row=0, column=0, sticky="ew")

    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:
                self.chart_type_combo.configure(state='readonly')
#4
                self.app.log("Arquivo carregado. Selecione um tipo de gráfico.")

    def on_chart_type_change(self, choice):
        for widget in self.dynamic_options_frame.winfo_children():
            widget.destroy()

        chart_type = self.chart_type_var.get()
        self.btn_generate.configure(state='normal')
        
        if chart_type in ["Barras", "Linha", "Dispersão"]:
            self.create_combo("Eixo X:", "x_col_var")
            self.create_combo("Eixo Y:", "y_col_var")
        elif chart_type == "Pizza":
            self.create_combo("Coluna de Rótulos:", "label_col_var")
            self.create_combo("Coluna de Valores:", "value_col_var")
        elif chart_type == "Histograma":
            self.create_combo("Coluna:", "hist_col_var")
    
    def create_combo(self, label_text, var_name):
        ctk.CTkLabel(self.dynamic_options_frame, text=label_text, font=theme.fonts["body"]).pack(anchor='w')
        var = ctk.StringVar()
        setattr(self, var_name, var)
        combo = ctk.CTkComboBox(self.dynamic_options_frame, variable=var, state='readonly', values=list(self.df.columns), button_color=theme.colors["comment"], fg_color=theme.colors["background"], border_color=theme.colors["comment"])
        combo.pack(fill='x', pady=(5,15))
        
    def generate_chart(self):
        if self.df is None: return
        
        chart_type = self.chart_type_var.get()
        if not chart_type:
            messagebox.showwarning("Aviso", "Selecione um tipo de gráfico.")
            return

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        plt.close('all')

        sns.set_theme(style="whitegrid", rc={
            "axes.facecolor": theme.colors["sidebar"],
            "figure.facecolor": theme.colors["background"],
            "grid.color": theme.colors["comment"], "grid.linestyle": ":",
            "xtick.color": theme.colors["foreground"],
            "ytick.color": theme.colors["foreground"],
            "axes.labelcolor": theme.colors["foreground"],
            "axes.edgecolor": theme.colors["comment"],
            "text.color": theme.colors["foreground"],
        })
        
        self.fig, ax = plt.subplots()

        try:
            if chart_type == "Barras":
                x, y = self.x_col_var.get(), self.y_col_var.get()
                sns.barplot(data=self.df, x=x, y=y, ax=ax, color=theme.colors["accent"])
            elif chart_type == "Linha":
                x, y = self.x_col_var.get(), self.y_col_var.get()
                sns.lineplot(data=self.df, x=x, y=y, ax=ax, color=theme.colors["accent"])
            elif chart_type == "Pizza":
                labels, values = self.label_col_var.get(), self.value_col_var.get()
                data = self.df.groupby(labels)[values].sum()
                ax.pie(data, labels=data.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("viridis", len(data)), textprops={'color': theme.colors["foreground"]})
                ax.axis('equal')
            elif chart_type == "Dispersão":
                x, y = self.x_col_var.get(), self.y_col_var.get()
                sns.scatterplot(data=self.df, x=x, y=y, ax=ax, color=theme.colors["accent"])
            elif chart_type == "Histograma":
                col = self.hist_col_var.get()
                sns.histplot(data=self.df, x=col, kde=True, ax=ax, color=theme.colors["accent"])

            plt.tight_layout()
            
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
            self.canvas.get_tk_widget().configure(bg=theme.colors["background"])
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill='both', expand=True)
            self.btn_save.configure(state='normal')
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
#4
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All files", "*.*")],
        )
        if filepath:
            try:
                self.fig.savefig(filepath, facecolor=self.fig.get_facecolor(), dpi=150)
#4
                messagebox.showinfo("Sucesso", f"Gráfico salvo com sucesso em:\n{filepath}")
#4
                self.app.log(f"Gráfico salvo em {filepath}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o gráfico:\n{e}")
