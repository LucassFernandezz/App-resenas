class Juego:
    def __init__(self, id_juego, nombre, descripcion="", puntuacion_media=0.0, total_reseñas=0, puntuacion_acumulada=0):
        self.id_juego = id_juego
        self.nombre = nombre
        self.descripcion = descripcion
        self.puntuacion_media = puntuacion_media
        self.total_reseñas = total_reseñas
        self.puntuacion_acumulada = puntuacion_acumulada

    def __str__(self):
        return (f"Juego(ID: {self.id_juego}, Nombre: '{self.nombre}', Media: {self.puntuacion_media:.2f}, "
                f"Reseñas: {self.total_reseñas}, Acumulado: {self.puntuacion_acumulada})")

    def __repr__(self):
        return self.__str__()

class Usuario:
    def __init__(self, id_usuario, nombre_usuario, tipo_usuario):
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.tipo_usuario = tipo_usuario #critico o usuario_normal

    def __str__(self):
        return f"Usuario(ID: {self.id_usuario}, Nombre: '{self.nombre_usuario}', Tipo: '{self.tipo_usuario}')"

    def __repr__(self):
        return self.__str__()

class Reseña:
    def __init__(self, id_reseña, id_juego, id_usuario, puntuacion, contenido="", fecha_reseña=None, origen_simulado_ip=""):
        self.id_reseña = id_reseña
        self.id_juego = id_juego
        self.id_usuario = id_usuario
        self.puntuacion = puntuacion
        self.contenido = contenido
        self.fecha_reseña = fecha_reseña
        self.origen_simulado_ip = origen_simulado_ip

    def __str__(self):
        return (f"Reseña(ID: {self.id_reseña}, Juego ID: {self.id_juego}, Usuario ID: {self.id_usuario}, "
                f"Puntuación: {self.puntuacion}, Fecha: {self.fecha_reseña})")

    def __repr__(self):
        return self.__str__()