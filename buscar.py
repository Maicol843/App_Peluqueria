import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import database
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

class BuscarFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pagina_actual = 1
        self.reg_por_pag = 10

        # --- TÍTULO ---
        ctk.CTkLabel(self, text="Búsqueda de Clientes", font=("Arial", 24, "bold")).pack(pady=20)

        # --- CONTENEDOR DE FILTROS ---
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(pady=10)

        # Buscador por texto
        self.search_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Nombre, apellido o servicio...", width=300)
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self.reset_y_cargar())

        # Selector de días
        self.combo_dias = ctk.CTkComboBox(
            self.filter_frame, 
            values=["Todos", "Últimos 10 días", "Últimos 20 días", "Últimos 30 días"], 
            command=lambda v: self.reset_y_cargar(),
            state="readonly"
        )
        self.combo_dias.set("Todos")
        self.combo_dias.pack(side="left", padx=10)

        # BOTÓN DESCARGAR PDF
        self.btn_pdf = ctk.CTkButton(self.filter_frame, text="Descargar", command=self.generar_pdf_busqueda, fg_color="#2c3e50")
        self.btn_pdf.pack(side="left", padx=10)

        # --- TABLA EN INTERFAZ ---
        self.tabla = ttk.Treeview(self, columns=("num", "fec", "nom", "ape", "ser", "for", "pre"), show='headings')
        self.tabla.heading("num", text="Nro.")
        self.tabla.heading("fec", text="Fecha")
        self.tabla.heading("nom", text="Nombre")
        self.tabla.heading("ape", text="Apellido")
        self.tabla.heading("ser", text="Servicio")
        self.tabla.heading("for", text="Fórmula")
        self.tabla.heading("pre", text="Precio")
        
        # Ajuste de anchos para acomodar la nueva columna
        anchos = [35, 90, 100, 100, 150, 150, 80]
        for col, width in zip(self.tabla["columns"], anchos):
            self.tabla.column(col, width=width, anchor="center")
        
        self.tabla.pack(expand=True, fill="both", padx=40, pady=10)

        # --- PAGINACIÓN ---
        self.pag_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pag_frame.pack(pady=15)
        
        self.btn_prev = ctk.CTkButton(self.pag_frame, text="<", width=40, command=self.ant_pag).pack(side="left", padx=10)
        self.lbl_pag = ctk.CTkLabel(self.pag_frame, text="Página 1 de 1", font=("Arial", 12, "bold"))
        self.lbl_pag.pack(side="left")
        self.btn_next = ctk.CTkButton(self.pag_frame, text=">", width=40, command=self.sig_pag).pack(side="left", padx=10)

        self.cargar_datos()

    def obtener_dias_filtro(self):
        opcion = self.combo_dias.get()
        if "10" in opcion: return 10
        if "20" in opcion: return 20
        if "30" in opcion: return 30
        return None

    def cargar_datos(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        
        texto = self.search_entry.get()
        dias = self.obtener_dias_filtro()
        # Nota: database.buscar_clientes_servicios debe devolver la fórmula ahora
        datos = database.buscar_clientes_servicios(texto, dias)
        
        total_pag = max(1, (len(datos) + self.reg_por_pag - 1) // self.reg_por_pag)
        if self.pagina_actual > total_pag: self.pagina_actual = total_pag
        self.lbl_pag.configure(text=f"Página {self.pagina_actual} de {total_pag}")
        
        inicio = (self.pagina_actual - 1) * self.reg_por_pag
        for i, r in enumerate(datos[inicio:inicio+self.reg_por_pag], start=inicio+1):
            # r[4] es Servicio, r[5] es Fórmula, r[6] es Precio
            # Manejamos posibles valores None para que no rompan el formato
            formula = r[5] if r[5] else ""
            precio = f"${r[6]:.2f}" if r[6] is not None else "$0.00"
            self.tabla.insert("", "end", values=(i, r[1], r[2], r[3], r[4], formula, precio))

    def reset_y_cargar(self):
        self.pagina_actual = 1
        self.cargar_datos()

    def sig_pag(self):
        texto = self.search_entry.get()
        dias = self.obtener_dias_filtro()
        total_datos = len(database.buscar_clientes_servicios(texto, dias))
        total_pag = (total_datos + self.reg_por_pag - 1) // self.reg_por_pag
        if self.pagina_actual < total_pag:
            self.pagina_actual += 1
            self.cargar_datos()

    def ant_pag(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.cargar_datos()

    def generar_pdf_busqueda(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not path: return
        try:
            doc = SimpleDocTemplate(path, pagesize=A4)
            elementos = []
            estilos = getSampleStyleSheet()
            estilo_titulo = ParagraphStyle('TituloCentrado', parent=estilos['Title'], alignment=TA_CENTER, spaceAfter=20)
            estilo_celda = ParagraphStyle('CeldaNormal', parent=estilos['Normal'], fontSize=8, alignment=TA_CENTER)
            estilo_celda.wordWrap = 'CJK'

            elementos.append(Paragraph("Reporte General de Servicios", estilo_titulo))

            datos_db = database.buscar_clientes_servicios(self.search_entry.get(), self.obtener_dias_filtro())

            # Encabezados del PDF con la nueva columna
            encabezados = ["Nro", "Fecha", "Nombre", "Apellido", "Servicio", "Fórmula", "Precio"]
            tabla_datos = [[Paragraph(f"<b>{h}</b>", estilo_celda) for h in encabezados]]

            for i, r in enumerate(datos_db, 1):
                tabla_datos.append([
                    Paragraph(str(i), estilo_celda),
                    Paragraph(str(r[1]), estilo_celda),
                    Paragraph(str(r[2]), estilo_celda),
                    Paragraph(str(r[3]), estilo_celda),
                    Paragraph(str(r[4]), estilo_celda),
                    Paragraph(str(r[5] if r[5] else ""), estilo_celda),
                    Paragraph(f"${r[6]:.2f}" if r[6] is not None else "$0.00", estilo_celda)
                ])

            # Ajuste de anchos de columna para el PDF (A4 tiene ~540 puntos de ancho útil)
            t = Table(tabla_datos, colWidths=[25, 65, 75, 75, 110, 110, 60])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ffc107")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ]))
            elementos.append(t)
            doc.build(elementos)
            messagebox.showinfo("Éxito", "Reporte generado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF: {e}")