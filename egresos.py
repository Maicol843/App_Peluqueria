import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import database
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime

class EgresosFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        database.crear_tabla_egresos()
        self.pagina_actual = 1
        self.reg_por_pag = 10

        # --- TÍTULO ---
        ctk.CTkLabel(self, text="Egresos", font=("Arial", 28, "bold")).pack(pady=(20, 10))

        # --- CONTENEDOR DE HERRAMIENTAS (TOOLBAR) ---
        self.toolbar_container = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar_container.pack(pady=5, fill="x")

        # FILA 1: BOTONES DE ACCIÓN
        self.button_row = ctk.CTkFrame(self.toolbar_container, fg_color="transparent")
        self.button_row.pack(anchor="center", pady=5)

        ctk.CTkButton(self.button_row, text="Gráfica Mes", width=100, fg_color="#1f538d", command=self.grafica_mes).pack(side="left", padx=5)
        ctk.CTkButton(self.button_row, text="Gráfica Año", width=100, fg_color="#1f538d", command=self.grafica_anio).pack(side="left", padx=5)
        ctk.CTkButton(self.button_row, text="Insertar", width=100, fg_color="#1f538d", command=self.abrir_formulario).pack(side="left", padx=5)
        ctk.CTkButton(self.button_row, text="Editar", width=100, fg_color="#1f538d", command=self.editar_seleccionado).pack(side="left", padx=5)
        ctk.CTkButton(self.button_row, text="Eliminar", width=100, fg_color="#1f538d", command=self.eliminar_seleccionado).pack(side="left", padx=5)
        ctk.CTkButton(self.button_row, text="Restablecer", width=110, fg_color="#1f538d", command=self.restablecer_todo).pack(side="left", padx=5)
        ctk.CTkButton(self.button_row, text="Descargar", width=120, fg_color="#1f538d", command=self.descargar_pdf).pack(side="left", padx=5)

        # FILA 2: BUSCADORES Y FILTROS
        self.search_row = ctk.CTkFrame(self.toolbar_container, fg_color="transparent")
        self.search_row.pack(anchor="center", pady=5)

        ctk.CTkLabel(self.search_row, text="Detalle:").pack(side="left", padx=2)
        self.search_det = ctk.CTkEntry(self.search_row, placeholder_text="Buscar por detalle...", width=180)
        self.search_det.pack(side="left", padx=10)
        self.search_det.bind("<KeyRelease>", lambda e: self.reset_y_cargar())

        ctk.CTkLabel(self.search_row, text="Desde:").pack(side="left", padx=2)
        self.ent_desde = ctk.CTkEntry(self.search_row, placeholder_text="dd/mm/aaaa", width=110)
        self.ent_desde.pack(side="left", padx=5)
        self.ent_desde.bind("<KeyRelease>", lambda e: self.reset_y_cargar())

        ctk.CTkLabel(self.search_row, text="Hasta:").pack(side="left", padx=2)
        self.ent_hasta = ctk.CTkEntry(self.search_row, placeholder_text="dd/mm/aaaa", width=110)
        self.ent_hasta.pack(side="left", padx=5)
        self.ent_hasta.bind("<KeyRelease>", lambda e: self.reset_y_cargar())

        # --- TABLA ---
        self.tabla = ttk.Treeview(self, columns=("num", "fec", "det", "egr"), show='headings')
        self.tabla.heading("num", text="Nro.")
        self.tabla.heading("fec", text="Fecha")
        self.tabla.heading("det", text="Detalle")
        self.tabla.heading("egr", text="Egreso ($)")
        
        self.tabla.column("num", width=50, anchor="center")
        self.tabla.column("fec", width=120, anchor="center")
        self.tabla.column("det", width=380, anchor="center")
        self.tabla.column("egr", width=120, anchor="center")
        self.tabla.pack(expand=True, fill="both", padx=40, pady=10)

        # --- TOTAL ---
        self.lbl_total = ctk.CTkLabel(self, text="Total Egresos: $0.00", font=("Arial", 20, "bold"), text_color="#e74c3c")
        self.lbl_total.pack(pady=5)

        # --- PAGINACIÓN ---
        self.pag_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pag_frame.pack(pady=10)
        ctk.CTkButton(self.pag_frame, text="<", width=40, command=self.ant_pag).pack(side="left", padx=10)
        self.lbl_pag = ctk.CTkLabel(self.pag_frame, text="Página 1 de 1", font=("Arial", 12, "bold"))
        self.lbl_pag.pack(side="left")
        ctk.CTkButton(self.pag_frame, text=">", width=40, command=self.sig_pag).pack(side="left", padx=10)

        self.cargar_datos()

    # --- LÓGICA DE DATOS ---
    def obtener_filtros(self):
        d = self.ent_desde.get()
        h = self.ent_hasta.get()
        return (d if len(d)==10 else None), (h if len(h)==10 else None)

    def cargar_datos(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        f_d, f_h = self.obtener_filtros()
        txt = self.search_det.get()
        
        total = database.obtener_total_egresos(txt, f_d, f_h)
        self.lbl_total.configure(text=f"Total Egresos: ${total:.2f}")

        datos = database.obtener_egresos_filtrados(txt, f_d, f_h)
        t_pag = max(1, (len(datos) + self.reg_por_pag - 1) // self.reg_por_pag)
        
        if self.pagina_actual > t_pag: self.pagina_actual = t_pag
        self.lbl_pag.configure(text=f"Página {self.pagina_actual} de {t_pag}")
        
        inicio = (self.pagina_actual - 1) * self.reg_por_pag
        for i, r in enumerate(datos[inicio:inicio+self.reg_por_pag], start=inicio+1):
            self.tabla.insert("", "end", values=(i, r[1], r[2], f"${r[3]:.2f}"), iid=r[0])

    def reset_y_cargar(self):
        self.pagina_actual = 1
        self.cargar_datos()

    def sig_pag(self):
        f_d, f_h = self.obtener_filtros()
        datos = database.obtener_egresos_filtrados(self.search_det.get(), f_d, f_h)
        if self.pagina_actual * self.reg_por_pag < len(datos):
            self.pagina_actual += 1
            self.cargar_datos()

    def ant_pag(self): 
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.cargar_datos()

    # --- GRÁFICAS ---
    def crear_ventana_grafica(self, titulo):
        ventana = ctk.CTkToplevel(self)
        ventana.title(titulo)
        ventana.geometry("700x500")
        ventana.attributes("-topmost", True)
        ventana.grab_set()
        return ventana

    def grafica_mes(self):
        mes_act = datetime.now().strftime("%m")
        anio_act = datetime.now().strftime("%Y")
        datos = database.obtener_egresos_filtrados("", None, None)
        dias = {}
        for r in datos:
            partes = r[1].split("/")
            if len(partes) == 3 and partes[1] == mes_act and partes[2] == anio_act:
                dias[partes[0]] = dias.get(partes[0], 0) + r[3]
        if not dias:
            return messagebox.showinfo("Info", "No hay egresos en el mes actual.")
        v = self.crear_ventana_grafica(f"Egresos del Mes {mes_act}/{anio_act}")
        fig, ax = plt.subplots(figsize=(6, 4))
        d_ord = sorted(dias.keys(), key=int)
        ax.bar(d_ord, [dias[d] for d in d_ord], color='#1f538d')
        ax.set_title("Egresos por Día")
        canvas = FigureCanvasTkAgg(fig, master=v)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def grafica_anio(self):
        anio_act = datetime.now().strftime("%Y")
        datos = database.obtener_egresos_filtrados("", None, None)
        meses_n = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        valores = [0] * 12
        hay = False
        for r in datos:
            p = r[1].split("/")
            if len(p) == 3 and p[2] == anio_act:
                valores[int(p[1]) - 1] += r[3]
                hay = True
        if not hay:
            return messagebox.showinfo("Info", f"No hay egresos en {anio_act}.")
        v = self.crear_ventana_grafica(f"Egresos de {anio_act}")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(meses_n, valores, color='#1f538d')
        ax.set_title(f"Egresos Mensuales {anio_act}")
        canvas = FigureCanvasTkAgg(fig, master=v)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # --- CRUD Y PDF ---
    def abrir_formulario(self, edit_data=None):
        v = ctk.CTkToplevel(self)
        v.title("Egreso" if not edit_data else "Editar Egreso")
        v.geometry("350x400")
        v.attributes("-topmost", True)
        v.grab_set()
        ctk.CTkLabel(v, text="Fecha (dd/mm/aaaa):").pack(pady=(20,0))
        ent_f = ctk.CTkEntry(v, width=200)
        ent_f.pack(pady=5)
        ent_f.insert(0, datetime.now().strftime("%d/%m/%Y") if not edit_data else edit_data[1])
        ctk.CTkLabel(v, text="Detalle:").pack(pady=(10,0))
        ent_d = ctk.CTkEntry(v, width=200)
        ent_d.pack(pady=5)
        if edit_data: ent_d.insert(0, edit_data[2])
        ctk.CTkLabel(v, text="Importe ($):").pack(pady=(10,0))
        ent_i = ctk.CTkEntry(v, width=200)
        ent_i.pack(pady=5)
        if edit_data: ent_i.insert(0, str(edit_data[3]).replace("$",""))
        def guardar():
            try:
                f, d, i = ent_f.get(), ent_d.get(), float(ent_i.get())
                if not edit_data: database.registrar_egreso(f, d, i)
                else: database.actualizar_egreso(edit_data[0], f, d, i)
                v.destroy(); self.cargar_datos()
            except: messagebox.showerror("Error", "Datos inválidos")
        ctk.CTkButton(v, text="Guardar", fg_color="#2ecc71", command=guardar).pack(pady=30)

    def editar_seleccionado(self):
        sel = self.tabla.selection()
        if not sel: return messagebox.showwarning("Atención", "Seleccione un registro")
        item = self.tabla.item(sel[0])['values']
        self.abrir_formulario([sel[0], item[1], item[2], item[3]])

    def eliminar_seleccionado(self):
        sel = self.tabla.selection()
        if not sel: return
        if messagebox.askyesno("Confirmar", "¿Eliminar este egreso?"):
            database.eliminar_egreso(sel[0]); self.cargar_datos()

    def restablecer_todo(self):
        if messagebox.askyesno("Peligro", "¿Desea eliminar TODO el historial?"):
            database.restablecer_egresos(); self.reset_y_cargar()

    def descargar_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not path: return
        try:
            doc = SimpleDocTemplate(path, pagesize=A4)
            est = getSampleStyleSheet()
            
            # Estilo para el título centrado
            t_est = ParagraphStyle('T', parent=est['Title'], alignment=TA_CENTER)
            
            # Estilo para el contenido de las celdas (evita que el texto se salga)
            estilo_celda = ParagraphStyle('Celda', parent=est['Normal'], fontSize=10, alignment=TA_CENTER)
            estilo_celda.wordWrap = 'CJK' # Clave para el ajuste de línea
            
            # Estilo para la fila del total
            estilo_total = ParagraphStyle('Total', parent=est['Normal'], fontSize=11, alignment=TA_CENTER)

            f_d, f_h = self.obtener_filtros()
            datos_db = database.obtener_egresos_filtrados(self.search_det.get(), f_d, f_h)
            
            # Intentamos obtener el total desde la base de datos
            try:
                total_db = database.obtener_total_egresos(self.search_det.get(), f_d, f_h)
            except:
                # Si la función falla, calculamos el total manualmente por seguridad
                total_db = sum(r[3] for r in datos_db if r[3])

            # Encabezados con Paragraph
            data = [[Paragraph(h, est['Helvetica-Bold'] if 'Helvetica-Bold' in est else est['Normal']) 
                    for h in ["Nro.", "Fecha", "Detalle", "Importe"]]]
            
            # Llenar la tabla con Paragraphs
            for i, r in enumerate(datos_db, 1):
                data.append([
                    Paragraph(str(i), estilo_celda),
                    Paragraph(str(r[1]), estilo_celda),
                    Paragraph(str(r[2]), estilo_celda), # El detalle ya no se saldrá de la celda
                    Paragraph(f"${r[3]:.2f}", estilo_celda)
                ])
            
            # --- AGREGAR FILA DE TOTAL ---
            data.append([
                "", 
                "", 
                Paragraph("<b>TOTAL:</b>", estilo_total), 
                Paragraph(f"<b>${total_db:.2f}</b>", estilo_total)
            ])
            
            # Definición de anchos: [Nro, Fecha, Detalle, Importe]
            tab = Table(data, colWidths=[40, 100, 280, 80])
            
            tab.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#c0392b")), # Color rojo para egresos
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centrado vertical
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                # Estilo para la fila del total (la última)
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#f9ebea")),
                ('LINEABOVE', (2, -1), (-1, -1), 1.5, colors.black),
            ]))
            
            elementos = [Paragraph("Reporte de Egresos", t_est), Spacer(1, 20), tab]
            doc.build(elementos)
            
            messagebox.showinfo("Éxito", "PDF generado correctamente con el total de egresos.")
        except Exception as e: 
            messagebox.showerror("Error", f"No se pudo generar el PDF: {e}")