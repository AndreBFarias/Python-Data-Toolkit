import customtkinter as ctk


colors = {
    "background": "#282A36",
    "sidebar": "#44475A",
    "foreground": "#F8F8F2",
    "accent": "#BD93F9",      
    "comment": "#6272A4",
    "pink": "#FF79C6",
    "green": "#50FA7B",
    "white": "#FFFFFF",       
}


font_definitions = {
    "title": ("Roboto", 28, "bold"),  
    "h1": ("Roboto", 19, "bold"),     
    "body": ("Roboto", 17, "normal"), 
    "button": ("Roboto", 17, "bold"), 
    "code": ("monospace", 14, "normal"), 
}


fonts = {}

def initialize_fonts():
    """Cria os objetos CTkFont depois da janela principal existir."""
    for name, definition in font_definitions.items():
        family, size, weight = definition
        fonts[name] = ctk.CTkFont(family=family, size=size, weight=weight)


sizing = {
    "sidebar_width": 400,  
    "button_height": 40,
}
padding = {
    "app": 20,
    "frame": 15,
    "widget_y": 5,
    "widget_x": 10,
}
CORNER_RADIUS = 10
