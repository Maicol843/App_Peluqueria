import sqlite3

def crear_base_de_datos():
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    # Tabla de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            fecha_nacimiento TEXT NOT NULL,
            email TEXT,
            telefono TEXT
        )
    ''')
    # Tabla de servicios (Relacionada con clientes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            fecha TEXT NOT NULL,
            servicio TEXT NOT NULL,
            precio REAL NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')
    conexion.commit()
    conexion.close()

# --- FUNCIONES DE CLIENTES ---

def registrar_cliente(nombre, apellido, fecha, email, telefono):
    try:
        if not nombre or not apellido:
            return False
        conexion = sqlite3.connect("peluqueria.db")
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO clientes (nombre, apellido, fecha_nacimiento, email, telefono)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, apellido, fecha, email, telefono))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def obtener_clientes(busqueda=""):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    if busqueda:
        cursor.execute("SELECT * FROM clientes WHERE nombre LIKE ? OR apellido LIKE ?", (f"%{busqueda}%", f"%{busqueda}%"))
    else:
        cursor.execute("SELECT * FROM clientes")
    datos = cursor.fetchall()
    conexion.close()
    return datos

def actualizar_cliente(id_cliente, nombre, apellido, fecha, email, telefono):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute('''
        UPDATE clientes SET nombre=?, apellido=?, fecha_nacimiento=?, email=?, telefono=?
        WHERE id=?
    ''', (nombre, apellido, fecha, email, telefono, id_cliente))
    conexion.commit()
    conexion.close()

def eliminar_cliente(id_cliente):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=?", (id_cliente,))
    # También eliminamos sus servicios para mantener la integridad
    cursor.execute("DELETE FROM servicios WHERE cliente_id=?", (id_cliente,))
    conexion.commit()
    conexion.close()

def eliminar_todos_los_clientes():
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes")
    cursor.execute("DELETE FROM servicios")
    conexion.commit()
    conexion.close()

# --- FUNCIONES DE SERVICIOS ---

def registrar_servicio(cliente_id, fecha, servicio, precio):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO servicios (cliente_id, fecha, servicio, precio) VALUES (?, ?, ?, ?)",
                   (cliente_id, fecha, servicio, precio))
    conexion.commit()
    conexion.close()

def obtener_servicios(cliente_id, busqueda=""):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    if busqueda:
        cursor.execute("SELECT * FROM servicios WHERE cliente_id = ? AND servicio LIKE ?", (cliente_id, f"%{busqueda}%"))
    else:
        cursor.execute("SELECT * FROM servicios WHERE cliente_id = ?", (cliente_id,))
    datos = cursor.fetchall()
    conexion.close()
    return datos

def actualizar_servicio(id_ser, fecha, servicio, precio):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute("UPDATE servicios SET fecha=?, servicio=?, precio=? WHERE id=?", (fecha, servicio, precio, id_ser))
    conexion.commit()
    conexion.close()

def eliminar_servicio(id_ser):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM servicios WHERE id=?", (id_ser,))
    conexion.commit()
    conexion.close()

def eliminar_servicios_cliente(cliente_id):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM servicios WHERE cliente_id=?", (cliente_id,))
    conexion.commit()
    conexion.close()

def buscar_clientes_servicios(texto="", dias=None):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    
    # Query base que une ambas tablas
    query = """
        SELECT s.id, s.fecha, c.nombre, c.apellido, s.servicio, s.precio
        FROM servicios s
        JOIN clientes c ON s.cliente_id = c.id
        WHERE (c.nombre LIKE ? OR c.apellido LIKE ? OR s.servicio LIKE ?)
    """
    params = [f"%{texto}%", f"%{texto}%", f"%{texto}%"]

    if dias is not None:
        # CORRECCIÓN LÓGICA: Convertimos DD/MM/YYYY a YYYY-MM-DD para que SQLite calcule bien los días
        query += """ 
            AND date(substr(s.fecha,7,4) || '-' || substr(s.fecha,4,2) || '-' || substr(s.fecha,1,2)) 
            >= date('now', 'localtime', ?)
        """
        params.append(f"-{dias} days")

    # Ordenar por fecha más reciente
    query += " ORDER BY substr(s.fecha,7,4) DESC, substr(s.fecha,4,2) DESC, substr(s.fecha,1,2) DESC"

    cursor.execute(query, params)
    datos = cursor.fetchall()
    conexion.close()
    return datos

def obtener_ingresos_filtrados(servicio="", desde=None, hasta=None):
    import sqlite3
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    
    # Query base: Buscamos por servicio (el primer ?)
    query = "SELECT id, fecha, servicio, precio FROM servicios WHERE servicio LIKE ?"
    params = [f"%{servicio}%"]

    # Filtro por rango de fecha
    if desde and hasta:
        # Cada '?' requiere un valor en la lista params. 
        # Como usamos substr 3 veces para 'desde' y 3 veces para 'hasta', 
        # debemos pasar las variables 3 veces cada una.
        query += """ AND date(substr(fecha,7,4) || '-' || substr(fecha,4,2) || '-' || substr(fecha,1,2)) 
                     BETWEEN date(substr(?,7,4) || '-' || substr(?,4,2) || '-' || substr(?,1,2)) 
                     AND date(substr(?,7,4) || '-' || substr(?,4,2) || '-' || substr(?,1,2)) """
        
        # Agregamos 'desde' 3 veces y 'hasta' 3 veces para llenar los 6 signos '?' del BETWEEN
        params.extend([desde, desde, desde, hasta, hasta, hasta])
    
    # Ordenar por fecha reciente
    query += " ORDER BY substr(fecha,7,4) DESC, substr(fecha,4,2) DESC, substr(fecha,1,2) DESC"
    
    cursor.execute(query, params)
    datos = cursor.fetchall()
    conexion.close()
    return datos

def obtener_total_ingresos(servicio="", desde=None, hasta=None):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    
    query = "SELECT SUM(precio) FROM servicios WHERE servicio LIKE ?"
    params = [f"%{servicio}%"]

    if desde and hasta:
        query += """ AND date(substr(fecha,7,4) || '-' || substr(fecha,4,2) || '-' || substr(fecha,1,2)) 
                     BETWEEN date(substr(?,7,4) || '-' || substr(?,4,2) || '-' || substr(?,1,2)) 
                     AND date(substr(?,7,4) || '-' || substr(?,4,2) || '-' || substr(?,1,2)) """
        params.extend([desde, desde, desde, hasta, hasta, hasta])
    
    cursor.execute(query, params)
    total = cursor.fetchone()[0]
    conexion.close()
    
    return total if total else 0.0

def crear_tabla_egresos():
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS egresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            detalle TEXT NOT NULL,
            importe REAL NOT NULL
        )
    ''')
    conexion.commit()
    conexion.close()

def registrar_egreso(fecha, detalle, importe):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO egresos (fecha, detalle, importe) VALUES (?, ?, ?)", (fecha, detalle, importe))
    conexion.commit()
    conexion.close()

def obtener_egresos_filtrados(detalle="", desde=None, hasta=None):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    query = "SELECT id, fecha, detalle, importe FROM egresos WHERE detalle LIKE ?"
    params = [f"%{detalle}%"]
    if desde and hasta:
        query += """ AND date(substr(fecha,7,4) || '-' || substr(fecha,4,2) || '-' || substr(fecha,1,2)) 
                     BETWEEN date(substr(?,7,4) || '-' || substr(?,4,2) || '-' || substr(?,1,2)) 
                     AND date(substr(?,7,4) || '-' || substr(?,4,2) || '-' || substr(?,1,2)) """
        params.extend([desde, desde, desde, hasta, hasta, hasta])
    query += " ORDER BY substr(fecha,7,4) DESC, substr(fecha,4,2) DESC, substr(fecha,1,2) DESC"
    cursor.execute(query, params)
    datos = cursor.fetchall()
    conexion.close()
    return datos

def obtener_total_egresos(detalle="", desde=None, hasta=None):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    query = "SELECT SUM(importe) FROM egresos WHERE detalle LIKE ?"
    params = [f"%{detalle}%"]
    if desde and hasta:
        query += """ AND date(substr(fecha,7,4) || '-' || substr(fecha,4,2) || '-' || substr(fecha,1,2)) 
                     BETWEEN date(substr(?,7,4) || '-' || substr(?,4,2) || '-' || substr(?,1,2)) 
                     AND date(substr(?,7,4) || '-' || substr(?,4,2) || '-' || substr(?,1,2)) """
        params.extend([desde, desde, desde, hasta, hasta, hasta])
    cursor.execute(query, params)
    total = cursor.fetchone()[0]
    conexion.close()
    return total if total else 0.0

def actualizar_egreso(id_egreso, fecha, detalle, importe):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute("UPDATE egresos SET fecha=?, detalle=?, importe=? WHERE id=?", (fecha, detalle, importe, id_egreso))
    conexion.commit()
    conexion.close()

def eliminar_egreso(id_egreso):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM egresos WHERE id=?", (id_egreso,))
    conexion.commit()
    conexion.close()

def restablecer_egresos():
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM egresos")
    conexion.commit()
    conexion.close()

def obtener_egresos_grafica():
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    # Obtenemos fecha e importe para procesar en Python
    cursor.execute("SELECT fecha, importe FROM egresos")
    datos = cursor.fetchall()
    conexion.close()
    return datos

# Inicialización automática al importar el archivo
crear_base_de_datos()
