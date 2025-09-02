import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import re
import json
import unicodedata
import threading
from dotenv import load_dotenv
import google.generativeai as genai
from .base_tab import BaseTab

class ETLPreparerTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.processed_df = None
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)

        # --- PAINEL DE CONTROLO (ESQUERDA) ---
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 20))

        # 1. Ficheiro de Origem
        file_frame = ttk.LabelFrame(controls_frame, text="Ficheiro de Origem", padding=(15, 10))
        file_frame.pack(fill='x', pady=(0, 20))
        self.btn_select_file = ttk.Button(file_frame, text="Selecionar Arquivo...", command=self.handle_file_selection)
        self.btn_select_file.pack(fill='x')
        self.lbl_filepath = ttk.Label(file_frame, text="Nenhum arquivo selecionado.", wraplength=250)
        self.lbl_filepath.pack(fill='x', pady=(5,0))

        # 2. Rituais de Purificação
        purify_frame = ttk.LabelFrame(controls_frame, text="Rituais de Purificação", padding=(15, 10))
        purify_frame.pack(fill='x', pady=(0, 20))
        self.sanitize_headers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(purify_frame, text="Sanear nomes das colunas", variable=self.sanitize_headers_var).pack(anchor='w')
        self.remove_empty_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(purify_frame, text="Remover colunas e linhas vazias", variable=self.remove_empty_var).pack(anchor='w')

        # 3. Opções de Pré-visualização
        preview_opts_frame = ttk.LabelFrame(controls_frame, text="Opções de Pré-visualização", padding=(15, 10))
        preview_opts_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(preview_opts_frame, text="Nº de linhas para visualizar:").pack(side='left', padx=(0,10))
        self.preview_rows_var = tk.IntVar(value=5)
        ttk.Spinbox(preview_opts_frame, from_=1, to=100, textvariable=self.preview_rows_var, width=5).pack(side='left')

        # 4. Invocação
        invoke_frame = ttk.LabelFrame(controls_frame, text="Invocação da IA", padding=(15, 10))
        invoke_frame.pack(fill='x', pady=(0, 20))
        self.status_label = ttk.Label(invoke_frame, text="Aguardando ficheiro...")
        self.status_label.pack(fill='x', pady=(0,10))
        self.btn_invoke = ttk.Button(invoke_frame, text="Analisar Tabela com IA", command=self.start_ai_analysis, style="Accent.TButton", state='disabled')
        self.btn_invoke.pack(fill='x')

        # --- PAINEL DE RESULTADOS (DIREITA) ---
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=0, column=1, sticky='nsew')
        results_frame.rowconfigure(1, weight=1)
        results_frame.columnconfigure(0, weight=1)

        # 1. Pré-visualização
        preview_frame = ttk.LabelFrame(results_frame, text="Pré-visualização dos Dados Tratados", padding=(15, 10))
        preview_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        
        tree_container = ttk.Frame(preview_frame)
        tree_container.pack(fill='both', expand=True)
        self.preview_tree = ttk.Treeview(tree_container, show="headings", height=5)
        
        xsb = ttk.Scrollbar(tree_container, orient='horizontal', command=self.preview_tree.xview)
        ysb = ttk.Scrollbar(tree_container, orient='vertical', command=self.preview_tree.yview)
        self.preview_tree.configure(xscrollcommand=xsb.set, yscrollcommand=ysb.set)

        ysb.pack(side='right', fill='y')
        xsb.pack(side='bottom', fill='x')
        self.preview_tree.pack(side='left', fill='both', expand=True)

        # 2. Schemas
        schemas_notebook = ttk.Notebook(results_frame, style='TNotebook')
        schemas_notebook.grid(row=1, column=0, sticky='nsew', pady=(0, 20))
        
        bq_frame = ttk.Frame(schemas_notebook, padding=10)
        schemas_notebook.add(bq_frame, text="Schema BigQuery (JSON)")
        self.bq_schema_text = tk.Text(bq_frame, wrap="none", height=10, relief='flat', background=self.app.ALT_BG, foreground=self.app.FG_COLOR)
        self.bq_schema_text.pack(fill='both', expand=True)

        dbt_frame = ttk.Frame(schemas_notebook, padding=10)
        schemas_notebook.add(dbt_frame, text="Schema dbt (YML)")
        self.dbt_schema_text = tk.Text(dbt_frame, wrap="none", height=10, relief='flat', background=self.app.ALT_BG, foreground=self.app.FG_COLOR)
        self.dbt_schema_text.pack(fill='both', expand=True)

        # 3. Descrição
        desc_frame = ttk.LabelFrame(results_frame, text="Descrição da Tabela (sugerida pela IA)", padding=(15, 10))
        desc_frame.grid(row=2, column=0, sticky='ew')
        self.description_text = tk.Text(desc_frame, wrap="word", height=4, relief='flat', background=self.app.ALT_BG, foreground=self.app.FG_COLOR)
        self.description_text.pack(fill='x', expand=True)

        # 4. Ação Final
        final_action_frame = ttk.LabelFrame(main_frame, text="Consagração Final", padding=(15, 10))
        final_action_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(20, 0))
        self.btn_save = ttk.Button(final_action_frame, text="Salvar CSV Tratado e Schemas...", command=self.save_artifacts, state='disabled')
        self.btn_save.pack(fill='x')

    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_filepath):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:
                self.btn_invoke.config(state='normal')
                self.status_label.config(text="Pronto para análise.")
                self.app.log("Ficheiro carregado. Pode iniciar a análise.")
                # Pré-purifica e mostra a pré-visualização inicial
                self.run_purification()
                self.update_preview_tree(self.processed_df)

    def start_ai_analysis(self):
        self.status_label.config(text="Analisando... Por favor, aguarde.")
        self.btn_invoke.config(state='disabled')
        self.btn_save.config(state='disabled')
        analysis_thread = threading.Thread(target=self.invoke_ai_analysis)
        analysis_thread.start()

    def run_purification(self):
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
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                messagebox.showerror("Erro de Configuração", "A variável de ambiente GEMINI_API_KEY não foi encontrada.\n\nCrie um ficheiro .env na pasta do projeto e adicione a linha:\nGEMINI_API_KEY='sua_chave_aqui'")
                self.status_label.config(text="Erro: Chave de API não encontrada.")
                return

            genai.configure(api_key=api_key)
            # CORREÇÃO: Usar um modelo atualizado e disponível como 'gemini-1.5-flash-latest'
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
            self.btn_save.config(state='normal')
            self.status_label.config(text="Análise concluída com sucesso.")

        except Exception as e:
            messagebox.showerror("Erro na Análise com IA", f"Ocorreu um erro: {e}")
            self.status_label.config(text="Erro durante a análise.")
            self.app.log(f"ERRO na análise com IA: {e}")
        finally:
            self.btn_invoke.config(state='normal')

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
        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', schema_data.get("table_description", "Nenhuma descrição gerada."))

        bq_schema = [{"name": c["name"], "type": c["type"], "description": c["description"], "mode": "NULLABLE"} for c in schema_data["columns"]]
        self.bq_schema_text.delete('1.0', tk.END)
        self.bq_schema_text.insert('1.0', json.dumps(bq_schema, indent=2, ensure_ascii=False))

        table_name = self.sanitize_column_name(os.path.splitext(os.path.basename(self.filepath))[0])
        dbt_yml = f"version: 2\n\nmodels:\n  - name: {table_name}\n"
        dbt_yml += f"    description: \"{schema_data.get('table_description', '')}\"\n"
        dbt_yml += "    columns:\n"
        for col in schema_data["columns"]:
            dbt_yml += f"      - name: {col['name']}\n"
            dbt_yml += f"        description: \"{col['description']}\"\n"
        
        self.dbt_schema_text.delete('1.0', tk.END)
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
        
        self.preview_tree.configure(height=len(df_head))
        for i in self.preview_tree.get_children(): self.preview_tree.delete(i)
        
        self.preview_tree["columns"] = list(df_head.columns)
        for col in df_head.columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, anchor="w", width=150)
            
        for _, row in df_head.iterrows():
            self.preview_tree.insert("", "end", values=[str(v) for v in row.fillna('')])

    def save_artifacts(self):
        if self.processed_df is None:
            messagebox.showwarning("Aviso", "Nenhum dado processado para salvar.")
            return
        
        folder_path = filedialog.askdirectory(title="Selecione a pasta para salvar os artefactos")
        if not folder_path: return
            
        base_name = self.sanitize_column_name(os.path.splitext(os.path.basename(self.filepath))[0])

        try:
            csv_path = os.path.join(folder_path, f"{base_name}.csv")
            self.processed_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            self.app.log(f"CSV tratado salvo em {csv_path}")

            bq_path = os.path.join(folder_path, "schema_bq.json")
            with open(bq_path, 'w', encoding='utf-8') as f:
                f.write(self.bq_schema_text.get('1.0', tk.END))
            self.app.log(f"Schema BigQuery salvo em {bq_path}")

            dbt_path = os.path.join(folder_path, f"{base_name}.yml")
            with open(dbt_path, 'w', encoding='utf-8') as f:
                f.write(self.dbt_schema_text.get('1.0', tk.END))
            self.app.log(f"Schema dbt salvo em {dbt_path}")

            messagebox.showinfo("Sucesso", f"Todos os artefactos foram salvos com sucesso na pasta:\n{folder_path}")

        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar os ficheiros:\n{e}")


