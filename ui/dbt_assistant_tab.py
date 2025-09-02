import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading
import yaml
import json
from dotenv import load_dotenv
import google.generativeai as genai
from .base_tab import BaseTab

class DBTAssistantTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.sql_files_map = {}
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        # --- PAINEL DE CONTROLO (ESQUERDA) ---
        controls_frame = ttk.Frame(main_frame, width=350)
        controls_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 20))

        # 1. Configuração do Repositório
        repo_frame = ttk.LabelFrame(controls_frame, text="Configuração do Repositório", padding=(15, 10))
        repo_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(repo_frame, text="Caminho do Projeto 'pipelines':").pack(anchor='w')
        self.repo_path_var = tk.StringVar()
        entry_repo = ttk.Entry(repo_frame, textvariable=self.repo_path_var, state='readonly')
        entry_repo.pack(fill='x', expand=True, pady=(0,5))
        ttk.Button(repo_frame, text="Selecionar Pasta do Projeto...", command=self.select_repo_path).pack(fill='x')
        
        ttk.Label(repo_frame, text="Subpasta de Destino (models):").pack(anchor='w', pady=(10,0))
        self.models_path_var = tk.StringVar()
        self.models_combo = ttk.Combobox(repo_frame, textvariable=self.models_path_var, state='readonly')
        self.models_combo.pack(fill='x', expand=True, pady=(0,5))

        ttk.Label(repo_frame, text="Ficheiro schema.yml Principal:").pack(anchor='w', pady=(10,0))
        self.schema_path_var = tk.StringVar()
        entry_schema = ttk.Entry(repo_frame, textvariable=self.schema_path_var, state='readonly')
        entry_schema.pack(fill='x', expand=True, pady=(0,5))
        ttk.Button(repo_frame, text="Selecionar schema.yml...", command=self.select_schema_path).pack(fill='x')

        # 2. Etapa 1: Criação da Branch
        branch_frame = ttk.LabelFrame(controls_frame, text="Etapa 1: Comandos para Branch", padding=(15, 10))
        branch_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(branch_frame, text="Nome da Feature:").pack(anchor='w')
        self.feature_name_var = tk.StringVar()
        self.feature_name_var.trace("w", self.update_git_commands)
        ttk.Entry(branch_frame, textvariable=self.feature_name_var).pack(fill='x', pady=(0,10))
        
        self.git_commands_text = tk.Text(branch_frame, height=4, wrap='word', relief='flat', background=self.app.ALT_BG, foreground=self.app.FG_COLOR)
        self.git_commands_text.pack(fill='x', expand=True)

        # --- PAINEL PRINCIPAL (DIREITA) ---
        main_panel_frame = ttk.Frame(main_frame)
        main_panel_frame.grid(row=0, column=1, sticky='nsew')
        
        notebook = ttk.Notebook(main_panel_frame, style='TNotebook')
        notebook.pack(fill='both', expand=True)
        
        prep_tab = ttk.Frame(notebook, padding=15)
        notebook.add(prep_tab, text="Preparação e Versionamento")
        prep_tab.columnconfigure(0, weight=1)
        prep_tab.rowconfigure(1, weight=1)

        # 3. Etapa 2: Preparação das Consultas
        sql_frame = ttk.LabelFrame(prep_tab, text="Etapa 2: Preparação das Consultas", padding=(15, 10))
        sql_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        ttk.Button(sql_frame, text="Selecionar Ficheiros SQL...", command=self.select_sql_files).pack(fill='x')

        # 4. Etapa 3: Edição e Documentação
        edit_frame = ttk.LabelFrame(prep_tab, text="Etapa 3: Edição e Documentação com IA", padding=(15, 10))
        edit_frame.grid(row=1, column=0, sticky='nsew')
        edit_frame.rowconfigure(1, weight=1)
        edit_frame.columnconfigure(0, weight=3)
        edit_frame.columnconfigure(1, weight=2)
        
        self.sql_listbox = tk.Listbox(edit_frame, height=5, background=self.app.ALT_BG, foreground=self.app.FG_COLOR, relief='flat')
        self.sql_listbox.grid(row=0, column=0, sticky='nsew', columnspan=2, pady=(0,10))
        self.sql_listbox.bind('<<ListboxSelect>>', self.on_sql_file_select)

        self.sql_editor_text = tk.Text(edit_frame, wrap="none", relief='flat', background=self.app.ALT_BG, foreground=self.app.FG_COLOR)
        self.sql_editor_text.grid(row=1, column=0, sticky='nsew', padx=(0,10))
        
        self.yml_editor_text = tk.Text(edit_frame, wrap="none", relief='flat', background=self.app.ALT_BG, foreground=self.app.FG_COLOR)
        self.yml_editor_text.grid(row=1, column=1, sticky='nsew')
        
        self.btn_generate_doc = ttk.Button(edit_frame, text="Gerar Documentação com IA", command=self.start_documentation_generation, state='disabled')
        self.btn_generate_doc.grid(row=2, column=1, sticky='ew', pady=(10,0))
        
        # 5. Etapa 4: Consagração
        commit_frame = ttk.LabelFrame(prep_tab, text="Etapa 4: Versionar e Preparar Commit", padding=(15, 10))
        commit_frame.grid(row=2, column=0, sticky='ew', pady=(20,0))
        self.btn_version_files = ttk.Button(commit_frame, text="Versionar Ficheiros", command=self.version_files, style="Accent.TButton", state='disabled')
        self.btn_version_files.pack(fill='x', pady=(0,10))
        self.final_git_commands_text = tk.Text(commit_frame, height=3, wrap='word', relief='flat', background=self.app.ALT_BG, foreground=self.app.FG_COLOR)
        self.final_git_commands_text.pack(fill='x', expand=True)

        # CORREÇÃO: Chamar update_git_commands DEPOIS que todos os widgets foram criados.
        self.update_git_commands()

    def select_repo_path(self):
        repo_path = filedialog.askdirectory(title="Selecione a pasta raiz do projeto 'pipelines'")
        if repo_path and os.path.basename(repo_path):
            self.repo_path_var.set(repo_path)
            self.app.log(f"Repositório selecionado: {repo_path}")
            self.scan_for_models_dirs()

    def scan_for_models_dirs(self):
        repo_path = self.repo_path_var.get()
        if not repo_path: return
        models_dirs = [os.path.join(r, d) for r, ds, _ in os.walk(repo_path) for d in ds if d == 'models']
        relative_paths = [os.path.relpath(d, repo_path) for d in models_dirs]
        self.models_combo['values'] = relative_paths
        self.models_combo.config(state='readonly')
        if relative_paths:
            self.models_combo.set(relative_paths[0])
            self.app.log(f"Subpastas 'models' encontradas: {len(relative_paths)}")
            
    def select_schema_path(self):
        initial_dir = self.repo_path_var.get() or os.path.expanduser("~")
        schema_path = filedialog.askopenfilename(
            title="Selecione o ficheiro schema.yml principal",
            filetypes=[("YAML files", "*.yml")],
            initialdir=initial_dir
        )
        if schema_path:
            self.schema_path_var.set(schema_path)
            self.app.log(f"Ficheiro schema.yml selecionado: {schema_path}")

    def update_git_commands(self, *args):
        feature_name = self.feature_name_var.get()
        branch_name = f"feature/{feature_name}" if feature_name else "feature/<nome_da_branch>"
        commands = f"git checkout develop\ngit pull\ngit checkout -b {branch_name}"
        self.git_commands_text.delete('1.0', tk.END)
        self.git_commands_text.insert('1.0', commands)

        final_commands = f"git add .\ngit commit -m \"feat(painel): adiciona modelo para {feature_name}\""
        self.final_git_commands_text.delete('1.0', tk.END)
        self.final_git_commands_text.insert('1.0', final_commands)

    def select_sql_files(self):
        files = filedialog.askopenfilenames(title="Selecione as suas consultas SQL", filetypes=[("SQL files", "*.sql")])
        if files:
            self.sql_listbox.delete(0, tk.END)
            self.sql_files_map = {os.path.basename(f): f for f in files}
            for basename in self.sql_files_map.keys():
                self.sql_listbox.insert(tk.END, basename)
            self.app.log(f"{len(files)} ficheiros SQL selecionados.")

    def on_sql_file_select(self, event):
        selection_indices = self.sql_listbox.curselection()
        if not selection_indices: return
        
        selected_basename = self.sql_listbox.get(selection_indices[0])
        filepath = self.sql_files_map.get(selected_basename)
        
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.sql_editor_text.delete('1.0', tk.END)
                self.sql_editor_text.insert('1.0', content)
                self.btn_generate_doc.config(state='normal')
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível ler o ficheiro:\n{e}")

    def start_documentation_generation(self):
        self.btn_generate_doc.config(state='disabled')
        threading.Thread(target=self.generate_documentation).start()

    def generate_documentation(self):
        self.app.log("Invocando IA para gerar documentação...")
        sql_query = self.sql_editor_text.get('1.0', tk.END)
        if not sql_query.strip():
            messagebox.showwarning("Aviso", "O editor de SQL está vazio.")
            self.btn_generate_doc.config(state='normal')
            return

        try:
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                messagebox.showerror("Erro", "Chave de API do Gemini não encontrada no ficheiro .env")
                return

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            prompt = self.build_prompt(sql_query)
            response = model.generate_content(prompt)
            
            response_text = response.text.strip().replace("```json", "").replace("```", "")
            doc_data = json.loads(response_text)
            
            yml_snippet = self.format_as_yml(doc_data)
            self.yml_editor_text.delete('1.0', tk.END)
            self.yml_editor_text.insert('1.0', yml_snippet)
            self.app.log("Documentação gerada com sucesso.")
            self.btn_version_files.config(state='normal')
        except Exception as e:
            messagebox.showerror("Erro na Geração", f"Ocorreu um erro ao comunicar com a IA:\n{e}")
            self.app.log(f"ERRO na geração de documentação: {e}")
        finally:
            self.btn_generate_doc.config(state='normal')

    def build_prompt(self, sql_query):
        return f"""
        Analise a seguinte consulta SQL de um modelo dbt:
        ---
        {sql_query}
        ---
        Sua tarefa é atuar como um engenheiro de dados especialista em dbt e gerar a documentação para este modelo em português do Brasil.
        Você deve gerar:
        1. Uma descrição concisa e informativa para o modelo como um todo.
        2. Uma descrição para cada coluna exposta no `SELECT` final da consulta.
        Retorne a sua resposta APENAS no seguinte formato JSON, sem nenhum texto ou formatação adicional:
        {{
          "model_description": "Descrição geral do modelo aqui.",
          "columns": [
            {{"name": "nome_da_coluna_1", "description": "Descrição da coluna 1."}},
            {{"name": "nome_da_coluna_2", "description": "Descrição da coluna 2."}}
          ]
        }}
        """
    
    def format_as_yml(self, doc_data):
        selection_indices = self.sql_listbox.curselection()
        if not selection_indices: return "# Selecione um ficheiro SQL"
        
        base_name = os.path.basename(self.sql_listbox.get(selection_indices[0]))
        model_name = f"painel_{os.path.splitext(base_name)[0]}"
        
        yml = f"  - name: {model_name}\n"
        yml += f"    description: \"{doc_data.get('model_description', '')}\"\n"
        yml += "    columns:\n"
        for col in doc_data.get('columns', []):
            yml += f"      - name: {col['name']}\n"
            yml += f"        description: \"{col['description']}\"\n"
        return yml

    def version_files(self):
        self.app.log("Iniciando processo de versionamento...")
        models_path = os.path.join(self.repo_path_var.get(), self.models_path_var.get())
        schema_path = self.schema_path_var.get()
        yml_content_to_append = self.yml_editor_text.get('1.0', tk.END)

        if not all([self.repo_path_var.get(), self.models_path_var.get(), schema_path, self.sql_files_map, yml_content_to_append.strip()]):
            messagebox.showerror("Erro", "Verifique se todas as configurações, ficheiros SQL e documentação estão preenchidos.")
            return

        try:
            # 1. Copiar e renomear ficheiros SQL
            for basename, original_path in self.sql_files_map.items():
                new_name = f"painel_{basename}"
                dest_path = os.path.join(models_path, new_name)
                
                # Usar o conteúdo do editor, que pode ter sido modificado
                content = self.sql_editor_text.get('1.0', tk.END)

                with open(dest_path, 'w', encoding='utf-8') as f_write:
                    f_write.write(content)
                self.app.log(f"Ficheiro salvo em {dest_path}")
            
            # 2. Anexar ao schema.yml
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_data = yaml.safe_load(f) or {}
            
            # Garante que a estrutura base do YML existe
            if 'version' not in schema_data: schema_data['version'] = 2
            if 'models' not in schema_data: schema_data['models'] = []

            # Carrega o trecho gerado como um objeto Python
            new_model_data_list = yaml.safe_load(yml_content_to_append)
            
            # Adiciona os novos modelos à lista existente
            schema_data['models'].extend(new_model_data_list)

            with open(schema_path, 'w', encoding='utf-8') as f:
                yaml.dump(schema_data, f, allow_unicode=True, sort_keys=False, indent=2)

            self.app.log(f"Schema.yml ({schema_path}) atualizado com sucesso.")
            messagebox.showinfo("Sucesso", "Ficheiros versionados e schema atualizado!\nPode agora fazer o commit.")

        except Exception as e:
            messagebox.showerror("Erro no Versionamento", f"Ocorreu um erro: {e}")
            self.app.log(f"ERRO no versionamento: {e}")


