
import sqlite3
from datetime import datetime
import os

APPDATA_DIR = os.path.join(os.getenv("APPDATA"), "MiniMarketPOS")
os.makedirs(APPDATA_DIR, exist_ok=True)

DB_NAME = os.path.join(APPDATA_DIR, "tiendita.db")

def conectar():
    return sqlite3.connect(DB_NAME)

def inicializar_db():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    ''')

    conn.commit()
    conn.close()

def agregar_producto(codigo, nombre, precio, stock):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)",
                       (codigo, nombre, precio, stock))
        conn.commit()
    except sqlite3.IntegrityError:
        raise Exception("El código ya existe")
    finally:
        conn.close()

def obtener_productos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, codigo, nombre, precio, stock FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

def registrar_venta(codigo, cantidad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, precio, stock FROM productos WHERE codigo = ?", (codigo,))
    producto = cursor.fetchone()
    if producto:
        id_prod, nombre, precio, stock = producto
        if stock >= cantidad:
            total = precio * cantidad
            nueva_fecha = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("INSERT INTO ventas (fecha, producto_id, cantidad, total) VALUES (?, ?, ?, ?)",
                           (nueva_fecha, id_prod, cantidad, total))
            cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, id_prod))
            conn.commit()
            conn.close()
            return nombre, total, precio
    conn.close()
    return None, None, None

def ventas_del_dia():
    conn = conectar()
    cursor = conn.cursor()
    hoy = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT p.codigo, p.nombre, v.cantidad, v.total
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
        WHERE v.fecha = ?
    ''', (hoy,))
    ventas = cursor.fetchall()
    conn.close()
    return ventas


def generar_ticket(codigo, nombre, cantidad, precio_unitario, total):
    hoy = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f"ticket_{codigo}_{hoy}.txt"

    tickets_folder = os.path.join(APPDATA_DIR, "tickets")
    os.makedirs(tickets_folder, exist_ok=True)

    ruta = os.path.join(tickets_folder, nombre_archivo)

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("==== MINI MARKET POS ====\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("--------------------------\n")
        f.write(f"Código: {codigo}\n")
        f.write(f"Producto: {nombre}\n")
        f.write(f"Cantidad: {cantidad}\n")
        f.write(f"Precio unitario: ${precio_unitario:.2f}\n")
        f.write(f"Total: ${total:.2f}\n")
        f.write("==========================\n")
        f.write("¡Gracias por su compra!\n")

    return ruta
