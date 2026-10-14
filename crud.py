import sqlite3
from contextlib import contextmanager

from db import get_connection


class ErrorValidacion(ValueError):
    """Error con un mensaje listo para mostrarle al usuario."""


@contextmanager
def conexion():
    con = get_connection()
    try:
        yield con.cursor()
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def validar_id(texto, etiqueta="ID"):
    # Obligatorio, solo numeros, maximo 5 digitos
    texto = str(texto).strip()
    if texto == "":
        raise ErrorValidacion(f"El {etiqueta} es obligatorio.")
    if not (texto.isascii() and texto.isdigit()):
        raise ErrorValidacion(f"El {etiqueta} solo puede contener números.")
    if len(texto) > 5:
        raise ErrorValidacion(f"El {etiqueta} puede tener máximo 5 dígitos.")
    return int(texto)


def _existe(cur, sql, params):
    return cur.execute(sql, params).fetchone() is not None


# ========================
# USUARIOS
# ========================


def registrar_usuario(usuario):
    try:
        with conexion() as cur:
            if _existe(
                cur,
                "SELECT 1 FROM Usuarios WHERE id_usuario=?",
                (usuario.id_usuario,),
            ):
                raise ErrorValidacion("Ya existe un usuario con ese ID.")
            if _existe(cur, "SELECT 1 FROM Usuarios WHERE nombre=?", (usuario.nombre,)):
                raise ErrorValidacion("Ya existe un usuario con ese nombre.")
            if _existe(cur, "SELECT 1 FROM Usuarios WHERE email=?", (usuario.email,)):
                raise ErrorValidacion("Ya existe un usuario con ese email.")
            cur.execute(
                "INSERT INTO Usuarios (id_usuario, nombre, email) VALUES (?, ?, ?)",
                (usuario.id_usuario, usuario.nombre, usuario.email),
            )
    except sqlite3.IntegrityError:
        raise ErrorValidacion("Hay datos repetidos (ID, nombre o email).")


def editar_usuario(id_usuario, nombre, email):
    try:
        with conexion() as cur:
            if not _existe(
                cur, "SELECT 1 FROM Usuarios WHERE id_usuario=?", (id_usuario,)
            ):
                raise ErrorValidacion("No existe un usuario con ese ID.")
            if _existe(
                cur,
                "SELECT 1 FROM Usuarios WHERE nombre=? AND id_usuario<>?",
                (nombre, id_usuario),
            ):
                raise ErrorValidacion("Ya existe otro usuario con ese nombre.")
            if _existe(
                cur,
                "SELECT 1 FROM Usuarios WHERE email=? AND id_usuario<>?",
                (email, id_usuario),
            ):
                raise ErrorValidacion("Ya existe otro usuario con ese email.")
            cur.execute(
                "UPDATE Usuarios SET nombre=?, email=? WHERE id_usuario=?",
                (nombre, email, id_usuario),
            )
    except sqlite3.IntegrityError:
        raise ErrorValidacion("Hay datos repetidos (nombre o email).")


def eliminar_usuario(id_usuario):
    # Solo se elimina el usuario; sus libros siguen existiendo y quedan
    # sin prestar (ON DELETE SET NULL en la base de datos).
    with conexion() as cur:
        if not _existe(cur, "SELECT 1 FROM Usuarios WHERE id_usuario=?", (id_usuario,)):
            raise ErrorValidacion("No existe un usuario con ese ID.")
        cur.execute("DELETE FROM Usuarios WHERE id_usuario=?", (id_usuario,))


def obtener_usuarios():
    with conexion() as cur:
        cur.execute(
            "SELECT id_usuario, nombre, email FROM Usuarios ORDER BY id_usuario"
        )
        return cur.fetchall()


# =======================
# LIBROS
# =======================
def registrar_libro(libro):
    # Al registrar, el usuario es obligatorio y debe existir
    if libro.usuario_id is None:
        raise ErrorValidacion("El ID del usuario es obligatorio.")
    try:
        with conexion() as cur:
            if _existe(cur, "SELECT 1 FROM Libros WHERE id_libro=?", (libro.id_libro,)):
                raise ErrorValidacion("Ya existe un libro con ese ID.")
            if _existe(cur, "SELECT 1 FROM Libros WHERE titulo=?", (libro.titulo,)):
                raise ErrorValidacion("Ya existe un libro con ese título.")
            if not _existe(
                cur,
                "SELECT 1 FROM Usuarios WHERE id_usuario=?",
                (libro.usuario_id,),
            ):
                raise ErrorValidacion("El ID de usuario no existe.")
            cur.execute(
                "INSERT INTO Libros (id_libro, titulo, autor, usuario_id) "
                "VALUES (?, ?, ?, ?)",
                (libro.id_libro, libro.titulo, libro.autor, libro.usuario_id),
            )
    except sqlite3.IntegrityError:
        raise ErrorValidacion("Hay datos repetidos (ID o título).")


def editar_libro(id_libro, titulo, autor, usuario_id):
    # usuario_id puede ser None: el libro queda sin prestar ("Ninguno")
    try:
        with conexion() as cur:
            if not _existe(cur, "SELECT 1 FROM Libros WHERE id_libro=?", (id_libro,)):
                raise ErrorValidacion("No existe un libro con ese ID.")
            if _existe(
                cur,
                "SELECT 1 FROM Libros WHERE titulo=? AND id_libro<>?",
                (titulo, id_libro),
            ):
                raise ErrorValidacion("Ya existe otro libro con ese título.")
            if usuario_id is not None and not _existe(
                cur, "SELECT 1 FROM Usuarios WHERE id_usuario=?", (usuario_id,)
            ):
                raise ErrorValidacion("El ID de usuario no existe.")
            cur.execute(
                "UPDATE Libros SET titulo=?, autor=?, usuario_id=? WHERE id_libro=?",
                (titulo, autor, usuario_id, id_libro),
            )
    except sqlite3.IntegrityError:
        raise ErrorValidacion("Hay datos repetidos (título).")


def eliminar_libro(id_libro):
    with conexion() as cur:
        if not _existe(cur, "SELECT 1 FROM Libros WHERE id_libro=?", (id_libro,)):
            raise ErrorValidacion("No existe un libro con ese ID.")
        cur.execute("DELETE FROM Libros WHERE id_libro=?", (id_libro,))


def obtener_libros():
    with conexion() as cur:
        cur.execute(
            "SELECT id_libro, titulo, autor, usuario_id FROM Libros ORDER BY id_libro"
        )
        return cur.fetchall()


# =======================
# FILTRO Y RESUMEN
# =======================


def filtrar_libros_por_usuario(usuario_id):
    with conexion() as cur:
        cur.execute(
            "SELECT id_libro, titulo, autor, usuario_id FROM Libros "
            "WHERE usuario_id=? ORDER BY id_libro",
            (usuario_id,),
        )
        return cur.fetchall()


def resumen_por_usuario():
    with conexion() as cur:
        cur.execute("""
            SELECT Usuarios.nombre, COUNT(Libros.id_libro)
            FROM Usuarios
            LEFT JOIN Libros ON Libros.usuario_id = Usuarios.id_usuario
            GROUP BY Usuarios.id_usuario
            ORDER BY Usuarios.id_usuario
        """)
        return cur.fetchall()
