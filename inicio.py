import customtkinter as ctk
from tkinter import ttk
import database
from datetime import datetime

# Importamos los otros módulos para la navegación
import registro
import clientes
import buscar
import ingresos
import egresos
import ver_ficha

class InicioFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # 1. Título principal
        ctk.CTkLabel(
            self, 
            text="Resumen del día", 
            font=("Arial", 32, "bold")
        ).pack(pady=(40, 20))

        # --- SECCIÓN DE BOTONES (Superiores) ---
        self.container_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.container_botones.pack(anchor="center", padx=20, pady=(0, 30))
        
        # Obtener datos de la base de datos
        t_cli, t_ing, t_egr, s_mes = database.obtener_resumen_inicio()

        # Botones con colores sólidos y texto en blanco
        self.crear_boton_dato(0, "Clientes registrados", str(t_cli), "#6610f2")
        self.crear_boton_dato(1, "Ingresos", f"${t_ing:,.2f}", "#198754")
        self.crear_boton_dato(2, "Egresos", f"${t_egr:,.2f}", "#dc3545")
        self.crear_boton_dato(3, "Clientes asistidos en el mes", str(s_mes), "#ffc107")

        # --- SECCIÓN INFERIOR (Tablas y Avisos) ---
        self.lower_container = ctk.CTkFrame(self, fg_color="transparent")
        self.lower_container.pack(expand=True, fill="both", padx=40, pady=10)
        self.lower_container.grid_columnconfigure((0, 1), weight=1)

        # --- COLUMNA IZQUIERDA: Tabla de Servicios ---
        self.frame_tabla = ctk.CTkFrame(self.lower_container, fg_color="transparent")
        self.frame_tabla.grid(row=0, column=0, padx=20, sticky="nsew")

        ctk.CTkLabel(self.frame_tabla, text="Servicios realizados este mes", font=("Arial", 18, "bold")).pack(pady=10)
        
        # Configuración de estilo para la tabla
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Arial", 11))
        
        self.tabla_servicios = ttk.Treeview(
            self.frame_tabla, 
            columns=("Servicio", "Cantidad"), 
            show="headings", 
            height=8
        )
        self.tabla_servicios.heading("Servicio", text="Servicio")
        self.tabla_servicios.heading("Cantidad", text="Veces realizado")
        self.tabla_servicios.column("Servicio", width=200, anchor="w")
        self.tabla_servicios.column("Cantidad", width=100, anchor="center")
        self.tabla_servicios.pack(expand=True, fill="both")

        self.cargar_servicios_mes()

        # --- COLUMNA DERECHA: Avisos de Cumpleaños ---
        self.frame_cumple = ctk.CTkFrame(self.lower_container, fg_color="transparent")
        self.frame_cumple.grid(row=0, column=1, padx=20, sticky="nsew")

        ctk.CTkLabel(self.frame_cumple, text="Cumpleaños de hoy", font=("Arial", 18, "bold")).pack(pady=10)
        
        self.txt_cumple = ctk.CTkTextbox(
            self.frame_cumple, 
            width=300, 
            height=200, 
            font=("Arial", 14),
            border_width=2,
            border_color="#d3d3d3"
        )
        self.txt_cumple.pack(expand=True, fill="both")
        
        self.mostrar_cumpleanios()

    def crear_boton_dato(self, columna, texto, valor, color):
        """Crea un botón estilizado con color de fondo sólido"""
        btn = ctk.CTkButton(
            self.container_botones,
            text=f"{texto}\n\n{valor}",
            font=("Arial", 15, "bold"),
            fg_color=color,
            text_color="white",
            hover=False, # Estático para información
            width=200,
            height=100,
            corner_radius=10
        )
        btn.grid(row=0, column=columna, padx=10, pady=10)

    def cargar_servicios_mes(self):
        # Limpiar tabla antes de cargar
        for i in self.tabla_servicios.get_children():
            self.tabla_servicios.delete(i)
        
        # Obtener datos de database.py
        datos = database.obtener_servicios_populares_mes()
        for srv, cant in datos:
            self.tabla_servicios.insert("", "end", values=(srv, cant))

    def mostrar_cumpleanios(self):
        self.txt_cumple.configure(state="normal")
        self.txt_cumple.delete("1.0", "end")
        
        cumpleaneros = database.obtener_cumpleanios_hoy()
        
        if cumpleaneros:
            for nombre, apellido in cumpleaneros:
                self.txt_cumple.insert("end", f"🎂 Hoy es el cumpleaños de {nombre} {apellido}\n\n")
        else:
            self.txt_cumple.insert("end", "Hoy no hay cumpleaños de ningún cliente.")
        
        self.txt_cumple.configure(state="disabled")

class AppPeluqueria(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestión - Peluquería")
        self.geometry("1200x700")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Panel de Navegación
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.navigation_frame, text="MENÚ", font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=20, pady=20)

        # Botones de navegación
        self.menu_items = [
            ("Inicio", self.show_inicio),
            ("Registro", self.show_registro),
            ("Clientes", self.show_clientes),
            ("Buscar", self.show_buscar),
            ("Ingresos", self.show_ingresos),
            ("Egresos", self.show_egresos)
        ]

        for i, (text, command) in enumerate(self.menu_items, 1):
            btn = ctk.CTkButton(self.navigation_frame, text=text, command=command)
            btn.grid(row=i, column=0, padx=20, pady=10)

        # Vista Principal
        self.main_view = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew")

        self.current_frame = None
        self.show_inicio()

    def clear_view(self):
        if self.current_frame is not None:
            self.current_frame.destroy()

    def show_inicio(self):
        self.clear_view()
        self.current_frame = InicioFrame(self.main_view)
        self.current_frame.pack(expand=True, fill="both")

    def show_registro(self):
        self.clear_view()
        self.current_frame = registro.RegistroFrame(self.main_view)
        self.current_frame.pack(expand=True, fill="both")

    def show_clientes(self):
        self.clear_view()
        self.current_frame = clientes.ClientesFrame(self.main_view)
        self.current_frame.pack(expand=True, fill="both")

    def show_buscar(self):
        self.clear_view()
        self.current_frame = buscar.BuscarFrame(self.main_view)
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
        self.current_frame = ver_ficha.VerFichaFrame(self.main_view, datos_cliente)
        self.current_frame.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = AppPeluqueria()
    app.mainloop()