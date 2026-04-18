import customtkinter as ctk
# Importamos los otros archivos (los crearemos a continuación)
import registro
import clientes
import ingresos
import egresos
import ver_ficha

class AppPeluqueria(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestión - Peluquería")
        self.geometry("900x600")

        # Configuración de cuadrícula (Grid)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Panel de Navegación ---
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        
        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="MENÚ", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Botones del menú
        self.btn_inicio = ctk.CTkButton(self.navigation_frame, text="Inicio", command=self.show_inicio)
        self.btn_inicio.grid(row=1, column=0, padx=20, pady=10)

        self.btn_registro = ctk.CTkButton(self.navigation_frame, text="Registro", command=self.show_registro)
        self.btn_registro.grid(row=2, column=0, padx=20, pady=10)

        self.btn_clientes = ctk.CTkButton(self.navigation_frame, text="Clientes", command=self.show_clientes)
        self.btn_clientes.grid(row=3, column=0, padx=20, pady=10)

        self.btn_ingresos = ctk.CTkButton(self.navigation_frame, text="Ingresos", command=self.show_ingresos)
        self.btn_ingresos.grid(row=4, column=0, padx=20, pady=10)

        self.btn_egresos = ctk.CTkButton(self.navigation_frame, text="Egresos", command=self.show_egresos)
        self.btn_egresos.grid(row=5, column=0, padx=20, pady=10)

        # --- Contenedor de Vistas ---
        self.main_view = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew")
        
        self.current_frame = None
        self.show_inicio() # Mostrar inicio por defecto

    def clear_view(self):
        if self.current_frame is not None:
            self.current_frame.destroy()

    def show_inicio(self):
        self.clear_view()
        self.current_frame = ctk.CTkLabel(self.main_view, text="Bienvenido a la Peluquería", font=("Arial", 24))
        self.current_frame.pack(pady=50)

    def show_registro(self):
        self.clear_view()
        self.current_frame = registro.RegistroFrame(self.main_view)
        self.current_frame.pack(expand=True, fill="both")

    def show_clientes(self):
        self.clear_view()
        self.current_frame = clientes.ClientesFrame(self.main_view)
        self.current_frame.pack(expand=True, fill="both")

    def show_ingresos(self):
        self.clear_view()
        self.current_frame = ingresos.IngresosFrame(self.main_view)
        self.current_frame.pack(expand=True, fill="both")

    def show_egresos(self):
        self.clear_view()
        self.current_frame = egresos.EgresosFrame(self.main_view)
        self.current_frame.pack(expand=True, fill="both")
    
    def cambiar_a_ficha(self, datos_cliente):
        self.clear_view()
        # Creamos el frame de la ficha pasando los datos
        self.current_frame = ver_ficha.VerFichaFrame(self.main_view, cliente_datos=datos_cliente)
        self.current_frame.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = AppPeluqueria()
    app.mainloop()