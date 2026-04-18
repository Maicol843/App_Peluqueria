import customtkinter as ctk

class IngresosFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = ctk.CTkLabel(self, text="Control de Ingresos", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=20)
        
        self.entry_monto = ctk.CTkEntry(self, placeholder_text="Monto $")
        self.entry_monto.pack(pady=10)