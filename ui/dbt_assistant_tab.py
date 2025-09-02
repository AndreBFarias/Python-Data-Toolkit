# Arquivo: DBTAssistantTab.py

import customtkinter as ctk
from tkinter import filedialog, messagebox, Listbox
import os
import threading
import yaml
import json
from dotenv import load_dotenv
import google.generativeai as genai
from .base_tab import BaseTab
from ui import theme
from ui.custom_widgets import EntryWithContextMenu, TextboxWithContextMenu

class DBTAssistantTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.sql_files_map = {}
        self.create_widgets()
        self.populate_initial_paths()
        
    def create_widgets(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # PAINEL DE CONTROLES (ESQUERDA)
        controls_frame = ctk.CTkFrame(self, width=350, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        controls_frame.grid(row=0, column=0, sticky='nsw', padx=(0, theme.padding["widget_x"]), pady=0)
        
        ctk.CTkLabel(controls_frame, text="Configuração do Repositório", font=theme.fonts["h1"]).pack(anchor='w', padx=15, pady=(15,10))
        
        self.repo_path_var = ctk.StringVar()
        ctk.CTkButton(controls_frame, text="Selecionar Pasta do Projeto dbt...", font=theme.fonts["button"], command=self.select_repo_path, fg_color=theme.colors["comment"]).pack(fill='x', padx=15, pady=5)
        EntryWithContextMenu(controls_frame, textvariable=self.repo_path_var, state='readonly', fg_color=theme.colors["background"], border_color=theme.colors["comment"]).pack(fill='x', expand=True, padx=15, pady=(0,10))
        
        ctk.CTkLabel(controls_frame, text="Subpasta de Destino (models):", font=theme.fonts["body"]).pack(anchor='w', padx=15)
        self.models_path_var = ctk.StringVar()
        self.models_combo = ctk.CTkComboBox(controls_frame, variable=self.models_path_var, state='readonly', button_color=theme.colors["comment"], fg_color=theme.colors["background"], border_color=theme.colors["comment"])
        self.models_combo.pack(fill='x', expand=True, padx=15, pady=(5,10))

        ctk.CTkLabel(controls_frame, text="Ficheiro schema.yml Principal:", font=theme.fonts["body"]).pack(anchor='w', padx=15)
        self.schema_path_var = ctk.StringVar()
        ctk.CTkButton(controls_frame, text="Selecionar schema.yml...", font=theme.fonts["button"], command=self.select_schema_path, fg_color=theme.colors["comment"]).pack(fill='x', padx=15, pady=5)
        EntryWithContextMenu(controls_frame, textvariable=self.schema_path_var, state='readonly', fg_color=theme.colors["background"], border_color=theme.colors["comment"]).pack(fill='x', expand=True, padx=15, pady=(0,15))

        ctk.CTkLabel(controls_frame, text="Etapa 1: Comandos para Branch", font=theme.fonts["h1"]).pack(anchor='w', padx=15, pady=(10,10))
        ctk.CTkLabel(controls_frame, text="Nome da Feature:", font=theme.fonts["body"]).pack(anchor='w', padx=15)
        self.feature_name_var = ctk.StringVar()
        self.feature_name_var.trace("w", self.update_git_commands)
        EntryWithContextMenu(controls_frame, textvariable=self.feature_name_var, fg_color=theme.colors["background"], border_color=theme.colors["comment"]).pack(fill='x', padx=15, pady=(5,10))
        self.git_commands_text = TextboxWithContextMenu(controls_frame, height=90, font=theme.fonts["code"], wrap='word', fg_color=theme.colors["background"], border_color=theme.colors["comment"], border_width=1)
        self.git_commands_text.pack(fill='x', expand=True, padx=15, pady=(0,15))

        # PAINEL PRINCIPAL (DIREITA)
        main_panel_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_panel_frame.grid(row=0, column=1, sticky='nsew', padx=(theme.padding["widget_x"], 0), pady=0)
        main_panel_frame.columnconfigure(0, weight=1)
        main_panel_frame.rowconfigure(1, weight=1)
        
        sql_frame = ctk.CTkFrame(main_panel_frame, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        sql_frame.grid(row=0, column=0, sticky='ew')
        ctk.CTkLabel(sql_frame, text="Etapa 2: Preparação das Consultas", font=theme.fonts["h1"]).pack(anchor='w', padx=15, pady=(15,10))
        ctk.CTkButton(sql_frame, text="Selecionar Ficheiros SQL...", font=theme.fonts["button"], command=self.select_sql_files, fg_color=theme.colors["comment"]).pack(fill='x', padx=15, pady=(0,15))

        edit_frame = ctk.CTkFrame(main_panel_frame, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        edit_frame.grid(row=1, column=0, sticky='nsew', pady=15)
        edit_frame.rowconfigure(2, weight=1)
        edit_frame.columnconfigure(0, weight=3)
        edit_frame.columnconfigure(1, weight=2)
        
        ctk.CTkLabel(edit_frame, text="Etapa 3: Edição e Documentação com IA", font=theme.fonts["h1"]).grid(row=0, column=0, columnspan=2, sticky='w', padx=15, pady=(15,10))
        
        self.sql_listbox = Listbox(edit_frame, height=5, background=theme.colors["background"], foreground=theme.colors["foreground"], selectbackground=theme.colors["accent"], relief='flat', borderwidth=0, highlightthickness=0, font=theme.fonts["body"])
        self.sql_listbox.grid(row=1, column=0, sticky='nsew', columnspan=2, padx=15, pady=(0,10))
        self.sql_listbox.bind('<<ListboxSelect>>', self.on_sql_file_select)
        
        self.sql_editor_text = TextboxWithContextMenu(edit_frame, wrap="none", font=theme.fonts["code"], fg_color=theme.colors["background"], border_color=theme.colors["comment"], border_width=1)
        self.sql_editor_text.grid(row=2, column=0, sticky='nsew', padx=(15,5), pady=(0,10))
        self.yml_editor_text = TextboxWithContextMenu(edit_frame, wrap="none", font=theme.fonts["code"], fg_color=theme.colors["background"], border_color=theme.colors["comment"], border_width=1)
        self.yml_editor_text.grid(row=2, column=1, sticky='nsew', padx=(5,15), pady=(0,10))
        
        self.btn_generate_doc = ctk.CTkButton(edit_frame, text="Gerar Documentação com IA", font=theme.fonts["button"], command=self.start_documentation_generation, state='disabled', fg_color=theme.colors["accent"], text_color="#000000", hover_color=theme.colors["pink"])
        self.btn_generate_doc.grid(row=3, column=0, columnspan=2, sticky='ew', padx=15, pady=10)
        
        commit_frame = ctk.CTkFrame(main_panel_frame, corner_radius=theme.CORNER_RADIUS, fg_color=theme.colors["sidebar"])
        commit_frame.grid(row=2, column=0, sticky='ew')
        ctk.CTkLabel(commit_frame, text="Etapa 4: Versionar e Preparar Commit", font=theme.fonts["h1"]).pack(anchor='w', padx=15, pady=(15,10))
        self.btn_version_files = ctk.CTkButton(commit_frame, text="Versionar Ficheiros", command=self.version_files, font=theme.fonts["button"], state='disabled', fg_color=theme.colors["green"], text_color="#000000", hover_color="#81F9A1")
        self.btn_version_files.pack(fill='x', padx=15, pady=(0,10))
        self.final_git_commands_text = TextboxWithContextMenu(commit_frame, height=60, font=theme.fonts["code"], wrap='word', fg_color=theme.colors["background"], border_color=theme.colors["comment"], border_width=1)
        self.final_git_commands_text.pack(fill='x', expand=True, padx=15, pady=(0,15))

        self.update_git_commands()

    # ... O resto dos métodos do ficheiro permanecem iguais ...


    def populate_initial_paths(self):
        dbt_path = self.app.config_manager.get("dbt_project_path")
        if dbt_path and os.path.isdir(dbt_path):
            self.repo_path_var.set(dbt_path)
            self.scan_for_models_dirs()

    def select_repo_path(self):
        initial_dir = self.app.config_manager.get("dbt_project_path") or os.path.expanduser("~")
        repo_path = filedialog.askdirectory(title="Selecione a pasta raiz do projeto dbt", initialdir=initial_dir)
        if repo_path and os.path.basename(repo_path):
            self.repo_path_var.set(repo_path)
            self.app.log(f"Repositório selecionado: {repo_path}")
            self.scan_for_models_dirs()
            self.app.config_manager.set("dbt_project_path", repo_path)
            self.app.config_manager.save_config()

    def scan_for_models_dirs(self):
        repo_path = self.repo_path_var.get()
        if not repo_path: return
        models_dirs = [os.path.join(r, d) for r, ds, _ in os.walk(repo_path) for d in ds if d == 'models']
        relative_paths = [os.path.relpath(d, repo_path) for d in models_dirs]
        self.models_combo.configure(values=relative_paths, state='readonly')
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
        self.git_commands_text.delete('1.0', ctk.END)
        self.git_commands_text.insert('1.0', commands)

        final_commands = f"git add .\ngit commit -m \"feat(painel): adiciona modelo para {feature_name}\""
        self.final_git_commands_text.delete('1.0', ctk.END)
        self.final_git_commands_text.insert('1.0', final_commands)

    def select_sql_files(self):
        initial_dir = self.app.config_manager.get("default_import_path") or os.path.expanduser("~")
        files = filedialog.askopenfilenames(title="Selecione as suas consultas SQL", filetypes=[("SQL files", "*.sql")], initialdir=initial_dir)
        if files:
            self.sql_listbox.delete(0, ctk.END)
            self.sql_files_map = {os.path.basename(f): f for f in files}
            for basename in self.sql_files_map.keys():
                self.sql_listbox.insert(ctk.END, basename)
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
                self.sql_editor_text.delete('1.0', ctk.END)
                self.sql_editor_text.insert('1.0', content)
                self.btn_generate_doc.configure(state='normal')
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível ler o ficheiro:\n{e}")

    def start_documentation_generation(self):
        self.btn_generate_doc.configure(state='disabled')
        threading.Thread(target=self.generate_documentation).start()

    def generate_documentation(self):
        self.app.log("Invocando IA para gerar documentação...")
        sql_query = self.sql_editor_text.get('1.0', ctk.END)
        if not sql_query.strip():
            messagebox.showwarning("Aviso", "O editor de SQL está vazio.")
            self.btn_generate_doc.configure(state='normal')
            return

        try:
            api_key = self.app.config_manager.get("gemini_api_key")
            if not api_key:
                load_dotenv()
                api_key = os.getenv("GEMINI_API_KEY")

            if not api_key:
                messagebox.showerror("Erro", "Chave de API do Gemini não encontrada. Por favor, configure-a na aba 'Configurações'.")
                return

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            prompt = self.build_prompt(sql_query)
            response = model.generate_content(prompt)
            
            response_text = response.text.strip().replace("```json", "").replace("```", "")
            doc_data = json.loads(response_text)
            
            yml_snippet = self.format_as_yml(doc_data)
            self.yml_editor_text.delete('1.0', ctk.END)
            self.yml_editor_text.insert('1.0', yml_snippet)
            self.app.log("Documentação gerada com sucesso.")
            self.btn_version_files.configure(state='normal')
        except Exception as e:
            messagebox.showerror("Erro na Geração", f"Ocorreu um erro ao comunicar com a IA:\n{e}")
            self.app.log(f"ERRO na geração de documentação: {e}")
        finally:
            self.btn_generate_doc.configure(state='normal')

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
        yml_content_to_append = self.yml_editor_text.get('1.0', ctk.END)

        if not all([self.repo_path_var.get(), self.models_path_var.get(), schema_path, self.sql_files_map, yml_content_to_append.strip()]):
            messagebox.showerror("Erro", "Verifique se todas as configurações, ficheiros SQL e documentação estão preenchidos.")
            return

        try:
            for basename, original_path in self.sql_files_map.items():
                new_name = f"painel_{basename}"
                dest_path = os.path.join(models_path, new_name)
                
                content = self.sql_editor_text.get('1.0', ctk.END)

                with open(dest_path, 'w', encoding='utf-8') as f_write:
                    f_write.write(content)
                self.app.log(f"Ficheiro salvo em {dest_path}")
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_data = yaml.safe_load(f) or {}
            
            if 'version' not in schema_data: schema_data['version'] = 2
            if 'models' not in schema_data: schema_data['models'] = []

            new_model_data_list = yaml.safe_load(yml_content_to_append)
            
            if new_model_data_list:
                schema_data['models'].extend(new_model_data_list)

            with open(schema_path, 'w', encoding='utf-8') as f:
                yaml.dump(schema_data, f, allow_unicode=True, sort_keys=False, indent=2)

            self.app.log(f"Schema.yml ({schema_path}) atualizado com sucesso.")
            messagebox.showinfo("Sucesso", "Ficheiros versionados e schema atualizado!\nPode agora fazer o commit.")

        except Exception as e:
            messagebox.showerror("Erro no Versionamento", f"Ocorreu um erro: {e}")
            self.app.log(f"ERRO no versionamento: {e}")
