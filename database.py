import sqlite3

def crear_base_de_datos():
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    # Creamos la tabla de clientes
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
    conexion.commit()
    conexion.close()

def registrar_cliente(nombre, apellido, fecha, email, telefono):
    try:
        # Validación básica: nombre y apellido no pueden estar vacíos
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
        print(f"Error en la base de datos: {e}")
        return False
    
def obtener_clientes(busqueda=""):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    if busqueda:
        query = "SELECT * FROM clientes WHERE nombre LIKE ? OR apellido LIKE ? OR email LIKE ?"
        param = f"%{busqueda}%"
        cursor.execute(query, (param, param, param))
    else:
        cursor.execute("SELECT * FROM clientes")
    datos = cursor.fetchall()
    conexion.close()
    return datos

def actualizar_cliente(id_cl, nombre, apellido, fecha, email, telefono):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute('''UPDATE clientes SET nombre=?, apellido=?, fecha_nacimiento=?, email=?, telefono=? WHERE id=?''', 
                   (nombre, apellido, fecha, email, telefono, id_cl))
    conexion.commit()
    conexion.close()

def eliminar_cliente(id_cl):
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=?", (id_cl,))
    conexion.commit()
    conexion.close()

def eliminar_todos_los_clientes():
    conexion = sqlite3.connect("peluqueria.db")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes")
    conexion.commit()
    conexion.close()

# Ejecutar la creación al importar
crear_base_de_datos()