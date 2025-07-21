import sqlite3
from datetime import datetime
import os

DB_LOCAL = "tiendita.db"

APPDATA_DIR = os.path.join(os.getenv("APPDATA"), "MiniMarketPOS")
os.makedirs(APPDATA_DIR, exist_ok=True)

DB_PROD = os.path.join(APPDATA_DIR, "tiendita.db")

# Alterna entre local y producción con una variable o 
#default 0 = usa la base de produccion
USE_LOCAL_DB = os.getenv("TIENDITA_LOCAL_DB", "0") == "1"


def conectar():
    if USE_LOCAL_DB:
        return sqlite3.connect(DB_LOCAL)
    else:
        return sqlite3.connect(DB_PROD)


def inicializar_db():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_producto TEXT NOT NULL,
            marca_producto TEXT,
            stock_inicial INTEGER NOT NULL,
            costo_compra REAL NOT NULL,
            precio_venta REAL,
            descripcion TEXT,
            stock_final INTEGER NOT NULL,
            codigo_barras TEXT UNIQUE,
            imagen_producto BLOB,
            status TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_producto TEXT NOT NULL,
            descripcion_producto TEXT NOT NULL,
            marca_producto TEXT,
            cantidad INTEGER NOT NULL,
            costo REAL NOT NULL,
            precio REAL,
            codigo_barras TEXT,
            imagen_producto BLOB,
            proveedor TEXT,
            fecha_registro TEXT NOT NULL
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            forma_cobro TEXT DEFAULT 'efectivo',
            fecha_registro TEXT NOT NULL,
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        )
    """
    )

    conn.commit()
    conn.close()


def agregar_producto(codigo, nombre, precio, stock):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO productos (
                nombre_producto, marca_producto, stock_inicial, costo_compra, precio_venta, descripcion, stock_final, codigo_barras, imagen_producto, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nombre,  # nombre_producto
                None,  # marca_producto
                stock,  # stock_inicial
                0.0,  # costo_compra (debe ser obligatorio en UI)
                precio,  # precio_venta
                None,  # descripcion
                stock,  # stock_final (igual al inicial al crear)
                codigo,  # codigo_barras
                None,  # imagen_producto
                "on_stock" if stock > 0 else "agotado",  # status
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise Exception("El código ya existe")
    finally:
        conn.close()


def obtener_productos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_producto, nombre_producto, marca_producto, stock_inicial, costo_compra, precio_venta, descripcion, stock_final, codigo_barras, status FROM productos"
    )
    productos = cursor.fetchall()
    conn.close()
    return productos


def registrar_venta(id_producto, cantidad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_producto, nombre_producto, precio_venta, stock_final FROM productos WHERE id_producto = ?",
        (id_producto,),
    )
    producto = cursor.fetchone()
    if producto:
        id_prod, nombre, precio, stock = producto
        # Si el precio es None, la función debe recibir el precio como argumento
        if stock >= cantidad:
            # Si el precio es None, usar el precio ingresado en la venta
            if precio is None:
                # Buscar el precio ingresado en la venta desde la llamada (main.py lo calcula)
                # Para compatibilidad, obtener el precio desde la variable global temporal
                from inspect import currentframe

                frame = currentframe().f_back
                precio_input = frame.f_locals.get("precio", None)
                if precio_input is not None:
                    precio = precio_input
                    # Actualizar el precio en la base de datos
                    cursor.execute(
                        "UPDATE productos SET precio_venta = ? WHERE id_producto = ?",
                        (precio, id_prod),
                    )
            total = precio * cantidad
            nueva_fecha = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "INSERT INTO ventas (id_producto, cantidad, precio, fecha_registro) VALUES (?, ?, ?, ?)",
                (id_prod, cantidad, precio, nueva_fecha),
            )
            nuevo_stock = stock - cantidad
            status = (
                "agotado"
                if nuevo_stock == 0
                else ("on_stock" if nuevo_stock > 0 else "sobrevendido")
            )
            cursor.execute(
                "UPDATE productos SET stock_final = ?, status = ? WHERE id_producto = ?",
                (nuevo_stock, status, id_prod),
            )
            conn.commit()
            conn.close()
            return nombre, total, precio
    conn.close()
    return None, None, None


def ventas_del_dia():
    conn = conectar()
    cursor = conn.cursor()
    hoy = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        """
        SELECT p.id_producto, p.nombre_producto, v.cantidad, v.precio * v.cantidad as total
        FROM ventas v
        JOIN productos p ON v.id_producto = p.id_producto
        WHERE v.fecha_registro = ?
        """,
        (hoy,),
    )
    ventas = cursor.fetchall()
    conn.close()
    return ventas


def generar_ticket(id_producto, nombre, cantidad, precio_unitario, total):
    hoy = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"ticket_{id_producto}_{hoy}.txt"
    tickets_folder = "tickets"
    if not os.path.exists(tickets_folder):
        os.makedirs(tickets_folder)
    ruta = os.path.join(tickets_folder, nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("==== MINI MARKET POS ====\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("--------------------------\n")
        f.write(f"ID producto: {id_producto}\n")
        f.write(f"Producto: {nombre}\n")
        f.write(f"Cantidad: {cantidad}\n")
        f.write(f"Precio unitario: ${precio_unitario:.2f}\n")
        f.write(f"Total: ${total:.2f}\n")
        f.write("==========================\n")
        f.write("¡Gracias por su compra!\n")

    return ruta


def registrar_compra(
    nombre_producto,
    descripcion_producto,
    marca_producto,
    cantidad,
    costo,
    precio=None,
    codigo_barras=None,
    imagen_producto=None,
    proveedor=None,
):
    """
    Registra una compra y actualiza el stock_final y status del producto correspondiente.
    Si el producto no existe, no hace nada (puedes adaptar para crear el producto si lo deseas).
    """
    conn = conectar()
    cursor = conn.cursor()
    fecha_registro = datetime.now().strftime("%Y-%m-%d")
    # Registrar la compra
    cursor.execute(
        """
        INSERT INTO compras (
            nombre_producto, descripcion_producto, marca_producto, cantidad, costo, precio, codigo_barras, imagen_producto, proveedor, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            nombre_producto,
            descripcion_producto,
            marca_producto,
            cantidad,
            costo,
            precio,
            codigo_barras,
            imagen_producto,
            proveedor,
            fecha_registro,
        ),
    )
    # Actualizar stock y status en productos
    cursor.execute(
        "SELECT id_producto, stock_final FROM productos WHERE nombre_producto = ?",
        (nombre_producto,),
    )
    prod = cursor.fetchone()
    if prod:
        id_producto, stock_final = prod
        nuevo_stock = stock_final + cantidad
        status = (
            "agotado"
            if nuevo_stock == 0
            else ("on_stock" if nuevo_stock > 0 else "sobrevendido")
        )
        cursor.execute(
            "UPDATE productos SET stock_final = ?, status = ? WHERE id_producto = ?",
            (nuevo_stock, status, id_producto),
        )
    else:
        # Si el producto no existe, lo creamos con los datos de la compra
        cursor.execute(
            """
            INSERT INTO productos (
                nombre_producto, marca_producto, stock_inicial, costo_compra, precio_venta, descripcion, stock_final, codigo_barras, imagen_producto, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nombre_producto,
                marca_producto,
                cantidad,  # stock_inicial
                costo,
                precio,
                descripcion_producto,
                cantidad,  # stock_final
                codigo_barras,
                imagen_producto,
                "on_stock" if cantidad > 0 else "agotado",
            ),
        )
    conn.commit()
    conn.close()
