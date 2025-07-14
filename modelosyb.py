class Juego:
    def __init__(self, id, titulo, genero, anio_lanzamiento, puntuacion_media=0.0):
        self.id = id
        self.titulo = titulo
        self.genero = genero
        self.anio_lanzamiento = anio_lanzamiento
        self.puntuacion_media = puntuacion_media

    def __repr__(self):
        # Representación para la depuración
        return (f"Juego(ID: {self.id}, Título: '{self.titulo}', Género: '{self.genero}', "
                f"Año de Lanzamiento: {self.anio_lanzamiento}, Puntuación Media: {self.puntuacion_media:.2f})")

    def a_diccionario(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "genero": self.genero,
            "anio_lanzamiento": self.anio_lanzamiento,
            "puntuacion_media": self.puntuacion_media
        }


class Usuario:
    def __init__(self, id, nombre_usuario, es_critico=False):
        self.id = id
        self.nombre_usuario = nombre_usuario
        self.es_critico = es_critico # True si es crítico, False si es usuario normal

    def __repr__(self):
        tipo_usuario = "Crítico" if self.es_critico else "Usuario"
        return f"Usuario(ID: {self.id}, Nombre de Usuario: '{self.nombre_usuario}', Tipo: {tipo_usuario})"

    def a_diccionario(self):
        return {
            "id": self.id,
            "nombre_usuario": self.nombre_usuario,
            "es_critico": self.es_critico
        }


class Resena:
    def __init__(self, id, id_juego, id_usuario, puntuacion, comentario, tipo_resena, marca_tiempo=None):
        self.id = id
        self.id_juego = id_juego
        self.id_usuario = id_usuario
        self.puntuacion = puntuacion
        self.comentario = comentario
        self.tipo_resena = tipo_resena
        self.marca_tiempo = marca_tiempo # Se llenará automáticamente por la DB si es None

    def __repr__(self):
        return (f"Reseña(ID: {self.id}, ID Juego: {self.id_juego}, ID Usuario: {self.id_usuario}, "
                f"Puntuación: {self.puntuacion}, Tipo: '{self.tipo_resena}')")

    def a_diccionario(self):
        return {
            "id": self.id,
            "id_juego": self.id_juego,
            "id_usuario": self.id_usuario,
            "puntuacion": self.puntuacion,
            "comentario": self.comentario,
            "tipo_resena": self.tipo_resena,
            "marca_tiempo": self.marca_tiempo
        }