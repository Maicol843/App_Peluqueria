import customtkinter as ctk

class ClientesFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = ctk.CTkLabel(self, text="Listado de Clientes", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=20)
        
        # Aquí podrías poner una tabla o lista más adelante
        self.info = ctk.CTkLabel(self, text="Aún no hay clientes registrados.")
        self.info.pack(pady=10)