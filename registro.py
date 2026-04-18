import customtkinter as ctk
from tkinter import messagebox
import database

class RegistroFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Título centrado
        self.label_titulo = ctk.CTkLabel(
            self, 
            text="Registro de Clientes", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_titulo.pack(pady=(30, 20))

        # Contenedor del formulario
        self.form_container = ctk.CTkFrame(self, fg_color="transparent")
        self.form_container.pack(pady=10, padx=40)

        # Campos del formulario
        self.entry_nombre = self.crear_campo("Nombre:")
        self.entry_apellido = self.crear_campo("Apellido:")
        self.entry_fecha = self.crear_campo("Fecha de Nacimiento (dd/mm/aaaa):")
        self.entry_email = self.crear_campo("Correo Electrónico:")
        self.entry_telefono = self.crear_campo("Teléfono:")

        # Botón de registrar
        self.btn_registrar = ctk.CTkButton(
            self, 
            text="Registrar", 
            command=self.ejecutar_registro,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_registrar.pack(pady=30)

    def crear_campo(self, texto_label):
        """Función auxiliar para crear etiqueta y campo de entrada"""
        label = ctk.CTkLabel(self.form_container, text=texto_label, font=("Arial", 13))
        label.pack(anchor="w", pady=(10, 0))
        entry = ctk.CTkEntry(self.form_container, width=350)
        entry.pack(pady=(0, 5))
        return entry

    def ejecutar_registro(self):
        # Obtener datos de los campos
        nombre = self.entry_nombre.get()
        apellido = self.entry_apellido.get()
        fecha = self.entry_fecha.get()
        email = self.entry_email.get()
        telefono = self.entry_telefono.get()

        # Intentar guardar en la base de datos
        exito = database.registrar_cliente(nombre, apellido, fecha, email, telefono)

        if exito:
            messagebox.showinfo("Éxito", "Se registró el cliente exitosamente")
            self.limpiar_campos()
        else:
            messagebox.showerror("Error", "Error, vuelva a ingresar los datos del cliente")

    def limpiar_campos(self):
        self.entry_nombre.delete(0, 'end')
        self.entry_apellido.delete(0, 'end')
        self.entry_fecha.delete(0, 'end')
        self.entry_email.delete(0, 'end')
        self.entry_telefono.delete(0, 'end')