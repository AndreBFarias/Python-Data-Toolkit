import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import re
import json
import unicodedata
import threading
from dotenv import load_dotenv
import google.generativeai as genai
from .base_tab import BaseTab
from ui import theme
from ui.custom_widgets import EntryWithContextMenu, TextboxWithContextMenu


class ETLPreparerTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.processed_df = None
        self.create_widgets()
        self.style_treeview()

    def create_widgets(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- PAINEL DE CONTROLES (ESQUERDA) ---
        controls_frame = ctk.CTkFrame(self, width=300, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        controls_frame.grid(row=0, column=0, sticky='nsw', padx=(0, theme.padding["widget_x"]), pady=0)
        
        ctk.CTkLabel(controls_frame, text="Controles", font=theme.fonts["h1"]).pack(anchor='w', padx=15, pady=(15,10))
        
#4
        self.btn_select_file = ctk.CTkButton(controls_frame, text="Selecionar Arquivo...", font=theme.fonts["button"], command=self.handle_file_selection, fg_color=theme.colors["comment"])
        self.btn_select_file.pack(fill='x', padx=15, pady=5)
#4
        self.lbl_filepath = ctk.CTkLabel(controls_frame, text="Nenhum arquivo selecionado.", wraplength=250, font=theme.fonts["body"], text_color=theme.colors["comment"])
        self.lbl_filepath.pack(fill='x', padx=15, pady=(0,10))

        ctk.CTkLabel(controls_frame, text="Rituais de Purificação", font=theme.fonts["body"]).pack(anchor='w', padx=15, pady=(10,5))
        self.sanitize_headers_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(controls_frame, text="Sanear nomes das colunas", variable=self.sanitize_headers_var, font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"]).pack(anchor='w', padx=15)
        self.remove_empty_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(controls_frame, text="Remover colunas e linhas vazias", variable=self.remove_empty_var, font=theme.fonts["body"], border_color=theme.colors["comment"], hover_color=theme.colors["accent"]).pack(anchor='w', padx=15, pady=5)
        
        preview_opts_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        preview_opts_frame.pack(fill='x', padx=15, pady=(10,5))
        ctk.CTkLabel(preview_opts_frame, text="Nº de linhas para visualizar:", font=theme.fonts["body"]).pack(side='left')
        self.preview_rows_var = ctk.IntVar(value=5)
        EntryWithContextMenu(preview_opts_frame, textvariable=self.preview_rows_var, width=50, fg_color=theme.colors["background"], border_color=theme.colors["comment"]).pack(side='left', padx=10)

        # --- CORREÇÃO DE ALINHAMENTO ---
        # Frame espaçador que empurra os widgets abaixo para o fundo
        spacer_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        spacer_frame.pack(fill='y', expand=True)

#4
        self.status_label = ctk.CTkLabel(controls_frame, text="Aguardando arquivo...", font=theme.fonts["body"], text_color=theme.colors["comment"])
        self.status_label.pack(fill='x', padx=15, pady=(15,5))
        self.btn_invoke = ctk.CTkButton(controls_frame, text="Analisar Tabela com IA", font=theme.fonts["button"], command=self.start_ai_analysis, state='disabled', fg_color=theme.colors["accent"], text_color=theme.colors["background"], hover_color=theme.colors["pink"])
        self.btn_invoke.pack(fill='x', padx=15, pady=(0,15))

        # --- PAINEL DE RESULTADOS (DIREITA) ---
        results_frame = ctk.CTkFrame(self, fg_color="transparent")
        results_frame.grid(row=0, column=1, sticky='nsew', padx=(theme.padding["widget_x"], 0), pady=0)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        preview_frame = ctk.CTkFrame(results_frame, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        preview_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        ctk.CTkLabel(preview_frame, text="Pré-visualização dos Dados Tratados", font=theme.fonts["h1"]).pack(anchor='w', padx=15, pady=(15,10))
        tree_container = ctk.CTkFrame(preview_frame, fg_color=theme.colors["background"])
        tree_container.pack(fill='both', expand=True, padx=15, pady=(0,15))
        self.preview_tree = ttk.Treeview(tree_container, show="headings", height=5)
        self.preview_tree.pack(fill='both', expand=True, padx=1, pady=1)
        
        schemas_frame = ctk.CTkFrame(results_frame, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        schemas_frame.grid(row=1, column=0, sticky='nsew', pady=(0,15))
        schemas_frame.rowconfigure(1, weight=1)
        schemas_frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(schemas_frame, text="Schemas Sugeridos pela IA", font=theme.fonts["h1"]).grid(row=0, column=0, sticky='w', padx=15, pady=(15,10))
        
        self.tab_view = ctk.CTkTabview(schemas_frame, text_color=theme.colors["foreground"], fg_color=theme.colors["background"], segmented_button_fg_color=theme.colors["background"], segmented_button_selected_color=theme.colors["accent"], segmented_button_unselected_color=theme.colors["sidebar"])
        self.tab_view.grid(row=1, column=0, sticky='nsew', padx=15, pady=(0,15))
        self.tab_view.add("Schema BigQuery (JSON)")
        self.tab_view.add("Schema dbt (YML)")
        
        self.bq_schema_text = TextboxWithContextMenu(self.tab_view.tab("Schema BigQuery (JSON)"), wrap="none", corner_radius=8, fg_color=theme.colors["background"], border_color=theme.colors["comment"], border_width=1)
        self.bq_schema_text.pack(fill='both', expand=True)
        self.dbt_schema_text = TextboxWithContextMenu(self.tab_view.tab("Schema dbt (YML)"), wrap="none", corner_radius=8, fg_color=theme.colors["background"], border_color=theme.colors["comment"], border_width=1)
        self.dbt_schema_text.pack(fill='both', expand=True)
        
        desc_frame = ctk.CTkFrame(results_frame, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        desc_frame.grid(row=2, column=0, sticky='ew')
        ctk.CTkLabel(desc_frame, text="Descrição da Tabela (sugerida pela IA)", font=theme.fonts["h1"]).pack(anchor='w', padx=15, pady=(15,10))
        self.description_text = TextboxWithContextMenu(desc_frame, wrap="word", height=100, corner_radius=8, fg_color=theme.colors["background"], border_color=theme.colors["comment"], border_width=1)
        self.description_text.pack(fill='x', expand=True, padx=15, pady=(0,15))
        
        final_action_frame = ctk.CTkFrame(self, fg_color="transparent")
        final_action_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=15)
        self.btn_save = ctk.CTkButton(final_action_frame, text="Salvar CSV Tratado e Schemas...", font=theme.fonts["button"], command=self.save_artifacts, state='disabled', fg_color=theme.colors["green"], text_color=theme.colors["background"], hover_color="#81F9A1")
        self.btn_save.pack(fill='x', padx=0, pady=0)
        
    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=theme.colors["background"], foreground=theme.colors["foreground"], fieldbackground=theme.colors["background"], rowheight=25, borderwidth=0)
        style.map("Treeview", background=[('selected', theme.colors["accent"])])
        style.configure("Treeview.Heading", background=theme.colors["sidebar"], foreground=theme.colors["accent"], font=theme.fonts["button"], relief="flat", borderwidth=0)
        style.map("Treeview.Heading", background=[('active', theme.colors["comment"])])
    
    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:
                self.btn_invoke.configure(state='normal')
                self.status_label.configure(text="Pronto para análise.")
#4
                self.app.log("Arquivo carregado. Pode iniciar a análise.")
                self.run_purification()
                self.update_preview_tree(self.processed_df)

    def start_ai_analysis(self):
        self.status_label.configure(text="Analisando... Por favor, aguarde.")
        self.btn_invoke.configure(state='disabled')
        self.btn_save.configure(state='disabled')
        analysis_thread = threading.Thread(target=self.invoke_ai_analysis)
        analysis_thread.start()

    def run_purification(self):
        if self.df is None: return
        self.app.log("Iniciando purificação dos dados...")
        df = self.df.copy()
        if self.remove_empty_var.get():
            df.dropna(how='all', inplace=True)
            df.dropna(axis=1, how='all', inplace=True)
        if self.sanitize_headers_var.get():
            df.columns = [self.sanitize_column_name(c) for c in df.columns]
        self.processed_df = df
        self.app.log("Purificação concluída.")
        return self.processed_df

    def invoke_ai_analysis(self):
        try:
            api_key = self.app.config_manager.get("gemini_api_key")
            if not api_key:
                load_dotenv()
                api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
#4
                messagebox.showerror("Erro de Configuração", "Chave de API do Gemini não encontrada.\n\nPor favor, adicione a chave na aba 'Configurações' ou num arquivo .env (GEMINI_API_KEY='sua_chave').")
                self.status_label.configure(text="Erro: Chave de API não encontrada.")
                return
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            self.run_purification()
            self.update_preview_tree(self.processed_df)
            self.app.log("Preparando dados para a IA...")
            sample_data = self.processed_df.head(20).to_string()
            prompt = self.build_prompt(self.processed_df.columns, sample_data)
            self.app.log("Invocando o Oráculo Gemini...")
            response = model.generate_content(prompt)
            self.app.log("Traduzindo as profecias do Oráculo...")
            response_text = response.text.strip().replace("```json", "").replace("```", "")
            schema_data = json.loads(response_text)
            self.populate_results(schema_data)
            self.btn_save.configure(state='normal')
            self.status_label.configure(text="Análise concluída com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro na Análise com IA", f"Ocorreu um erro: {e}")
            self.status_label.configure(text="Erro durante a análise.")
            self.app.log(f"ERRO na análise com IA: {e}")
        finally:
            self.btn_invoke.configure(state='normal')

    def build_prompt(self, columns, sample_data):
        return f"""
        Analise a seguinte amostra de uma tabela com as colunas {list(columns)} e os dados:
        {sample_data}
        Sua tarefa é atuar como um engenheiro de dados especialista e gerar um schema para esta tabela.
        Para cada coluna, infira o tipo de dado mais apropriado para o Google BigQuery (escolha entre STRING, INTEGER, FLOAT, BOOLEAN, DATE, TIMESTAMP).
        Para cada coluna, escreva uma descrição concisa e informativa em português do Brasil.
        Gere também uma descrição geral para a tabela, explicando seu propósito principal.
        Retorne a sua resposta APENAS no seguinte formato JSON, sem nenhum texto ou formatação adicional:
        {{
          "table_description": "Descrição geral da tabela aqui.",
          "columns": [
            {{
              "name": "nome_da_coluna_1",
              "type": "BIGQUERY_TYPE",
              "description": "Descrição da coluna 1."
            }},
            {{
              "name": "nome_da_coluna_2",
              "type": "BIGQUERY_TYPE",
              "description": "Descrição da coluna 2."
            }}
          ]
        }}
        """

    def populate_results(self, schema_data):
        self.description_text.delete('1.0', ctk.END)
        self.description_text.insert('1.0', schema_data.get("table_description", "Nenhuma descrição gerada."))
        bq_schema = [{"name": c["name"], "type": c["type"], "description": c["description"], "mode": "NULLABLE"} for c in schema_data.get("columns", [])]
        self.bq_schema_text.delete('1.0', ctk.END)
        self.bq_schema_text.insert('1.0', json.dumps(bq_schema, indent=2, ensure_ascii=False))
#4
        table_name = self.sanitize_column_name(os.path.splitext(os.path.basename(self.filepath))[0]) if self.filepath else "nome_da_tabela"
        dbt_yml = f"version: 2\n\nmodels:\n  - name: {table_name}\n"
        dbt_yml += f"    description: \"{schema_data.get('table_description', '')}\"\n"
        dbt_yml += "    columns:\n"
        for col in schema_data.get("columns", []):
            dbt_yml += f"      - name: {col['name']}\n"
            dbt_yml += f"        description: \"{col['description']}\"\n"
        self.dbt_schema_text.delete('1.0', ctk.END)
        self.dbt_schema_text.insert('1.0', dbt_yml)
        self.app.log("Resultados da IA populados na interface.")

    def sanitize_column_name(self, col_name):
        nfkd_form = unicodedata.normalize('NFKD', str(col_name))
        sanitized = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        sanitized = re.sub(r'[^a-zA-Z0-9]+', '_', sanitized)
        sanitized = re.sub(r'_+', '_', sanitized).strip('_')
        return sanitized.lower()

    def update_preview_tree(self, df):
        if df is None: return
        num_rows = self.preview_rows_var.get()
        df_head = df.head(num_rows)
        for i in self.preview_tree.get_children(): self.preview_tree.delete(i)
        self.preview_tree["columns"] = list(df_head.columns)
        for col in df_head.columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, anchor="w", width=150)
        for i, row in df_head.iterrows():
            self.preview_tree.insert("", "end", values=[str(v) for v in row.fillna('')], iid=str(i))

    def save_artifacts(self):
        if self.processed_df is None:
            messagebox.showwarning("Aviso", "Nenhum dado processado para salvar.")
            return
#4
        folder_path = filedialog.askdirectory(title="Selecione a pasta para salvar os artefatos")
        if not folder_path: return
        base_name = self.sanitize_column_name(os.path.splitext(os.path.basename(self.filepath))[0])
        try:
            csv_path = os.path.join(folder_path, f"{base_name}.csv")
            self.processed_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
#4
            self.app.log(f"CSV tratado salvo em {csv_path}")
            bq_path = os.path.join(folder_path, "schema_bq.json")
            with open(bq_path, 'w', encoding='utf-8') as f:
                f.write(self.bq_schema_text.get('1.0', ctk.END))
#4
            self.app.log(f"Schema BigQuery salvo em {bq_path}")
            dbt_path = os.path.join(folder_path, f"{base_name}.yml")
            with open(dbt_path, 'w', encoding='utf-8') as f:
                f.write(self.dbt_schema_text.get('1.0', ctk.END))
#4
            self.app.log(f"Schema dbt salvo em {dbt_path}")
#4
            messagebox.showinfo("Sucesso", f"Todos os artefatos foram salvos com sucesso na pasta:\n{folder_path}")
        except Exception as e:
#4
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar os arquivos:\n{e}")
