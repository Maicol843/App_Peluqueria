import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import database
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

class VerFichaFrame(ctk.CTkFrame):
    def __init__(self, master, cliente_datos, **kwargs):
        super().__init__(master, **kwargs)
        # cliente_datos contiene: [id, nombre, apellido, fecha, email, tel]
        self.cliente = cliente_datos 
        self.pagina_actual = 1
        self.reg_por_pag = 10

        # --- TÍTULO ---
        ctk.CTkLabel(self, text="Ficha del Cliente", font=("Arial", 24, "bold")).pack(pady=15)

        # --- INFORMACIÓN DEL CLIENTE (Sin recuadro y con separadores '|') ---
        self.info_text = (
            f"{self.cliente[1]} {self.cliente[2]}\n"
            "F. de Nacimiento: " f"{self.cliente[3]} "  " | "  "Correo: " f"{self.cliente[4]}" " | "  "Teléfono: " f"{self.cliente[5]}"
        )
        ctk.CTkLabel(self, text=self.info_text, font=("Arial", 15), justify="center").pack(pady=10)

        # --- SECCIÓN: SERVICIOS REALIZADOS ---
        ctk.CTkLabel(self, text="Servicios Realizados", font=("Arial", 18, "bold")).pack(pady=(20, 5))

        # Toolbar: Botones + Buscador
        self.toolbar = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar.pack(pady=10)
        
        ctk.CTkButton(self.toolbar, text="Insertar", width=90, command=self.abrir_modal_servicio).pack(side="left", padx=5)
        ctk.CTkButton(self.toolbar, text="Editar", width=90, command=self.editar_servicio).pack(side="left", padx=5)
        ctk.CTkButton(self.toolbar, text="Eliminar", width=90, command=self.eliminar_servicio).pack(side="left", padx=5)
        ctk.CTkButton(self.toolbar, text="Restablecer", width=90, command=self.restablecer_servicios).pack(side="left", padx=5)
        ctk.CTkButton(self.toolbar, text="Descargar", width=90, command=self.generar_pdf).pack(side="left", padx=5)
        
        self.search_ser = ctk.CTkEntry(self.toolbar, placeholder_text="Buscar servicio...", width=200)
        self.search_ser.pack(side="left", padx=(20, 5))
        self.search_ser.bind("<KeyRelease>", lambda e: self.reset_paginar_y_cargar())

        # --- TABLA DE SERVICIOS ---
        style = ttk.Style()
        style.configure("Ficha.Treeview", background="#2b2b2b", foreground="white", rowheight=35, font=("Arial", 12))
        style.configure("Ficha.Treeview.Heading", font=("Arial", 13, "bold"))
        
        self.tabla = ttk.Treeview(self, columns=("num", "fec", "ser", "pre"), show='headings', style="Ficha.Treeview")
        self.tabla.heading("num", text="Nro.")
        self.tabla.heading("fec", text="Fecha")
        self.tabla.heading("ser", text="Servicio")
        self.tabla.heading("pre", text="Precio ($)")
        
        self.tabla.column("num", width=50, anchor="center")
        self.tabla.column("fec", width=150, anchor="center")
        self.tabla.column("ser", width=300, anchor="center")
        self.tabla.column("pre", width=100, anchor="center")
        self.tabla.pack(expand=True, fill="both", padx=40, pady=10)

        # --- PAGINACIÓN VISUAL (Debajo de la tabla) ---
        self.pag_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pag_frame.pack(pady=15)
        
        self.btn_prev = ctk.CTkButton(self.pag_frame, text="<", width=40, command=self.ant_pag)
        self.btn_prev.pack(side="left", padx=10)
        
        self.lbl_pag = ctk.CTkLabel(self.pag_frame, text="Página 1 de 1", font=("Arial", 12, "bold"))
        self.lbl_pag.pack(side="left")
        
        self.btn_next = ctk.CTkButton(self.pag_frame, text=">", width=40, command=self.sig_pag)
        self.btn_next.pack(side="left", padx=10)

        self.cargar_servicios()

    def cargar_servicios(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        datos = database.obtener_servicios(self.cliente[0], self.search_ser.get())
        
        total_pag = max(1, (len(datos) + self.reg_por_pag - 1) // self.reg_por_pag)
        if self.pagina_actual > total_pag: self.pagina_actual = total_pag
        
        inicio = (self.pagina_actual - 1) * self.reg_por_pag
        for i, s in enumerate(datos[inicio:inicio+self.reg_por_pag], start=inicio+1):
            self.tabla.insert("", "end", iid=s[0], values=(i, s[2], s[3], f"{s[4]:.2f}"))
        
        self.lbl_pag.configure(text=f"Página {self.pagina_actual} de {total_pag}")

    def reset_paginar_y_cargar(self):
        self.pagina_actual = 1
        self.cargar_servicios()

    def sig_pag(self): 
        datos = database.obtener_servicios(self.cliente[0], self.search_ser.get())
        total_pag = (len(datos) + self.reg_por_pag - 1) // self.reg_por_pag
        if self.pagina_actual < total_pag:
            self.pagina_actual += 1
            self.cargar_servicios()

    def ant_pag(self): 
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.cargar_servicios()

    def abrir_modal_servicio(self, edit_data=None):
        modal = ctk.CTkToplevel(self)
        modal.title("Servicio")
        modal.geometry("350x400")
        modal.attributes("-topmost", True)
        modal.grab_set()

        ctk.CTkLabel(modal, text="Datos del Servicio", font=("Arial", 16, "bold")).pack(pady=10)
        ent_fec = ctk.CTkEntry(modal, placeholder_text="Fecha (dd/mm/aaaa)", width=250)
        ent_fec.pack(pady=10)
        ent_ser = ctk.CTkEntry(modal, placeholder_text="Servicio", width=250)
        ent_ser.pack(pady=10)
        ent_pre = ctk.CTkEntry(modal, placeholder_text="Precio", width=250)
        ent_pre.pack(pady=10)

        if edit_data:
            ent_fec.insert(0, edit_data[1])
            ent_ser.insert(0, edit_data[2])
            ent_pre.insert(0, str(edit_data[3]).replace('$', ''))

        def guardar():
            try:
                precio = float(ent_pre.get())
                if edit_data:
                    database.actualizar_servicio(edit_data[0], ent_fec.get(), ent_ser.get(), precio)
                else:
                    database.registrar_servicio(self.cliente[0], ent_fec.get(), ent_ser.get(), precio)
                modal.destroy()
                self.cargar_servicios()
            except ValueError: 
                messagebox.showerror("Error", "Ingrese un precio numérico válido.")

        ctk.CTkButton(modal, text="Guardar", command=guardar).pack(pady=20)

    def editar_servicio(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un servicio.")
            return
        v = self.tabla.item(sel)['values']
        self.abrir_modal_servicio(edit_data=(sel[0], v[1], v[2], v[3]))

    def eliminar_servicio(self):
        sel = self.tabla.selection()
        if sel and messagebox.askyesno("Confirmar", "¿Desea eliminar este servicio?"):
            database.eliminar_servicio(sel[0])
            self.cargar_servicios()

    def restablecer_servicios(self):
        if messagebox.askyesno("Advertencia", "¿Eliminar TODOS los servicios de este cliente?"):
            database.eliminar_servicios_cliente(self.cliente[0])
            self.cargar_servicios()

    def generar_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not path: return
        try:
            doc = SimpleDocTemplate(path, pagesize=A4)
            elementos = []
            estilos = getSampleStyleSheet()
            
            # Estilos personalizados para centrar y espaciar
            estilo_titulo = ParagraphStyle('TituloPDF', parent=estilos['Title'], alignment=TA_CENTER, spaceAfter=10)
            estilo_subtitulo = ParagraphStyle('SubPDF', parent=estilos['Normal'], alignment=TA_CENTER, fontSize=14, spaceAfter=5, fontName='Helvetica-Bold')
            estilo_datos = ParagraphStyle('DatosPDF', parent=estilos['Normal'], alignment=TA_CENTER, fontSize=11, spaceAfter=20)

            # 1. TÍTULOS Y CABECERA (Según lo solicitado)
            elementos.append(Paragraph("Historial de Servicios", estilo_titulo))
            elementos.append(Paragraph(f"{self.cliente[1]} {self.cliente[2]}", estilo_subtitulo))
            
            # Línea de contacto: Fecha | Email | Teléfono
            linea_contacto = f"{self.cliente[3]}  |  {self.cliente[4]}  |  {self.cliente[5]}"
            elementos.append(Paragraph(linea_contacto, estilo_datos))
            elementos.append(Spacer(1, 10))
            
            # 2. TABLA DE SERVICIOS
            datos_tabla = [["Nro.", "Fecha", "Servicio", "Precio"]]
            servicios = database.obtener_servicios(self.cliente[0])
            for i, s in enumerate(servicios, 1):
                datos_tabla.append([i, s[2], s[3], f"${s[4]:.2f}"])
            
            t = Table(datos_tabla, colWidths=[30, 90, 260, 90])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#333333")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ]))
            elementos.append(t)
            
            doc.build(elementos)
            messagebox.showinfo("Éxito", "PDF generado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el PDF: {e}")