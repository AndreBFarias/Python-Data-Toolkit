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
}

# 2. Definições das Fontes (parâmetros, não objetos)
font_definitions = {
    "title": ("Roboto", 20, "bold"),
    "h1": ("Roboto", 14, "bold"),
    "body": ("Roboto", 12, "normal"),
    "button": ("Roboto", 12, "bold"),
    "code": ("monospace", 11, "normal"),
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
    "sidebar_width": 200,
    "button_height": 40,
}
padding = {
    "app": 20,
    "frame": 15,
    "widget_y": 5,
    "widget_x": 10,
}
CORNER_RADIUS = 10
