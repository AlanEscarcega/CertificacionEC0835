import os
import shutil
import sqlite3

NOMBRE_BD = "biblioteca.db"
RESPALDO_BD = "biblioteca_respaldo.db"

# ====================
#  Conexion a la base de datos
# ====================


def get_connection():
    con = sqlite3.connect(NOMBRE_BD)
    con.execute("PRAGMA foreign_keys = ON")
    return con


# ====================
#  Esquema
# ====================
# - Los IDs los escribe el usuario (sin AUTOINCREMENT), asi que un ID
#   eliminado puede volver a usarse.
# - nombre, email y titulo son UNIQUE sin distinguir mayusculas/minusculas.
# - Si se elimina un usuario, sus libros quedan sin prestar (usuario_id = NULL).
SQL_USUARIOS = """
CREATE TABLE IF NOT EXISTS Usuarios (
    id_usuario INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE COLLATE NOCASE,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE
)
"""

SQL_LIBROS = """
CREATE TABLE IF NOT EXISTS Libros (
    id_libro INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL UNIQUE COLLATE NOCASE,
    autor TEXT NOT NULL,
    usuario_id INTEGER,
    FOREIGN KEY(usuario_id) REFERENCES Usuarios(id_usuario) ON DELETE SET NULL
)
"""


def _esquema_viejo():
    # True si ya existe una base creada con el esquema anterior
    if not os.path.exists(NOMBRE_BD):
        return False
    con = sqlite3.connect(NOMBRE_BD)
    try:
        fila = con.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='Libros'"
        ).fetchone()
    finally:
        con.close()
    return fila is not None and "ON DELETE SET NULL" not in fila[0]


def _migrar():
    # Respaldo antes de tocar nada
    shutil.copy2(NOMBRE_BD, RESPALDO_BD)

    con = sqlite3.connect(NOMBRE_BD)
    con.execute("PRAGMA foreign_keys = OFF")
    cur = con.cursor()
    cur.execute("ALTER TABLE Libros RENAME TO Libros_old")
    cur.execute("ALTER TABLE Usuarios RENAME TO Usuarios_old")
    cur.execute(SQL_USUARIOS)
    cur.execute(SQL_LIBROS)

    total_u = cur.execute("SELECT COUNT(*) FROM Usuarios_old").fetchone()[0]
    total_l = cur.execute("SELECT COUNT(*) FROM Libros_old").fetchone()[0]

    # OR IGNORE: si habia nombres, emails o titulos repetidos, se conserva el primero
    cur.execute("""
        INSERT OR IGNORE INTO Usuarios (id_usuario, nombre, email)
        SELECT id_usuario, TRIM(nombre), TRIM(email)
        FROM Usuarios_old ORDER BY id_usuario
    """)
    cur.execute("""
        INSERT OR IGNORE INTO Libros (id_libro, titulo, autor, usuario_id)
        SELECT id_libro, TRIM(titulo), TRIM(autor),
               CASE WHEN usuario_id IN (SELECT id_usuario FROM Usuarios)
                    THEN usuario_id ELSE NULL END
        FROM Libros_old ORDER BY id_libro
    """)

    nuevos_u = cur.execute("SELECT COUNT(*) FROM Usuarios").fetchone()[0]
    nuevos_l = cur.execute("SELECT COUNT(*) FROM Libros").fetchone()[0]

    cur.execute("DROP TABLE Libros_old")
    cur.execute("DROP TABLE Usuarios_old")
    con.commit()
    con.close()

    omitidos = (total_u - nuevos_u) + (total_l - nuevos_l)
    print(f"Base de datos actualizada. Respaldo guardado en {RESPALDO_BD}.")
    if omitidos:
        print(f"Se omitieron {omitidos} registros por tener datos repetidos.")


# ====================
#  Creacion de tablas
# ====================
def init_db():
    if _esquema_viejo():
        _migrar()

    con = get_connection()
    cur = con.cursor()
    cur.execute(SQL_USUARIOS)
    cur.execute(SQL_LIBROS)
    con.commit()
    con.close()
