# theme.py
import customtkinter as ctk

# 1. Paleta de Cores Centralizada (Dracula)
colors = {
    "background": "#282A36",
    "sidebar": "#44475A",
    "foreground": "#F8F8F2",
    "accent": "#BD93F9",      # Purple
    "comment": "#6272A4",
    "pink": "#FF79C6",
    "green": "#50FA7B",
    "white": "#FFFFFF",       # Adicionado para elementos desabilitados
}

# 2. Definições das Fontes (parâmetros, não objetos) - Aumentadas em 20%
font_definitions = {
    "title": ("Roboto", 28, "bold"),  # De 24 para 28
    "h1": ("Roboto", 19, "bold"),     # De 16 para 19
    "body": ("Roboto", 17, "normal"), # De 14 para 17
    "button": ("Roboto", 17, "bold"), # De 14 para 17
    "code": ("monospace", 14, "normal"), # De 12 para 14
}

# Dicionário que será populado com os objetos CTkFont
fonts = {}

def initialize_fonts():
    """Cria os objetos CTkFont depois da janela principal existir."""
    for name, definition in font_definitions.items():
        family, size, weight = definition
        fonts[name] = ctk.CTkFont(family=family, size=size, weight=weight)

# 3. Constantes de Tamanho e Estilo
sizing = {
    "sidebar_width": 400,  # Aumentado de 300 para 400
    "button_height": 40,
}
padding = {
    "app": 20,
    "frame": 15,
    "widget_y": 5,
    "widget_x": 10,
}
CORNER_RADIUS = 10
