import sqlite3
from .conexion_bd import obtener_conexion 
import time 

class BaseDAO:
    def __init__(self):
        pass

    def _ejecutar_consulta(self, consulta, parametros=None, es_escritura=False):
        conexion = obtener_conexion()
        if conexion is None:
            print("Error: No se pudo establecer conexión con la base de datos.")
            return None

        cursor = conexion.cursor()
        try:
            if parametros:
                cursor.execute(consulta, parametros)
            else:
                cursor.execute(consulta)

            if es_escritura:
                conexion.commit() 
                return cursor.lastrowid
            else:
                return cursor.fetchall()
        except sqlite3.IntegrityError as e:
            print(f"Error de integridad en la base de datos: {e}")
            conexion.rollback() 
            raise 
        except sqlite3.Error as e:
            print(f"Error en la base de datos: {e}")
            conexion.rollback()
            raise 
        finally:
            conexion.close()


class JuegoDAO(BaseDAO):
    def insertar_juego(self, nombre, descripcion=""):
        consulta = "INSERT INTO Juegos (nombre, descripcion) VALUES (?, ?);"
        try:
            id_juego = self._ejecutar_consulta(consulta, (nombre, descripcion), es_escritura=True)
            print(f"Juego '{nombre}' insertado con ID: {id_juego}")
            return id_juego
        except Exception:
            return None 

    def obtener_juego_por_id(self, id_juego):
        consulta = "SELECT id_juego, nombre, descripcion, puntuacion_media, total_reseñas, puntuacion_acumulada FROM Juegos WHERE id_juego = ?;"
        resultado = self._ejecutar_consulta(consulta, (id_juego,))
        return resultado[0] if resultado else None

    def obtener_juego_por_nombre(self, nombre_juego):
        consulta = "SELECT id_juego, nombre, descripcion, puntuacion_media, total_reseñas, puntuacion_acumulada FROM Juegos WHERE nombre = ?;"
        resultado = self._ejecutar_consulta(consulta, (nombre_juego,))
        return resultado[0] if resultado else None

    def obtener_todos_los_juegos(self):
        consulta = "SELECT id_juego, nombre, descripcion, puntuacion_media, total_reseñas, puntuacion_acumulada FROM Juegos;"
        return self._ejecutar_consulta(consulta)

    def actualizar_puntuacion_juego(self, id_juego, nueva_puntuacion_media, nuevo_total_reseñas, nueva_puntuacion_acumulada):
        consulta = "UPDATE Juegos SET puntuacion_media = ?, total_reseñas = ?, puntuacion_acumulada = ? WHERE id_juego = ?;"
        try:
            self._ejecutar_consulta(consulta, (nueva_puntuacion_media, nuevo_total_reseñas, nueva_puntuacion_acumulada, id_juego), es_escritura=True)
            print(f"Puntuación del juego ID {id_juego} actualizada.")
            return True
        except Exception:
            return False


class UsuarioDAO(BaseDAO):
    def insertar_usuario(self, nombre_usuario, tipo_usuario):
        consulta = "INSERT INTO Usuarios (nombre_usuario, tipo_usuario) VALUES (?, ?);"
        try:
            id_usuario = self._ejecutar_consulta(consulta, (nombre_usuario, tipo_usuario), es_escritura=True)
            print(f"Usuario '{nombre_usuario}' insertado con ID: {id_usuario}")
            return id_usuario
        except sqlite3.IntegrityError: 
            print(f"Error: El usuario '{nombre_usuario}' ya existe.")
            return None
        except Exception as e:
            print(f"Error al insertar usuario: {e}")
            return None

    def obtener_usuario_por_id(self, id_usuario):
        consulta = "SELECT id_usuario, nombre_usuario, tipo_usuario FROM Usuarios WHERE id_usuario = ?;"
        resultado = self._ejecutar_consulta(consulta, (id_usuario,))
        return resultado[0] if resultado else None

    def obtener_usuario_por_nombre(self, nombre_usuario):
        consulta = "SELECT id_usuario, nombre_usuario, tipo_usuario FROM Usuarios WHERE nombre_usuario = ?;"
        resultado = self._ejecutar_consulta(consulta, (nombre_usuario,))
        return resultado[0] if resultado else None

    def obtener_todos_los_usuarios(self):
        consulta = "SELECT id_usuario, nombre_usuario, tipo_usuario FROM Usuarios;"
        return self._ejecutar_consulta(consulta)


class ReseñaDAO(BaseDAO):
    def insertar_reseña(self, id_juego, id_usuario, puntuacion, contenido="", origen_simulado_ip=""):
        consulta = "INSERT INTO Reseñas (id_juego, id_usuario, puntuacion, contenido, origen_simulado_ip) VALUES (?, ?, ?, ?, ?);"
        try:
            id_reseña = self._ejecutar_consulta(consulta, (id_juego, id_usuario, puntuacion, contenido, origen_simulado_ip), es_escritura=True)
            print(f"Reseña insertada con ID: {id_reseña} para Juego ID {id_juego} y Usuario ID {id_usuario}.")
            return id_reseña
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: Reseñas.id_juego, Reseñas.id_usuario" in str(e):
                print(f"Advertencia: El usuario ID {id_usuario} ya ha reseñado el juego ID {id_juego}. Reseña duplicada rechazada por la base de datos.")
            else:
                print(f"Error de integridad al insertar reseña: {e}")
            return None
        except Exception as e:
            print(f"Error general al insertar reseña: {e}")
            return None

    def obtener_reseñas_por_juego(self, id_juego):
        consulta = "SELECT id_reseña, id_juego, id_usuario, puntuacion, contenido, fecha_reseña, origen_simulado_ip FROM Reseñas WHERE id_juego = ?;"
        return self._ejecutar_consulta(consulta, (id_juego,))

    def verificar_existencia_reseña(self, id_juego, id_usuario):
        consulta = "SELECT COUNT(*) FROM Reseñas WHERE id_juego = ? AND id_usuario = ?;"
        resultado = self._ejecutar_consulta(consulta, (id_juego, id_usuario))
        return resultado[0][0] > 0 if resultado else False

    def obtener_total_reseñas_y_puntuacion_acumulada_para_juego(self, id_juego):
        consulta = "SELECT COUNT(puntuacion), SUM(puntuacion) FROM Reseñas WHERE id_juego = ?;"
        resultado = self._ejecutar_consulta(consulta, (id_juego,))
        if resultado and resultado[0][0] is not None:
            total_reseñas = resultado[0][0]
            puntuacion_acumulada = resultado[0][1] if resultado[0][1] is not None else 0
            return total_reseñas, puntuacion_acumulada
        return 0, 0 

if __name__ == '__main__':
    print("--- Probando DAOs ---")
    juego_dao = JuegoDAO()
    usuario_dao = UsuarioDAO()
    reseña_dao = ReseñaDAO()

    # Insertar juegos
    id_juego1 = juego_dao.insertar_juego("The Witcher 3", "Un RPG épico.")
    id_juego2 = juego_dao.insertar_juego("Cyberpunk 2077", "RPG de ciencia ficción.")

    # Insertar usuarios
    id_usuario1 = usuario_dao.insertar_usuario("Geralt_fan", "usuario_normal")
    id_usuario2 = usuario_dao.insertar_usuario("CriticoMaster", "critico")
    id_usuario3 = usuario_dao.insertar_usuario("JugadorAnonimo", "usuario_normal")


    if id_juego1 and id_usuario1:
        # --- Insertar reseñas ---
        print("\n--- Insertando Reseñas ---")
        # Reseña exitosa
        reseña_dao.insertar_reseña(id_juego1, id_usuario1, 9, "Excelente juego, mucha profundidad.")
        # Intentar insertar la misma reseña para el mismo usuario/juego (debería fallar por UNIQUE constraint)
        reseña_dao.insertar_reseña(id_juego1, id_usuario1, 5, "Esta reseña es duplicada!", "192.168.1.100")

        if id_usuario2:
            reseña_dao.insertar_reseña(id_juego1, id_usuario2, 10, "Obra maestra!", "10.0.0.5")
            reseña_dao.insertar_reseña(id_juego2, id_usuario2, 7, "Interesante, pero le falta pulido.", "10.0.0.5")

        if id_usuario3:
            reseña_dao.insertar_reseña(id_juego1, id_usuario3, 8, "Muy bueno, lo recomiendo.", "172.16.0.1")


        #Obtener y mostrar datos
        print("\n--- Datos de Juegos ---")
        juegos = juego_dao.obtener_todos_los_juegos()
        if juegos:
            for juego in juegos:
                print(f"Juego: {juego}")

        print("\n--- Datos de Usuarios ---")
        usuarios = usuario_dao.obtener_todos_los_usuarios()
        if usuarios:
            for usuario in usuarios:
                print(f"Usuario: {usuario}")

        print("\n--- Reseñas para The Witcher 3 (ID {id_juego1}) ---")
        if id_juego1:
            reseñas_thewitcher = reseña_dao.obtener_reseñas_por_juego(id_juego1)
            if reseñas_thewitcher:
                for reseña in reseñas_thewitcher:
                    print(f"Reseña: {reseña}")
            else:
                print("No hay reseñas para The Witcher 3.")

        print("\n--- Verificando existencia de reseña ---")
        if id_juego1 and id_usuario1:
            existe_reseña = reseña_dao.verificar_existencia_reseña(id_juego1, id_usuario1)
            print(f"¿Usuario ID {id_usuario1} ya reseñó Juego ID {id_juego1}? {existe_reseña}")
        if id_juego2 and id_usuario1:
            existe_reseña = reseña_dao.verificar_existencia_reseña(id_juego2, id_usuario1)
            print(f"¿Usuario ID {id_usuario1} ya reseñó Juego ID {id_juego2}? {existe_reseña}")

        print("\n--- Calculando total y acumulado de reseñas para The Witcher 3 ---")
        if id_juego1:
            total, acumulado = reseña_dao.obtener_total_reseñas_y_puntuacion_acumulada_para_juego(id_juego1)
            print(f"Total reseñas The Witcher 3: {total}, Puntuación acumulada: {acumulado}")

    print("\n--- Fin de prueba de DAOs ---")