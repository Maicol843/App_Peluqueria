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

class IngresosFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pagina_actual = 1
        self.reg_por_pag = 10

        # --- TÍTULO ---
        ctk.CTkLabel(self, text="Ingresos", font=("Arial", 28, "bold")).pack(pady=(20, 10))

        # --- CONTENEDOR ÚNICO DE FILTROS Y BOTONES (CENTRADOS) ---
        self.main_toolbar = ctk.CTkFrame(self, fg_color="transparent")
        self.main_toolbar.pack(pady=10, fill="x")

        # Sub-frame interno para centrar todo el contenido
        self.center_frame = ctk.CTkFrame(self.main_toolbar, fg_color="transparent")
        self.center_frame.pack(anchor="center")

        # 1. Buscador por Servicio
        ctk.CTkLabel(self.center_frame, text="Servicio:").pack(side="left", padx=(10, 2))
        self.search_ser = ctk.CTkEntry(self.center_frame, placeholder_text="Buscar...", width=140)
        self.search_ser.pack(side="left", padx=5)
        self.search_ser.bind("<KeyRelease>", lambda e: self.reset_y_cargar())

        # 2. Buscador de Fechas (Desde - Hasta)
        ctk.CTkLabel(self.center_frame, text="Desde:").pack(side="left", padx=(10, 2))
        self.ent_desde = ctk.CTkEntry(self.center_frame, placeholder_text="dd/mm/aaaa", width=100)
        self.ent_desde.pack(side="left", padx=5)
        self.ent_desde.bind("<KeyRelease>", lambda e: self.reset_y_cargar())

        ctk.CTkLabel(self.center_frame, text="Hasta:").pack(side="left", padx=(5, 2))
        self.ent_hasta = ctk.CTkEntry(self.center_frame, placeholder_text="dd/mm/aaaa", width=100)
        self.ent_hasta.pack(side="left", padx=5)
        self.ent_hasta.bind("<KeyRelease>", lambda e: self.reset_y_cargar())

        # 3. Botones de Acción
        self.btn_mes = ctk.CTkButton(self.center_frame, text="Gráfica Mes", width=100, fg_color="#1f538d", command=self.grafica_mes)
        self.btn_mes.pack(side="left", padx=5)

        self.btn_anio = ctk.CTkButton(self.center_frame, text="Gráfica Año", width=100, fg_color="#1f538d", command=self.grafica_anio)
        self.btn_anio.pack(side="left", padx=5)

        self.btn_pdf = ctk.CTkButton(self.center_frame, text="Descargar", width=100, fg_color="#1f538d", command=self.generar_pdf_ingresos)
        self.btn_pdf.pack(side="left", padx=5)

        # --- TABLA ---
        self.tabla = ttk.Treeview(self, columns=("num", "fec", "ser", "ing"), show='headings')
        self.tabla.heading("num", text="Nro.")
        self.tabla.heading("fec", text="Fecha")
        self.tabla.heading("ser", text="Servicio")
        self.tabla.heading("ing", text="Ingreso ($)")
        
        self.tabla.column("num", width=50, anchor="center")
        self.tabla.column("fec", width=120, anchor="center")
        self.tabla.column("ser", width=300, anchor="center")
        self.tabla.column("ing", width=100, anchor="center")
        self.tabla.pack(expand=True, fill="both", padx=40, pady=10)

        # --- TOTAL ACUMULADO ---
        self.lbl_total = ctk.CTkLabel(self, text="Total Ingresos: $0.00", font=("Arial", 20, "bold"), text_color="#2ecc71")
        self.lbl_total.pack(pady=5)

        # --- PAGINACIÓN ---
        self.pag_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pag_frame.pack(pady=10)
        
        self.btn_prev = ctk.CTkButton(self.pag_frame, text="<", width=40, command=self.ant_pag)
        self.btn_prev.pack(side="left", padx=10)
        
        self.lbl_pag = ctk.CTkLabel(self.pag_frame, text="Página 1 de 1", font=("Arial", 12, "bold"))
        self.lbl_pag.pack(side="left")
        
        self.btn_next = ctk.CTkButton(self.pag_frame, text=">", width=40, command=self.sig_pag)
        self.btn_next.pack(side="left", padx=10)

        self.cargar_datos()

    # --- LÓGICA DE DATOS ---
    def obtener_filtros_fechas(self):
        desde = self.ent_desde.get()
        hasta = self.ent_hasta.get()
        return (desde if len(desde) == 10 else None), (hasta if len(hasta) == 10 else None)

    def cargar_datos(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        f_desde, f_hasta = self.obtener_filtros_fechas()
        texto = self.search_ser.get()
        
        total = database.obtener_total_ingresos(texto, f_desde, f_hasta)
        self.lbl_total.configure(text=f"Total Ingresos: ${total:.2f}")

        datos = database.obtener_ingresos_filtrados(texto, f_desde, f_hasta)
        total_pag = max(1, (len(datos) + self.reg_por_pag - 1) // self.reg_por_pag)
        self.lbl_pag.configure(text=f"Página {self.pagina_actual} de {total_pag}")
        
        inicio = (self.pagina_actual - 1) * self.reg_por_pag
        for i, r in enumerate(datos[inicio:inicio+self.reg_por_pag], start=inicio+1):
            self.tabla.insert("", "end", values=(i, r[1], r[2], f"${r[3]:.2f}"))

    def reset_y_cargar(self):
        self.pagina_actual = 1
        self.cargar_datos()

    def sig_pag(self):
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
        ventana.grab_set() 
        return ventana

    def grafica_mes(self):
        mes_actual = datetime.now().strftime("%m")
        anio_actual = datetime.now().strftime("%Y")
        datos = database.obtener_ingresos_filtrados("", None, None)
        
        dias_acumulados = {}
        for r in datos:
            fec = r[1]
            partes = fec.split("/")
            if partes[1] == mes_actual and partes[2] == anio_actual:
                dia = partes[0]
                dias_acumulados[dia] = dias_acumulados.get(dia, 0) + r[3]

        if not dias_acumulados:
            messagebox.showinfo("Información", "No hay datos para el mes actual.")
            return

        ventana = self.crear_ventana_grafica(f"Gráfica - Mes {mes_actual}")
        fig, ax = plt.subplots(figsize=(6, 4))
        dias_ordenados = sorted(dias_acumulados.keys(), key=int)
        valores = [dias_acumulados[d] for d in dias_ordenados]
        ax.bar(dias_ordenados, valores, color='#1f538d')
        ax.set_title(f"Ingresos Diarios ({mes_actual}/{anio_actual})")
        
        canvas = FigureCanvasTkAgg(fig, master=ventana)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def grafica_anio(self):
        anio_actual = datetime.now().strftime("%Y")
        datos = database.obtener_ingresos_filtrados("", None, None)
        meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        valores = [0] * 12
        
        hay_datos = False
        for r in datos:
            partes = r[1].split("/")
            if partes[2] == anio_actual:
                valores[int(partes[1]) - 1] += r[3]
                hay_datos = True

        if not hay_datos:
            messagebox.showinfo("Información", "No hay datos para el año actual.")
            return

        ventana = self.crear_ventana_grafica(f"Gráfica - Año {anio_actual}")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(meses_nombres, valores, color='#1f538d')
        ax.set_title(f"Ingresos Mensuales {anio_actual}")
        
        canvas = FigureCanvasTkAgg(fig, master=ventana)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # --- PDF ---
    def generar_pdf_ingresos(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not path: return
        try:
            doc = SimpleDocTemplate(path, pagesize=A4)
            estilos = getSampleStyleSheet()
            estilo_titulo = ParagraphStyle('Title', parent=estilos['Title'], alignment=TA_CENTER)
            elementos = [Paragraph("Ingresos", estilo_titulo), Spacer(1, 20)]
            
            f_desde, f_hasta = self.obtener_filtros_fechas()
            datos_db = database.obtener_ingresos_filtrados(self.search_ser.get(), f_desde, f_hasta)
            
            data_tabla = [["Nro.", "Fecha", "Servicio", "Ingreso"]]
            for i, r in enumerate(datos_db, 1):
                data_tabla.append([i, r[1], r[2], f"${r[3]:.2f}"])
            
            t = Table(data_tabla, colWidths=[40, 100, 280, 80])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2c3e50")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ]))
            elementos.append(t)
            doc.build(elementos)
            messagebox.showinfo("Éxito", "PDF generado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")