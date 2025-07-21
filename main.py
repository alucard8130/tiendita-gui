# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import database
import csv
from tkinter import filedialog
from datetime import datetime, timedelta

# Inicializar base de datos al arrancar
database.inicializar_db()


def abrir_web():
    import webbrowser

    webbrowser.open_new("https://paginaweb-ro9v.onrender.com")


# ------------------------ Ventanas ------------------------


def ventana_ver_productos():
    win = tk.Toplevel()
    win.transient(None)
    win.grab_set()
    win.title("Lista de productos")
    win.geometry("1250x500")

    # Centrar ventana
    win.update_idletasks()
    width = 1250
    height = 500
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

    frame = ttk.Frame(win, padding=10)
    frame.pack(fill="both", expand=True)

    ttk.Label(
        frame, text="📦 Productos disponibles", font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    columns = (
        "ID",
        "Nombre",
        "Marca",
        "Stock ini",
        "Costo",
        "Precio ",
        "Descripción",
        "Stock fin",
        "Código barras",
        "Status",
    )
    style = ttk.Style()
    style.configure("Custom.Treeview", font=("Segoe UI", 12), rowheight=22)
    style.configure("Custom.Treeview.Heading", font=("Segoe UI", 12, "bold"))
    tree = ttk.Treeview(
        frame, columns=columns, show="headings", height=15, style="Custom.Treeview"
    )
    col_widths = [60, 180, 120, 100, 100, 100, 250, 100, 120, 100]
    for i, col in enumerate(columns):
        tree.heading(col, text=col, anchor="center")
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

    # Footer
    footer = ttk.Frame(win)
    footer.pack(side="bottom", fill="x", pady=(15, 0))
    ttk.Label(
        footer,
        text="© 2025 Mini Market POS | Todos los derechos reservados Jaime Martin Estrada Bernabe",
        font=("Segoe UI", 10),
        foreground="#555",
    ).pack(side="left", padx=15)
    web_label = ttk.Label(
        footer,
        text="VISITA NUESTRA WEB PARA MAS PRODUCTOS",
        foreground="#007acc",
        cursor="hand2",
        font=("Segoe UI", 10, "underline"),
    )
    web_label.pack(side="right", padx=15)
    web_label.bind("<Button-1>", lambda e: abrir_web())


def ventana_registrar_venta():
    win = tk.Toplevel()
    win.transient(None)
    win.grab_set()
    win.title("Registrar venta")
    win.geometry("300x500")

    # Centrar ventana
    win.update_idletasks()
    width = 500
    height = 500
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

    frame = ttk.Frame(win, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="💰 Registrar venta", font=("Segoe UI", 12, "bold")).grid(
        row=0, column=0, columnspan=2, pady=10, sticky="ew"
    )

    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)

    ttk.Label(frame, text="Producto:").grid(row=1, column=0, sticky="ew", pady=5)
    productos = database.obtener_productos()
    opciones = [f"{p[1]} (ID:{p[0]})" for p in productos] if productos else []
    producto_var = tk.StringVar()
    producto_combo = ttk.Combobox(
        frame,
        textvariable=producto_var,
        values=opciones,
        state="readonly",
        font=("Segoe UI", 12),
    )
    producto_combo.grid(row=1, column=1, pady=8, ipady=8, sticky="ew")
    producto_combo.configure(font=("Segoe UI", 12))

    ttk.Label(frame, text="Cantidad:").grid(row=2, column=0, sticky="ew", pady=5)
    cantidad = ttk.Entry(frame, font=("Segoe UI", 12))
    cantidad.grid(row=2, column=1, pady=8, ipady=8, sticky="ew")

    ttk.Label(frame, text="Precio venta:").grid(row=3, column=0, sticky="ew", pady=5)
    precio_venta = ttk.Entry(frame, font=("Segoe UI", 12))
    precio_venta.grid(row=3, column=1, pady=8, ipady=8, sticky="ew")

    def vender():
        try:
            seleccion = producto_var.get()
            if not seleccion:
                messagebox.showerror("Error", "Selecciona un producto")
                return
            cantidad_str = cantidad.get().strip()
            precio_input = precio_venta.get().strip()
            if not cantidad_str:
                messagebox.showerror("Error", "Ingresa la cantidad")
                return
            if not precio_input:
                messagebox.showerror("Error", "Ingresa el precio de venta")
                return
            try:
                cant = int(cantidad_str)
                if cant <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Error", "Cantidad inválida. Debe ser un número entero positivo."
                )
                return
            try:
                precio = float(precio_input)
                if precio < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Error", "Precio inválido. Debe ser un número positivo."
                )
                return
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
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(frame, text="Vender", command=vender).grid(
        row=4, column=0, columnspan=2, pady=15
    )

    # Footer
    footer = ttk.Frame(win)
    footer.pack(side="bottom", fill="x", pady=(15, 0))
    ttk.Label(
        footer,
        text="© 2025 Mini Market POS | Todos los derechos reservados Jaime Martin Estrada Bernabe",
        font=("Segoe UI", 10),
        foreground="#555",
    ).pack(side="left", padx=15)
    web_label = ttk.Label(
        footer,
        text="VISITA NUESTRA WEB PARA MAS PRODUCTOS",
        foreground="#007acc",
        cursor="hand2",
        font=("Segoe UI", 10, "underline"),
    )
    web_label.pack(side="right", padx=15)
    web_label.bind("<Button-1>", lambda e: abrir_web())


def ventana_ventas_dia():
    win = tk.Toplevel()
    win.transient(None)
    win.grab_set()
    win.title("Ventas del día")
    win.geometry("1200x650")

    # Centrar ventana
    win.update_idletasks()
    width = 1200
    height = 650
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

    frame = ttk.Frame(win, padding=10)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="📊 Ventas del día", font=("Segoe UI", 16, "bold")).pack(
        pady=10
    )

    # Filtro de fecha
    filtro_frame = ttk.Frame(frame)
    filtro_frame.pack(pady=5)
    ttk.Label(filtro_frame, text="Fecha Ventas:").grid(row=0, column=0, padx=5)
    fecha_entry = ttk.Entry(filtro_frame)
    fecha_entry.grid(row=0, column=1, padx=5)

    columns = ("Fecha", "ID producto", "Nombre", "Cantidad", "Total")
    style = ttk.Style()
    style.configure("Custom.Treeview", font=("Segoe UI", 12), rowheight=20)
    style.configure("Custom.Treeview.Heading", font=("Segoe UI", 12, "bold"))
    tree = ttk.Treeview(
        frame, columns=columns, show="headings", height=15, style="Custom.Treeview"
    )
    for col in columns:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center")

    ventas_actuales = []

    def cargar_ventas():
        fecha = fecha_entry.get().strip()
        if not fecha:
            fecha = datetime.now().strftime("%Y-%m-%d")
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Usa YYYY-MM-DD.")
            return
        for i in tree.get_children():
            tree.delete(i)
        nonlocal ventas_actuales
        ventas_actuales = []
        ventas_raw = database.ventas_del_dia(fecha)
        total = 0
        for v in ventas_raw:
            fila = (fecha,) + v
            ventas_actuales.append(fila)
            tree.insert("", "end", values=fila)
            total += float(v[3])
        total_label.config(text=f"Total vendido: ${total:.2f}")

    ttk.Button(filtro_frame, text="Filtrar", command=cargar_ventas).grid(
        row=0, column=2, padx=10
    )

    tree.pack(fill="both", expand=True, pady=10)
    total_label = ttk.Label(
        frame, text=f"Total vendido: $0.00", font=("Segoe UI", 12, "bold")
    )
    total_label.pack(pady=5)

    def exportar_csv():
        if not ventas_actuales:
            messagebox.showinfo("Sin datos", "No hay datos para exportar.")
            return
        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Guardar reporte como CSV",
        )
        if not archivo:
            return
        with open(archivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Fecha", "ID producto", "Nombre", "Cantidad", "Total"])
            for v in ventas_actuales:
                writer.writerow(v)
        messagebox.showinfo("Exportado", f"Reporte exportado a {archivo}")

    btn_exportar = ttk.Button(frame, text="Descargar Reporte", command=exportar_csv)
    btn_exportar.pack(pady=5)

    # Footer
    footer = ttk.Frame(win)
    footer.pack(side="bottom", fill="x", pady=(15, 0))
    ttk.Label(
        footer,
        text="© 2025 Mini Market POS | Todos los derechos reservados Jaime Martin Estrada Bernabe",
        font=("Segoe UI", 10),
        foreground="#555",
    ).pack(side="left", padx=15)
    web_label = ttk.Label(
        footer,
        text="VISITA NUESTRA WEB PARA MAS PRODUCTOS",
        foreground="#007acc",
        cursor="hand2",
        font=("Segoe UI", 10, "underline"),
    )
    web_label.pack(side="right", padx=15)
    web_label.bind("<Button-1>", lambda e: abrir_web())

    # Inicializar con la fecha de hoy
    fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
    cargar_ventas()


def ventana_registrar_compra():
    win = tk.Toplevel()
    win.transient(None)  # No bloquea el root
    win.grab_set()  # Permite interacción con otras ventanas
    win.title("Registrar compra")
    win.geometry("500x580")

    # Centrar ventana
    win.update_idletasks()
    width = 850
    height = 660
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

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
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    for i, (label, key) in enumerate(campos):
        ttk.Label(frame, text=label + ":").grid(row=i, column=0, sticky="ew", pady=8)
        ent = ttk.Entry(frame, font=("Segoe UI", 12))
        ent.grid(row=i, column=1, pady=8, ipady=8, sticky="ew")
        entradas[key] = ent

    def guardar():
        try:
            nombre = entradas["nombre"].get().strip()
            descripcion = entradas["descripcion"].get().strip()
            marca = entradas["marca"].get().strip() or None
            cantidad_str = entradas["cantidad"].get().strip()
            costo_str = entradas["costo"].get().strip()
            precio_str = entradas["precio"].get().strip()
            codigo = entradas["codigo"].get().strip() or None
            proveedor = entradas["proveedor"].get().strip() or None

            if not nombre:
                messagebox.showerror("Error", "Debes ingresar el nombre del producto.")
                return
            if not cantidad_str:
                messagebox.showerror("Error", "Debes ingresar la cantidad.")
                return
            if not costo_str:
                messagebox.showerror("Error", "Debes ingresar el costo.")
                return
            try:
                cantidad = int(cantidad_str)
                if cantidad <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Error", "Cantidad inválida. Debe ser un número entero positivo."
                )
                return
            try:
                costo = float(costo_str)
                if costo < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Error", "Costo inválido. Debe ser un número positivo."
                )
                return
            precio = None
            if precio_str:
                try:
                    precio = float(precio_str)
                    if precio < 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror(
                        "Error", "Precio inválido. Debe ser un número positivo."
                    )
                    return
            database.registrar_compra(
                nombre,
                descripcion,
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

    # Footer
    footer = ttk.Frame(win)
    footer.pack(side="bottom", fill="x", pady=(15, 0))
    ttk.Label(
        footer,
        text="© 2025 Mini Market POS | Todos los derechos reservados Jaime Martin Estrada Bernabe",
        font=("Segoe UI", 10),
        foreground="#555",
    ).pack(side="left", padx=15)
    web_label = ttk.Label(
        footer,
        text="VISITA NUESTRA WEB PARA MAS PRODUCTOS",
        foreground="#007acc",
        cursor="hand2",
        font=("Segoe UI", 10, "underline"),
    )
    web_label.pack(side="right", padx=15)
    web_label.bind("<Button-1>", lambda e: abrir_web())


# ------------------------ Reporte ventas semanal ------------------------


def ventana_reporte_semanal():
    win = tk.Toplevel()
    win.title("Reporte ventas por periodos")
    win.geometry("1200x650")
    win.transient(None)
    win.grab_set()

    # Centrar ventana
    win.update_idletasks()
    width = 1200
    height = 650
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

    frame = ttk.Frame(win, padding=10)
    frame.pack(fill="both", expand=True)

    ttk.Label(
        frame, text="📅 Reporte de ventas por periodos", font=("Segoe UI", 16, "bold")
    ).pack(pady=10)

    # Selección de fechas
    fechas_frame = ttk.Frame(frame)
    fechas_frame.pack(pady=10)
    ttk.Label(fechas_frame, text="Fecha inicio (YYYY-MM-DD):").grid(
        row=0, column=0, padx=5
    )
    fecha_inicio_entry = ttk.Entry(fechas_frame)
    fecha_inicio_entry.grid(row=0, column=1, padx=5)
    ttk.Label(fechas_frame, text="Fecha fin (YYYY-MM-DD):").grid(
        row=0, column=2, padx=5
    )
    fecha_fin_entry = ttk.Entry(fechas_frame)
    fecha_fin_entry.grid(row=0, column=3, padx=5)

    def cargar_reporte():
        fecha_inicio = fecha_inicio_entry.get().strip()
        fecha_fin = fecha_fin_entry.get().strip()
        try:
            datetime.strptime(fecha_inicio, "%Y-%m-%d")
            datetime.strptime(fecha_fin, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Usa YYYY-MM-DD.")
            return
        nonlocal ventas_actuales
        ventas_actuales = database.ventas_por_semana(fecha_inicio, fecha_fin)
        for i in tree.get_children():
            tree.delete(i)
        total = 0
        for v in ventas_actuales:
            tree.insert("", "end", values=v)
            total += float(v[4])
        total_label.config(text=f"Total vendido en el periodo: ${total:.2f}")

    def exportar_csv():
        if not ventas_actuales:
            messagebox.showinfo("Sin datos", "No hay datos para exportar.")
            return
        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Guardar reporte como CSV",
        )
        if not archivo:
            return
        with open(archivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Fecha", "ID producto", "Nombre", "Cantidad", "Total"])
            for v in ventas_actuales:
                writer.writerow(v)
        messagebox.showinfo("Exportado", f"Reporte exportado a {archivo}")

    ttk.Button(fechas_frame, text="Filtrar", command=cargar_reporte).grid(
        row=0, column=4, padx=10
    )

    columns = ("Fecha", "ID producto", "Nombre", "Cantidad", "Total")
    style = ttk.Style()
    style.configure("Custom.Treeview", font=("Segoe UI", 12), rowheight=20)
    style.configure("Custom.Treeview.Heading", font=("Segoe UI", 12, "bold"))
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=15, style="Custom.Treeview")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")
    tree.pack(fill="both", expand=True, pady=10)

    total_label = ttk.Label(
        frame, text="Total vendido en el periodo: $0.00", font=("Segoe UI", 12, "bold")
    )
    total_label.pack(pady=5)

    # Botón exportar CSV
    btn_exportar = ttk.Button(frame, text="Descargar Reporte", command=exportar_csv)
    btn_exportar.pack(pady=5)

    # Footer
    footer = ttk.Frame(win)
    footer.pack(side="bottom", fill="x", pady=(15, 0))
    ttk.Label(
        footer,
        text="© 2025 Mini Market POS | Todos los derechos reservados Jaime Martin Estrada Bernabe",
        font=("Segoe UI", 10),
        foreground="#555",
    ).pack(side="left", padx=15)
    web_label = ttk.Label(
        footer,
        text="VISITA NUESTRA WEB PARA MAS PRODUCTOS",
        foreground="#007acc",
        cursor="hand2",
        font=("Segoe UI", 10, "underline"),
    )
    web_label.pack(side="right", padx=15)
    web_label.bind("<Button-1>", lambda e: abrir_web())

    # Variable para almacenar los datos actuales
    ventas_actuales = []

    # Por defecto, mostrar la semana actual
    hoy = datetime.now()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    fecha_inicio_entry.insert(0, inicio_semana.strftime("%Y-%m-%d"))
    fecha_fin_entry.insert(0, fin_semana.strftime("%Y-%m-%d"))
    cargar_reporte()


# ---------------------# Función principal para iniciar la aplicación


def main():
    def abrir_web():
        import webbrowser

        webbrowser.open_new("https://paginaweb-ro9v.onrender.com")

    root = tk.Tk()
    root.title("🛒 Mini Market POS")
    root.geometry("900x560")
    root.configure(bg="white")

    # Centrar ventana y deshabilitar movimiento
    root.update_idletasks()
    width = 900
    height = 560
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.resizable(False, False)

    def disable_event():
        pass

    root.protocol("WM_MOVING", disable_event)

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

    # Footer moderno con copyright y web
    def abrir_web():
        import webbrowser

        webbrowser.open_new(
            "https://paginaweb-ro9v.onrender.com"
        )  # Cambia por tu URL real

    footer = ttk.Frame(root)
    footer.pack(side="bottom", fill="x", pady=(15, 0))

    copyright_label = ttk.Label(
        footer,
        text="© 2025 Mini Market POS | Todos los derechos reservados Jaime Martin Estrada Bernabe",
        font=("Segoe UI", 10),
        foreground="#555",
    )
    copyright_label.pack(side="left", padx=15)

    web_label = ttk.Label(
        footer,
        text="VISITA NUESTRA WEB PARA MAS PRODUCTOS",
        foreground="#007acc",
        cursor="hand2",
        font=("Segoe UI", 10, "underline"),
    )
    web_label.pack(side="right", padx=15)
    web_label.bind("<Button-1>", lambda e: abrir_web())

    # Botones principales
    ttk.Button(root, text="📦 Ver Inventario", command=ventana_ver_productos).pack(
        pady=6
    )
    ttk.Button(
        root, text="🛒 Registrar compra de mercancías", command=ventana_registrar_compra
    ).pack(pady=6)
    ttk.Button(
        root, text="💰 Registrar venta diaria", command=ventana_registrar_venta
    ).pack(pady=6)
    ttk.Button(root, text="📊 Reporte ventas diarias", command=ventana_ventas_dia).pack(
        pady=6
    )
    ttk.Button(
        root, text="📅 Reporte ventas por periodos", command=ventana_reporte_semanal
    ).pack(pady=6)

    def abrir_actualizacion_web():
        import webbrowser

        webbrowser.open_new("https://paginaweb-ro9v.onrender.com")

    ttk.Button(
        root, text="🔄 Buscar actualizaciones", command=abrir_actualizacion_web
    ).pack(pady=6)

    ttk.Button(root, text="❌ Salir", command=root.quit).pack(pady=20)

    def ventana_donativos():
        win = tk.Toplevel(root)
        win.title("Donativos por PayPal")
        win.geometry("400x180")
        win.resizable(False, False)
        win.transient(root)
        win.grab_set()

        win.update_idletasks()
        width = 400
        height = 200
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

        frame = ttk.Frame(win, padding=30)
        frame.pack(fill="both", expand=True)
        ttk.Label(
            frame,
            text="¡Gracias por apoyar el proyecto!",
            font=("Segoe UI", 14, "bold"),
            foreground="#007acc",
        ).pack(pady=10)
        ttk.Label(
            frame,
            text="Puedes donar por PayPal usando el siguiente enlace:",
            font=("Segoe UI", 11),
        ).pack(pady=5)

        def abrir_paypal():
            import webbrowser

            webbrowser.open_new(
                "https://paypal.me/mareb?country.x=MX&locale.x=es_XC"
            )  # Cambia TU_ID_PAYPAL por tu ID real

        link = ttk.Label(
            frame,
            text="Donar por PayPal",
            foreground="#007acc",
            cursor="hand2",
            font=("Segoe UI", 11, "underline"),
        )
        link.pack(pady=10)
        link.bind("<Button-1>", lambda e: abrir_paypal())

    style.configure(
        "Donar.TButton",
        font=("Segoe UI", 12, "bold"),
        padding=10,
        background="#FFD700",
        foreground="#005f99",
        borderwidth=2,
        relief="raised",
    )
    style.map(
        "Donar.TButton",
        background=[("active", "#FFB800")],
        foreground=[("active", "#007acc")],
    )
    ttk.Button(
        root,
        text="💙 Donar por PayPal",
        command=ventana_donativos,
        style="Donar.TButton",
    ).pack(pady=6)

    root.mainloop()


if __name__ == "__main__":
    main()
