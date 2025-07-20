# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import database

# Inicializar base de datos al arrancar
database.inicializar_db()

# ------------------------ Ventanas ------------------------

def ventana_agregar_producto():
    win = tk.Toplevel()
    win.title("Agregar producto")

    tk.Label(win, text="Código:").grid(row=0, column=0)
    tk.Label(win, text="Nombre:").grid(row=1, column=0)
    tk.Label(win, text="Precio:").grid(row=2, column=0)
    tk.Label(win, text="Stock:").grid(row=3, column=0)

    codigo = tk.Entry(win)
    nombre = tk.Entry(win)
    precio = tk.Entry(win)
    stock = tk.Entry(win)

    codigo.grid(row=0, column=1)
    nombre.grid(row=1, column=1)
    precio.grid(row=2, column=1)
    stock.grid(row=3, column=1)

    def guardar():
        try:
            database.agregar_producto(
                codigo.get(),
                nombre.get(),
                float(precio.get()),
                int(stock.get())
            )
            messagebox.showinfo("Éxito", "Producto guardado correctamente")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(win, text="Guardar", command=guardar).grid(row=4, column=0, columnspan=2)

def ventana_ver_productos():
    win = tk.Toplevel()
    win.title("Lista de productos")

    tree = ttk.Treeview(win, columns=("Código", "Nombre", "Precio", "Stock"), show='headings')
    tree.heading("Código", text="Código")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Precio", text="Precio")
    tree.heading("Stock", text="Stock")

    for prod in database.obtener_productos():
        tree.insert("", "end", values=(prod[1], prod[2], prod[3], prod[4]))

    tree.pack()

def ventana_registrar_venta():
    win = tk.Toplevel()
    win.title("Registrar venta")

    tk.Label(win, text="Código de producto:").grid(row=0, column=0)
    tk.Label(win, text="Cantidad:").grid(row=1, column=0)

    codigo = tk.Entry(win)
    cantidad = tk.Entry(win)

    codigo.grid(row=0, column=1)
    cantidad.grid(row=1, column=1)

    def vender():
        try:
            cant = int(cantidad.get())
            nombre, total, precio_unitario = database.registrar_venta(codigo.get(), cant)
            if total:
                ruta = database.generar_ticket(codigo.get(), nombre, cant, precio_unitario, total)
                messagebox.showinfo("Venta realizada", f"{nombre} x{cant} = ${total:.2f}\nTicket: {ruta}")
                win.destroy()
            else:
                messagebox.showerror("Error", "No se pudo realizar la venta (producto no encontrado o stock insuficiente)")
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida")


    tk.Button(win, text="Vender", command=vender).grid(row=2, column=0, columnspan=2)

def ventana_ventas_dia():
    win = tk.Toplevel()
    win.title("Ventas del día")

    tree = ttk.Treeview(win, columns=("Código", "Nombre", "Cantidad", "Total"), show='headings')
    for col in ("Código", "Nombre", "Cantidad", "Total"):
        tree.heading(col, text=col)

    total = 0
    for v in database.ventas_del_dia():
        tree.insert("", "end", values=v)
        total += float(v[3])

    tree.pack()
    tk.Label(win, text=f"Total vendido hoy: ${total:.2f}").pack()

# ------------------------ Ventana principal ------------------------

def main():
    root = tk.Tk()
    root.title("Mini Market POS")

    tk.Button(root, text="➕ Agregar producto", width=30, command=ventana_agregar_producto).pack(pady=5)
    tk.Button(root, text="📦 Ver productos", width=30, command=ventana_ver_productos).pack(pady=5)
    tk.Button(root, text="💰 Registrar venta", width=30, command=ventana_registrar_venta).pack(pady=5)
    tk.Button(root, text="📊 Ventas del día", width=30, command=ventana_ventas_dia).pack(pady=5)
    tk.Button(root, text="Salir", width=30, command=root.quit).pack(pady=10)

    root.mainloop()

if __name__ == '__main__':
    main()
