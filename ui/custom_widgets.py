import customtkinter as ctk
import tkinter as tk
from . import theme

class EntryWithContextMenu(ctk.CTkEntry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.context_menu = tk.Menu(self, tearoff=0, background=theme.colors["sidebar"], foreground=theme.colors["foreground"], relief="flat")
        self.context_menu.add_command(label="Cortar", command=self.cut)
        self.context_menu.add_command(label="Copiar", command=self.copy)
        self.context_menu.add_command(label="Colar", command=self.paste)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Selecionar Tudo", command=self.select_all)
        self.bind("<Button-3>", self.show_context_menu)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Control-A>", self.select_all) 

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def cut(self): self.event_generate("<<Cut>>")
    def copy(self): self.event_generate("<<Copy>>")
    def paste(self): self.event_generate("<<Paste>>")
    def select_all(self, event=None):
        self.select_range(0, 'end')
        return "break"

class TextboxWithContextMenu(ctk.CTkTextbox):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.context_menu = tk.Menu(self, tearoff=0, background=theme.colors["sidebar"], foreground=theme.colors["foreground"], relief="flat")
        self.context_menu.add_command(label="Copiar", command=self.copy)
        self.context_menu.add_command(label="Colar", command=self.paste)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Selecionar Tudo", command=self.select_all)
        self.bind("<Button-3>", self.show_context_menu)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Control-A>", self.select_all)

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def copy(self): self.event_generate("<<Copy>>")
    def paste(self): self.event_generate("<<Paste>>")
    def select_all(self, event=None):
        self.tag_add('sel', '1.0', 'end')
        return "break"
