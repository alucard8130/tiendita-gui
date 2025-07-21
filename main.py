def ventana_registrar_compra():
    win = tk.Toplevel()
    win.title("Registrar compra")
    win.geometry("500x500")

    frame = ttk.Frame(win, padding=20)
    frame.pack(fill="both", expand=True)

    campos = [
        ("Nombre producto", "nombre"),
        ("Descripción", "descripcion"),
        ("Marca", "marca"),
        ("Cantidad", "cantidad"),
        ("Costo", "costo"),
        ("Precio (opcional)", "precio"),
        ("Código de barras (opcional)", "codigo"),
        ("Proveedor (opcional)", "proveedor"),
    ]
    entradas = {}
    for i, (label, key) in enumerate(campos):
        ttk.Label(frame, text=label + ":").grid(row=i, column=0, sticky="e", pady=5)
        ent = ttk.Entry(frame)
        ent.grid(row=i, column=1, pady=5)
        entradas[key] = ent

    def guardar():
        try:
            nombre = entradas["nombre"].get()
            descripcion = entradas["descripcion"].get()
            # tipo = entradas["tipo"].get() or None
            marca = entradas["marca"].get() or None
            cantidad = int(entradas["cantidad"].get())
            costo = float(entradas["costo"].get())
            precio = entradas["precio"].get()
            precio = float(precio) if precio else None
            codigo = entradas["codigo"].get() or None
            proveedor = entradas["proveedor"].get() or None
            database.registrar_compra(
                nombre,
                descripcion,
                # tipo,
                marca,
                cantidad,
                costo,
                precio,
                codigo,
                None,
                proveedor,
            )
            messagebox.showinfo("Éxito", "Compra registrada y stock actualizado")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(frame, text="Registrar compra", command=guardar).grid(
        row=len(campos), column=0, columnspan=2, pady=15
    )


# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import database

# Inicializar base de datos al arrancar
database.inicializar_db()

# ------------------------ Ventanas ------------------------
# ------------------------ Función oculta para versión de paga ------------------------
# def registrar_compras_masivas(lista_compras):
#     '''
#     Recibe una lista de dicts con los campos:
#     nombre, descripcion, marca, cantidad, costo, precio, codigo, proveedor
#     Ejemplo:
#     compras = [
#         {"nombre": "Coca Cola", "descripcion": "Bebida", "marca": "Coca Cola", "cantidad": 10, "costo": 12.5, "precio": 15, "codigo": "12345", "proveedor": "Distribuidor X"},
#         {"nombre": "Galletas", "descripcion": "Dulce", "marca": "Gamesa", "cantidad": 20, "costo": 8, "precio": 10, "codigo": "54321", "proveedor": "Distribuidor Y"}
#     ]
#     registrar_compras_masivas(compras)
#     '''
#     for compra in lista_compras:
#         try:
#             database.registrar_compra(
#                 compra.get("nombre"),
#                 compra.get("descripcion"),
#                 compra.get("marca"),
#                 int(compra.get("cantidad", 0)),
#                 float(compra.get("costo", 0)),
#                 float(compra.get("precio", 0)) if compra.get("precio") else None,
#                 compra.get("codigo"),
#                 None,
#                 compra.get("proveedor"),
#             )
#         except Exception as e:
#             print(f"Error en compra masiva: {compra.get('nombre')}: {e}")


def ventana_agregar_producto():
    win = tk.Toplevel()
    win.title("Agregar producto")
    win.geometry("400x300")

    style = ttk.Style()
    style.configure("TEntry", font=("Segoe UI", 12))
    style.configure("TLabel", font=("Segoe UI", 12))

    frame = ttk.Frame(win, padding=20)
    frame.pack(fill="both", expand=True)

    labels = [
        ("Nombre", "nombre"),
        ("Tipo", "tipo"),
        ("Marca", "marca"),
        ("Stock inicial", "stock"),
        ("Costo compra", "costo"),
        ("Precio venta", "precio"),
        ("Descripción", "descripcion"),
        ("Código de barras (opcional)", "codigo"),
    ]
    entradas = {}
    for i, (label, key) in enumerate(labels):
        ttk.Label(frame, text=label + ":").grid(row=i, column=0, sticky="w", pady=5)
        ent = ttk.Entry(frame)
        ent.grid(row=i, column=1, pady=5)
        entradas[key] = ent

    def guardar():
        try:
            nombre = entradas["nombre"].get()
            tipo = entradas["tipo"].get() or None
            marca = entradas["marca"].get() or None
            stock = int(entradas["stock"].get())
            costo = float(entradas["costo"].get())
            precio = float(entradas["precio"].get())
            descripcion = entradas["descripcion"].get() or None
            codigo = entradas["codigo"].get() or None
            database.agregar_producto(codigo, nombre, precio, stock)
            messagebox.showinfo("Éxito", "Producto guardado correctamente")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(frame, text="Guardar", command=guardar).grid(
        row=len(labels), column=0, columnspan=2, pady=15
    )


def ventana_ver_productos():
    win = tk.Toplevel()
    win.title("Lista de productos")
    win.geometry("1250x500")

    frame = ttk.Frame(win, padding=10)
    frame.pack(fill="both", expand=True)

    ttk.Label(
        frame, text="📦 Productos disponibles", font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    columns = (
        "ID",
        "Nombre",
        "Marca",
        "Stock inicial",
        "Costo compra",
        "Precio venta",
        "Descripción",
        "Stock final",
        "Código barras",
        "Status",
    )
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
    col_widths = [60, 180, 120, 100, 100, 100, 250, 100, 120, 100]
    for i, col in enumerate(columns):
        tree.heading(col, text=col)
        tree.column(
            col, anchor="center", width=col_widths[i], minwidth=60, stretch=True
        )

    productos = database.obtener_productos()
    if not productos:
        ttk.Label(
            frame, text="No hay productos registrados.", font=("Segoe UI", 12)
        ).pack(pady=10)
    else:
        for prod in productos:
            tree.insert("", "end", values=prod)

    tree.pack(expand=True, fill="both", pady=10)


def ventana_registrar_venta():
    win = tk.Toplevel()
    win.title("Registrar venta")
    win.geometry("400x250")

    frame = ttk.Frame(win, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="💰 Registrar venta", font=("Segoe UI", 16, "bold")).grid(
        row=0, column=0, columnspan=2, pady=10
    )

    ttk.Label(frame, text="Producto:").grid(row=1, column=0, sticky="e", pady=5)
    productos = database.obtener_productos()
    opciones = [f"{p[1]} (ID:{p[0]})" for p in productos] if productos else []
    producto_var = tk.StringVar()
    producto_combo = ttk.Combobox(
        frame, textvariable=producto_var, values=opciones, state="readonly"
    )
    producto_combo.grid(row=1, column=1, pady=5)

    ttk.Label(frame, text="Cantidad:").grid(row=2, column=0, sticky="e", pady=5)
    cantidad = ttk.Entry(frame)
    cantidad.grid(row=2, column=1, pady=5)

    ttk.Label(frame, text="Precio venta:").grid(row=3, column=0, sticky="e", pady=5)
    precio_venta = ttk.Entry(frame)
    precio_venta.grid(row=3, column=1, pady=5)

    def vender():
        try:
            cant = int(cantidad.get())
            seleccion = producto_var.get()
            if not seleccion:
                messagebox.showerror("Error", "Selecciona un producto")
                return
            precio_input = precio_venta.get()
            if not precio_input:
                messagebox.showerror("Error", "Ingresa el precio de venta")
                return
            precio = float(precio_input)
            idx = opciones.index(seleccion)
            prod = productos[idx]
            id_producto = prod[0]  # Usar el ID del producto
            nombre, total, _ = database.registrar_venta(id_producto, cant)
            total = precio * cant if nombre else None
            if total:
                ruta = database.generar_ticket(id_producto, nombre, cant, precio, total)
                messagebox.showinfo(
                    "Venta realizada",
                    f"{nombre} x{cant} = ${total:.2f}\nTicket generado:\n{ruta}",
                )
                win.destroy()
            else:
                messagebox.showerror(
                    "Error",
                    "No se pudo realizar la venta (producto no encontrado o stock insuficiente)",
                )
        except ValueError:
            messagebox.showerror("Error", "Cantidad o precio inválido")

    ttk.Button(frame, text="Vender", command=vender).grid(
        row=4, column=0, columnspan=2, pady=15
    )


def ventana_ventas_dia():
    win = tk.Toplevel()
    win.title("Ventas del día")
    win.geometry("1200x500")

    frame = ttk.Frame(win, padding=10)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="📊 Ventas del día", font=("Segoe UI", 16, "bold")).pack(
        pady=10
    )

    columns = ("ID producto", "Nombre", "Cantidad", "Total")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    total = 0
    ventas = database.ventas_del_dia()
    for v in ventas:
        tree.insert("", "end", values=v)
        total += float(v[3])

    tree.pack(fill="both", expand=True, pady=10)
    ttk.Label(
        frame, text=f"Total vendido hoy: ${total:.2f}", font=("Segoe UI", 12, "bold")
    ).pack(pady=5)


def verificar_actualizacion():
    try:
        with open("input", "r") as f:
            last_update = f.read().strip()
        if last_update == "lastupdateV1.0":
            messagebox.showinfo(
                "Actualización", "La aplicación está actualizada a la última versión."
            )
        else:
            messagebox.showwarning(
                "Actualización disponible",
                "Hay una nueva versión disponible. Por favor, actualiza la aplicación.",
            )
    except FileNotFoundError:
        messagebox.showerror(
            "Error",
            "No se pudo verificar la actualización. Archivo 'input' no encontrado.",
        )
    except Exception as e:
        messagebox.showerror(
            "Error", f"Ocurrió un error al verificar la actualización: {str(e)}"
        )


# ------------------------ Ventana principal ------------------------


def main():

    root = tk.Tk()
    root.title("🛒 Mini Market POS")
    root.geometry("600x500")
    root.configure(bg="white")

    # Centrar ventana
    root.update_idletasks()
    width = 600
    height = 500
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    # Estilo general
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "TButton",
        font=("Segoe UI", 12),
        padding=10,
        background="#007acc",
        foreground="white",
    )
    style.map("TButton", background=[("active", "#005f99")])

    style.configure("TLabel", font=("Segoe UI", 14))
    style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#007acc")

    # Título
    ttk.Label(root, text="Mini Market POS", style="Title.TLabel").pack(pady=20)

    # Botones principales
    # ttk.Button(root, text="➕ Agregar producto", command=ventana_agregar_producto).pack(
    #     pady=6
    # )
    ttk.Button(root, text="📦 Ver productos", command=ventana_ver_productos).pack(
        pady=6
    )
    ttk.Button(root, text="🛒 Registrar compra", command=ventana_registrar_compra).pack(
        pady=6
    )
    ttk.Button(root, text="💰 Registrar venta", command=ventana_registrar_venta).pack(
        pady=6
    )
    ttk.Button(root, text="📊 Ventas del día", command=ventana_ventas_dia).pack(pady=6)
    ttk.Button(
        root, text="🔄 Buscar actualizaciones", command=verificar_actualizacion
    ).pack(pady=6)
    ttk.Button(root, text="❌ Salir", command=root.quit).pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
