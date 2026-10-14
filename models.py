# ====================
#  Clases del sistema
# ====================


class Usuario:
    def __init__(self, id_usuario, nombre, email):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email


class Libro:
    def __init__(self, id_libro, titulo, autor, usuario_id):
        self.id_libro = id_libro
        self.titulo = titulo
        self.autor = autor
        self.usuario_id = usuario_id
