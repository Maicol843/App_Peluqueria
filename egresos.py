import customtkinter as ctk

class EgresosFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = ctk.CTkLabel(self, text="Control de Egresos (Gastos)", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=20)