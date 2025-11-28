import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
import google.generativeai as genai
import threading
from src.ui.base_tab import BaseTab
from src.ui import theme
from src.ui.widgets import TextboxWithContextMenu

class AuxiliadorTab(BaseTab):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance)
        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        
        info_frame = ctk.CTkFrame(self, fg_color=theme.colors["sidebar"])
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        info_frame.columnconfigure(1, weight=1)

        ctk.CTkButton(info_frame, text="Selecionar Arquivo de Contexto", 
                      command=self.handle_file_selection, 
                      font=theme.fonts["button"], 
                      fg_color=theme.colors["comment"]).grid(row=0, column=0, padx=10, pady=10)
        
        self.lbl_file = ctk.CTkLabel(info_frame, text="Nenhum arquivo selecionado", font=theme.fonts["body"])
        self.lbl_file.grid(row=0, column=1, sticky="w", padx=10)

        
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(input_frame, text="Descreva seu problema ou solicitação:", font=theme.fonts["h1"]).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.txt_prompt = TextboxWithContextMenu(input_frame, height=100, font=theme.fonts["body"])
        self.txt_prompt.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.btn_ask = ctk.CTkButton(input_frame, text="Perguntar à IA", 
                                   command=self.run_ai_thread,
                                   font=theme.fonts["button"], 
                                   height=40,
                                   fg_color=theme.colors["accent"], 
                                   text_color=theme.colors["background"])
        self.btn_ask.grid(row=2, column=0, sticky="e")

        
        output_frame = ctk.CTkFrame(self, fg_color="transparent")
        output_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)

        ctk.CTkLabel(output_frame, text="Resposta da IA:", font=theme.fonts["h1"]).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.txt_response = TextboxWithContextMenu(output_frame, font=theme.fonts["code"], wrap="word")
        self.txt_response.grid(row=1, column=0, sticky="nsew")

    def handle_file_selection(self):
        if self.selecionar_arquivo(self.lbl_file):
            self.df = self.carregar_dataframe(self.filepath)
            if self.df is not None:
                self.app.log(f"Contexto carregado: {self.df.shape[0]} linhas, {self.df.shape[1]} colunas")

    def run_ai_thread(self):
        prompt = self.txt_prompt.get("1.0", "end").strip()
        if not prompt:
            messagebox.showwarning("Aviso", "Por favor, digite uma solicitação.")
            return

        api_key = self.app.config_manager.get("gemini_api_key")
        if not api_key:
            messagebox.showerror("Erro", "Chave de API do Gemini não configurada.\nVá em Configurações e adicione sua chave.")
            return

        self.btn_ask.configure(state="disabled", text="Processando...")
        self.txt_response.delete("1.0", "end")
        self.txt_response.insert("1.0", "Gerando resposta...\n")
        
        thread = threading.Thread(target=self.ask_gemini, args=(api_key, prompt))
        thread.start()

    def ask_gemini(self, api_key, user_prompt):
        try:
            genai.configure(api_key=api_key)
            model_name = self.app.config_manager.get("gemini_model") or "gemini-2.5-flash"
            model = genai.GenerativeModel(model_name)

            context = ""
            if self.df is not None:
                
                buffer = []
                buffer.append(f"Contexto do Arquivo: {pd.io.common.stringify_path(self.filepath)}")
                buffer.append(f"Dimensões: {self.df.shape}")
                buffer.append("Colunas e Tipos:")
                for col, dtype in self.df.dtypes.items():
                    buffer.append(f"- {col} ({dtype})")
                
                buffer.append("\nAmostra dos dados (primeiras 5 linhas):")
                buffer.append(self.df.head().to_markdown(index=False))
                
                context = "\n".join(buffer) + "\n\n"

            full_prompt = (
                "Você é um assistente especialista em análise de dados e Python.\n"
                "Use o contexto abaixo (se houver) para responder à solicitação do usuário.\n"
                "Se for solicitado código, forneça código Python limpo e comentado.\n"
                "Se for solicitado uma fórmula de Excel, forneça a fórmula.\n\n"
                f"{context}"
                "Solicitação do Usuário:\n"
                f"{user_prompt}"
            )

            response = model.generate_content(full_prompt)
            
            self.after(0, lambda: self.txt_response.delete("1.0", "end"))
            self.after(0, lambda: self.txt_response.insert("1.0", response.text))
            self.app.log("Resposta da IA gerada com sucesso.")

        except Exception as e:
            self.after(0, lambda: self.txt_response.delete("1.0", "end"))
            self.after(0, lambda: self.txt_response.insert("1.0", f"Erro ao consultar a IA: {str(e)}"))
            self.app.log(f"Erro Gemini: {e}")
        finally:
            self.after(0, lambda: self.btn_ask.configure(state="normal", text="Perguntar à IA"))
