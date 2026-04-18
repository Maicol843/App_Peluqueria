import customtkinter as ctk

class RegistroFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = ctk.CTkLabel(self, text="Registro de Turnos", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=20)
        
        # Ejemplo de un campo de entrada
        self.entry_cliente = ctk.CTkEntry(self, placeholder_text="Nombre del cliente")
        self.entry_cliente.pack(pady=10)
        
        self.btn_guardar = ctk.CTkButton(self, text="Guardar Turno", fg_color="green")
        self.btn_guardar.pack(pady=10)