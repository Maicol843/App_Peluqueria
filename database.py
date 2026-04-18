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

# Ejecutar la creación al importar
crear_base_de_datos()