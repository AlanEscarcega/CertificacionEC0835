import tkinter as tk
from tkinter import ttk, messagebox

from db import init_db
from models import Usuario, Libro
from crud import (
    ErrorValidacion,
    validar_id,
    registrar_usuario,
    editar_usuario,
    eliminar_usuario,
    obtener_usuarios,
    registrar_libro,
    editar_libro,
    eliminar_libro,
    obtener_libros,
    filtrar_libros_por_usuario,
    resumen_por_usuario,
)

# Inicializar base (si es de una version anterior, la actualiza)
init_db()


###############################
# Funciones auxiliares
###############################
def limpiar_campos():
    for entrada in (
        entry_id_usuario,
        entry_nombre,
        entry_email,
        entry_id_libro,
        entry_titulo,
        entry_autor,
        entry_usuario_id,
    ):
        entrada.delete(0, tk.END)


def aviso(error):
    messagebox.showwarning("Aviso", str(error))


def mostrar_tabla(columnas, filas):
    # Limpia la tabla y la vuelve a llenar con las columnas y filas recibidas
    tabla.delete(*tabla.get_children())
    tabla["columns"] = columnas
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=130, anchor="center")
    for fila in filas:
        tabla.insert("", tk.END, values=fila)


def mostrar_usuarios_gui():
    mostrar_tabla(("ID", "Nombre", "Email"), obtener_usuarios())


def mostrar_libros_gui(registros=None):
    if registros is None:
        registros = obtener_libros()
    filas = []
    for r in registros:
        usuario = r[3] if r[3] is not None else "Ninguno"
        filas.append((r[0], r[1], r[2], usuario))
    mostrar_tabla(("ID", "Título", "Autor", "ID Usuario"), filas)


def leer_usuario_id_opcional():
    # None si el campo está vacío; si no, lo valida como ID
    if entry_usuario_id.get().strip() == "":
        return None
    return validar_id(entry_usuario_id.get(), "ID del usuario")


###############################
# Eventos de usuarios
###############################
def registrar_usuario_gui():
    try:
        id_usuario = validar_id(entry_id_usuario.get(), "ID")
        nombre = entry_nombre.get().strip()
        email = entry_email.get().strip()
        if not nombre or not email:
            raise ErrorValidacion("Escribe nombre y email.")
        registrar_usuario(Usuario(id_usuario, nombre, email))
    except ErrorValidacion as e:
        aviso(e)
        return
    limpiar_campos()
    mostrar_usuarios_gui()


def editar_usuario_gui():
    try:
        id_usuario = validar_id(entry_id_usuario.get(), "ID")
        nombre = entry_nombre.get().strip()
        email = entry_email.get().strip()
        if not nombre or not email:
            raise ErrorValidacion("Escribe el nombre y el email.")
        editar_usuario(id_usuario, nombre, email)
    except ErrorValidacion as e:
        aviso(e)
        return
    limpiar_campos()
    mostrar_usuarios_gui()


def eliminar_usuario_gui():
    try:
        id_usuario = validar_id(entry_id_usuario.get(), "ID")
        if not messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar al usuario {id_usuario}?\n"
            "Sus libros no se borran: quedarán sin prestar.",
        ):
            return
        eliminar_usuario(id_usuario)
    except ErrorValidacion as e:
        aviso(e)
        return
    limpiar_campos()
    mostrar_usuarios_gui()


###############################
# Eventos de libros
###############################
def registrar_libro_gui():
    try:
        id_libro = validar_id(entry_id_libro.get(), "ID del libro")
        titulo = entry_titulo.get().strip()
        autor = entry_autor.get().strip()
        if not titulo or not autor:
            raise ErrorValidacion("Escribe título y autor.")
        # Obligatorio al registrar
        usuario_id = validar_id(entry_usuario_id.get(), "ID del usuario")
        registrar_libro(Libro(id_libro, titulo, autor, usuario_id))
    except ErrorValidacion as e:
        aviso(e)
        return
    limpiar_campos()
    mostrar_libros_gui()


def editar_libro_gui():
    try:
        id_libro = validar_id(entry_id_libro.get(), "ID del libro")
        titulo = entry_titulo.get().strip()
        autor = entry_autor.get().strip()
        if not titulo or not autor:
            raise ErrorValidacion("Escribe título y autor.")
        # Vacío = libro sin prestar ("Ninguno")
        usuario_id = leer_usuario_id_opcional()
        editar_libro(id_libro, titulo, autor, usuario_id)
    except ErrorValidacion as e:
        aviso(e)
        return
    limpiar_campos()
    mostrar_libros_gui()


def eliminar_libro_gui():
    try:
        id_libro = validar_id(entry_id_libro.get(), "ID del libro")
        eliminar_libro(id_libro)
    except ErrorValidacion as e:
        aviso(e)
        return
    limpiar_campos()
    mostrar_libros_gui()


def filtrar_libros_gui():
    try:
        usuario_id = validar_id(entry_usuario_id.get(), "ID del usuario")
    except ErrorValidacion as e:
        aviso(e)
        return
    mostrar_libros_gui(filtrar_libros_por_usuario(usuario_id))


def resumen_gui():
    mostrar_tabla(("Usuario", "Total de libros"), resumen_por_usuario())


###############################
# Ventana principal
###############################
ventana = tk.Tk()
ventana.title("Sistema de Biblioteca")
ventana.geometry("860x620")
ventana.configure(bg="#f4f1ea")

estilo = ttk.Style()
estilo.theme_use("clam")
estilo.configure("TNotebook", background="#f4f1ea")
estilo.configure("TFrame", background="#ffffff")
estilo.configure("TLabel", background="#ffffff", font=("Segoe UI", 10))
estilo.configure("TButton", font=("Segoe UI", 10), padding=6)
estilo.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))


# Los campos de ID solo aceptan números y máximo 5 dígitos (también al pegar)
def _solo_id(valor):
    return valor == "" or (valor.isascii() and valor.isdigit() and len(valor) <= 5)


vcmd_id = (ventana.register(_solo_id), "%P")

# ---- Encabezado ----
encabezado = tk.Label(
    ventana,
    text="Sistema de Biblioteca",
    font=("Segoe UI", 20, "bold"),
    bg="#6b4226",
    fg="white",
    pady=14,
)
encabezado.pack(fill="x")

# ---- Pestañas ----
pestanas = ttk.Notebook(ventana)
pestanas.pack(fill="x", padx=15, pady=15)

tab_usuarios = ttk.Frame(pestanas, padding=15)
tab_libros = ttk.Frame(pestanas, padding=15)
pestanas.add(tab_usuarios, text="  Usuarios  ")
pestanas.add(tab_libros, text="  Libros  ")

###############################
# Pestaña Usuarios
###############################
ttk.Label(tab_usuarios, text="ID").grid(row=0, column=0, sticky="w", padx=5)
ttk.Label(tab_usuarios, text="Nombre").grid(row=0, column=1, sticky="w", padx=5)
ttk.Label(tab_usuarios, text="Email").grid(row=0, column=2, sticky="w", padx=5)

entry_id_usuario = ttk.Entry(
    tab_usuarios, width=10, validate="key", validatecommand=vcmd_id
)
entry_id_usuario.grid(row=1, column=0, padx=5, pady=5)
entry_nombre = ttk.Entry(tab_usuarios, width=25)
entry_nombre.grid(row=1, column=1, padx=5, pady=5)
entry_email = ttk.Entry(tab_usuarios, width=30)
entry_email.grid(row=1, column=2, padx=5, pady=5)

ttk.Button(tab_usuarios, text="Registrar", command=registrar_usuario_gui).grid(
    row=2, column=0, pady=10, padx=5
)
ttk.Button(tab_usuarios, text="Editar", command=editar_usuario_gui).grid(
    row=2, column=1, pady=10, padx=5
)
ttk.Button(tab_usuarios, text="Eliminar", command=eliminar_usuario_gui).grid(
    row=2, column=2, pady=10, padx=5
)
ttk.Button(tab_usuarios, text="Mostrar todos", command=mostrar_usuarios_gui).grid(
    row=2, column=3, pady=10, padx=5
)

###############################
# Pestaña Libros
###############################
ttk.Label(tab_libros, text="ID Libro").grid(row=0, column=0, sticky="w", padx=5)
ttk.Label(tab_libros, text="Título").grid(row=0, column=1, sticky="w", padx=5)
ttk.Label(tab_libros, text="Autor").grid(row=0, column=2, sticky="w", padx=5)
ttk.Label(tab_libros, text="ID Usuario").grid(row=0, column=3, sticky="w", padx=5)

entry_id_libro = ttk.Entry(tab_libros, width=8, validate="key", validatecommand=vcmd_id)
entry_id_libro.grid(row=1, column=0, padx=5, pady=5)
entry_titulo = ttk.Entry(tab_libros, width=22)
entry_titulo.grid(row=1, column=1, padx=5, pady=5)
entry_autor = ttk.Entry(tab_libros, width=18)
entry_autor.grid(row=1, column=2, padx=5, pady=5)
entry_usuario_id = ttk.Entry(
    tab_libros, width=10, validate="key", validatecommand=vcmd_id
)
entry_usuario_id.grid(row=1, column=3, padx=5, pady=5)

ttk.Button(tab_libros, text="Registrar", command=registrar_libro_gui).grid(
    row=2, column=0, pady=10, padx=3
)
ttk.Button(tab_libros, text="Editar", command=editar_libro_gui).grid(
    row=2, column=1, pady=10, padx=3
)
ttk.Button(tab_libros, text="Eliminar", command=eliminar_libro_gui).grid(
    row=2, column=2, pady=10, padx=3
)
ttk.Button(tab_libros, text="Mostrar todos", command=mostrar_libros_gui).grid(
    row=2, column=3, pady=10, padx=3
)
ttk.Button(tab_libros, text="Filtrar por usuario", command=filtrar_libros_gui).grid(
    row=2, column=4, pady=10, padx=3
)
ttk.Button(tab_libros, text="Resumen", command=resumen_gui).grid(
    row=2, column=5, pady=10, padx=3
)

###############################
# Tabla de resultados
###############################
frame_tabla = ttk.LabelFrame(ventana, text="Resultados", padding=10)
frame_tabla.pack(fill="both", expand=True, padx=15, pady=(0, 15))

tabla = ttk.Treeview(frame_tabla, show="headings", height=10)
barra = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
tabla.configure(yscrollcommand=barra.set)
tabla.pack(side="left", fill="both", expand=True)
barra.pack(side="right", fill="y")

ventana.mainloop()
