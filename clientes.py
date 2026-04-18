import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import database
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

class ClientesFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Variables de control para paginación
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        
        # Título centrado
        self.label_titulo = ctk.CTkLabel(self, text="Lista de Clientes", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_titulo.pack(pady=20)

        # --- CONTENEDOR PRINCIPAL DE HERRAMIENTAS (Botones + Buscador) ---
        self.toolbar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar_frame.pack(pady=20, fill="x")

        # Sub-contenedor para centrar todo el contenido
        self.center_toolbar = ctk.CTkFrame(self.toolbar_frame, fg_color="transparent")
        self.center_toolbar.pack(expand=True)

        # 1. BOTONES DE ACCIÓN
        botones = [
            ("Ver Ficha", self.ver_ficha),
            ("Editar", self.abrir_modal_editar),
            ("Eliminar", self.eliminar_seleccionado),
            ("Restablecer", self.restablecer_todo),
            ("Descargar", self.generar_pdf)
        ]

        for texto, comando in botones:
            btn = ctk.CTkButton(self.center_toolbar, text=texto, command=comando, width=110)
            btn.pack(side="left", padx=5)

        # 2. BUSCADOR (Al lado de los botones)
        self.search_entry = ctk.CTkEntry(
            self.center_toolbar, 
            placeholder_text="Buscar cliente...", 
            width=250
        )
        self.search_entry.pack(side="left", padx=(20, 5))
        self.search_entry.bind("<KeyRelease>", lambda e: self.reset_paginacion_y_cargar())

        # --- TABLA (Treeview) ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        rowheight=35,
                        font=("Arial", 12),
                        borderwidth=0)
        style.map("Treeview", background=[('selected', '#1f538d')])
        # Configuración de los encabezados
        style.configure("Treeview.Heading", 
                        background="#333333", 
                        foreground="white", 
                        relief="flat",
                        font=("Arial", 13, "bold"))

        self.tabla = ttk.Treeview(self, columns=("num", "nom", "ape", "fec", "ema", "tel"), show='headings')
        self.tabla.heading("num", text="Nro.")
        self.tabla.heading("nom", text="Nombre")
        self.tabla.heading("ape", text="Apellido")
        self.tabla.heading("fec", text="F. Nacimiento")
        self.tabla.heading("ema", text="Email")
        self.tabla.heading("tel", text="Teléfono")
        
        columnas = {"num": 40, "nom": 120, "ape": 120, "fec": 120, "ema": 180, "tel": 120}
        for col, ancho in columnas.items():
            self.tabla.column(col, anchor="center", width=ancho)

        # Empacamos la tabla PRIMERO
        self.tabla.pack(expand=True, fill="both", padx=20, pady=(10, 5))

        # --- PANEL DE PAGINACIÓN (Ahora debajo de la tabla) ---
        self.paginacion_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.paginacion_frame.pack(pady=15) # Un poco más de margen inferior

        self.btn_prev = ctk.CTkButton(self.paginacion_frame, text="<", width=40, command=self.pagina_anterior)
        self.btn_prev.pack(side="left", padx=10)

        self.label_paginas = ctk.CTkLabel(self.paginacion_frame, text="Página 1 de 1", font=("Arial", 12, "bold"))
        self.label_paginas.pack(side="left")

        self.btn_next = ctk.CTkButton(self.paginacion_frame, text=">", width=40, command=self.pagina_siguiente)
        self.btn_next.pack(side="left", padx=10)
        
        self.cargar_datos()

    def cargar_datos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        busqueda = self.search_entry.get()
        todos_los_clientes = database.obtener_clientes(busqueda)
        
        total_clientes = len(todos_los_clientes)
        total_paginas = max(1, (total_clientes + self.registros_por_pagina - 1) // self.registros_por_pagina)
        
        if self.pagina_actual > total_paginas:
            self.pagina_actual = total_paginas

        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        clientes_pagina = todos_los_clientes[inicio:fin]

        for i, cliente in enumerate(clientes_pagina, start=inicio + 1):
            self.tabla.insert("", "end", iid=cliente[0], values=(i, cliente[1], cliente[2], cliente[3], cliente[4], cliente[5]))
        
        self.label_paginas.configure(text=f"Página {self.pagina_actual} de {total_paginas}")

    def reset_paginacion_y_cargar(self):
        self.pagina_actual = 1
        self.cargar_datos()

    def pagina_siguiente(self):
        busqueda = self.search_entry.get()
        total_clientes = len(database.obtener_clientes(busqueda))
        total_paginas = (total_clientes + self.registros_por_pagina - 1) // self.registros_por_pagina
        
        if self.pagina_actual < total_paginas:
            self.pagina_actual += 1
            self.cargar_datos()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.cargar_datos()

    def eliminar_seleccionado(self):
        item = self.tabla.selection()
        if not item:
            messagebox.showwarning("Atención", "Seleccione un cliente de la tabla.")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro en eliminar este cliente?"):
            database.eliminar_cliente(item[0])
            self.cargar_datos()

    def restablecer_todo(self):
        if messagebox.askyesno("Advertencia", "¿Está seguro de eliminar TODOS los datos?"):
            database.eliminar_todos_los_clientes()
            self.pagina_actual = 1
            self.cargar_datos()

    def abrir_modal_editar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un cliente.")
            return
        
        datos = self.tabla.item(seleccion)['values']
        id_cliente = seleccion[0]

        modal = ctk.CTkToplevel(self)
        modal.title("Editar Cliente")
        modal.geometry("400x550")
        modal.attributes("-topmost", True)
        modal.grab_set()

        ctk.CTkLabel(modal, text="Editar Datos", font=("Arial", 16, "bold")).pack(pady=20)
        
        ent_nom = self.crear_campo_modal(modal, "Nombre:", datos[1])
        ent_ape = self.crear_campo_modal(modal, "Apellido:", datos[2])
        ent_fec = self.crear_campo_modal(modal, "F. Nacimiento (dd/mm/aaaa):", datos[3])
        ent_ema = self.crear_campo_modal(modal, "Email:", datos[4])
        ent_tel = self.crear_campo_modal(modal, "Teléfono:", datos[5])

        def guardar_cambios():
            database.actualizar_cliente(id_cliente, ent_nom.get(), ent_ape.get(), ent_fec.get(), ent_ema.get(), ent_tel.get())
            modal.destroy()
            self.cargar_datos()

        ctk.CTkButton(modal, text="Guardar", command=guardar_cambios, fg_color="green").pack(pady=30)

    def crear_campo_modal(self, master, label_text, valor_actual):
        ctk.CTkLabel(master, text=label_text).pack(pady=(5, 0))
        entry = ctk.CTkEntry(master, width=300)
        entry.insert(0, valor_actual)
        entry.pack(pady=(0, 5))
        return entry

    def generar_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not path: return
        
        try:
            doc = SimpleDocTemplate(path, pagesize=A4)
            elementos = []
            estilos = getSampleStyleSheet()
            titulo = Paragraph("LISTADO DE CLIENTES - PELUQUERÍA", estilos['Title'])
            elementos.append(titulo)
            
            encabezados = ["Nro.", "Nombre", "Apellido", "F. Nacimiento", "Email", "Teléfono"]
            datos_pdf = [encabezados]
            
            clientes = database.obtener_clientes()
            for i, cl in enumerate(clientes, 1):
                datos_pdf.append([i, cl[1], cl[2], cl[3], cl[4], cl[5]])
            
            tabla_pdf = Table(datos_pdf, colWidths=[30, 90, 90, 80, 150, 80])
            estilo_tabla = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#333333")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F3F3F3")),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])
            tabla_pdf.setStyle(estilo_tabla)
            elementos.append(tabla_pdf)
            doc.build(elementos)
            messagebox.showinfo("PDF", "Reporte generado correctamente.")
        except Exception as e:
            messagebox.showerror("Error PDF", f"No se pudo generar: {e}")

    def ver_ficha(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un cliente.")
            return
        print(f"Ficha del cliente ID: {seleccion[0]}")