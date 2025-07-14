import threading
import multiprocessing 
from .gestor_base_datos import GestorBaseDatos
from .modelosyb import Juego, Usuario, Resena
import time

class ServicioResenas:
    def __init__(self, gestor_db: GestorBaseDatos, lock_manager=None):
        self.gestor_db = gestor_db
        self.lock_manager = lock_manager 

        
        if self.lock_manager:
            self.bloqueos_juegos = self.lock_manager.dict()
        else:
            self.bloqueos_juegos = {}

        
        self.bloqueos_juegos_acceso_lock = threading.Lock() 

    def _obtener_bloqueo_juego(self, id_juego):
        with self.bloqueos_juegos_acceso_lock:
            if id_juego not in self.bloqueos_juegos:
                if self.lock_manager:
                    # Crea un bloqueo gestionado por el Manager para procesos
                    self.bloqueos_juegos[id_juego] = self.lock_manager.Lock() 
                else:
                    # Crea un bloqueo estándar de threading para hilos
                    self.bloqueos_juegos[id_juego] = threading.Lock() 
            return self.bloqueos_juegos[id_juego]

    def agregar_juego(self, titulo, genero, anio_lanzamiento):
        self.gestor_db.conectar()
        try:
            juego_existente = self.gestor_db.obtener_juego_por_titulo(titulo)
            if juego_existente:
                print(f"ERROR: El juego '{titulo}' ya existe.")
                return None

            cursor = self.gestor_db.conexion.cursor()
            cursor.execute(""" INSERT INTO juegos (titulo, genero, anio_lanzamiento) VALUES (?, ?, ?) """, (titulo, genero, anio_lanzamiento))
            self.gestor_db.conexion.commit()
            id_juego = cursor.lastrowid
            print(f"Juego '{titulo}' agregado con ID: {id_juego}")
            return Juego(id_juego, titulo, genero, anio_lanzamiento)
        except Exception as e:
            print(f"Error al agregar juego: {e}")
            return None
        finally:
            self.gestor_db.cerrar()

    def agregar_usuario(self, nombre_usuario, es_critico=False):
        self.gestor_db.conectar()
        try:
            usuario_existente = self.gestor_db.obtener_usuario_por_nombre(nombre_usuario)
            if usuario_existente:
                print(f"ERROR: El usuario '{nombre_usuario}' ya existe.")
                return None

            cursor = self.gestor_db.conexion.cursor()
            cursor.execute(""" INSERT INTO usuarios (nombre_usuario, es_critico) VALUES (?, ?) """, (nombre_usuario, 1 if es_critico else 0)) # SQLite usa 0/1 para booleanos
            self.gestor_db.conexion.commit()
            id_usuario = cursor.lastrowid
            tipo_usuario = "crítico" if es_critico else "usuario"
            print(f"Usuario '{nombre_usuario}' ({tipo_usuario}) agregado con ID: {id_usuario}")
            return Usuario(id_usuario, nombre_usuario, es_critico)
        except Exception as e:
            print(f"Error al agregar usuario: {e}")
            return None
        finally:
            self.gestor_db.cerrar()

    def _calcular_puntuacion_media(self, id_juego):
        cursor = self.gestor_db.conexion.cursor()
        cursor.execute("SELECT puntuacion FROM resenas WHERE id_juego = ?", (id_juego,))
        puntuaciones = [row['puntuacion'] for row in cursor.fetchall()]
        if puntuaciones:
            return sum(puntuaciones) / len(puntuaciones)
        return 0.0

    def enviar_resena(self, id_juego, id_usuario, puntuacion, comentario, tipo_resena, origen="Hilo"):
        if not (0 <= puntuacion <= 100):
            print(f"[{origen}] ERROR: La puntuación {puntuacion} debe estar entre 0 y 100. Reseña no enviada.")
            return False
        bloqueo_juego = self._obtener_bloqueo_juego(id_juego)

        with bloqueo_juego:
            print(f"[{origen} {threading.current_thread().name}]: Adquiriendo bloqueo para juego ID {id_juego}...")
            time.sleep(0.1)

            self.gestor_db.conectar()
            try:
                cursor = self.gestor_db.conexion.cursor()
                cursor.execute(""" SELECT id FROM resenas WHERE id_juego = ? AND id_usuario = ? """, (id_juego, id_usuario))
                if cursor.fetchone():
                    print(f"[{origen} {threading.current_thread().name}]: ERROR - El usuario con ID {id_usuario} ya ha enviado una reseña para el juego ID {id_juego}. Reseña no enviada.")
                    return False

                # 1. Insertar la nueva reseña
                cursor.execute(""" INSERT INTO resenas (id_juego, id_usuario, puntuacion, comentario, tipo_resena) VALUES (?, ?, ?, ?, ?) """, (id_juego, id_usuario, puntuacion, comentario, tipo_resena))

                # 2. Recalcular la puntuación media del juego (la conexión sigue abierta)
                nueva_puntuacion_media = self._calcular_puntuacion_media(id_juego)

                # 3. Actualizar la puntuación media en la tabla 'juegos' (la conexión sigue abierta)
                cursor.execute(""" UPDATE juegos SET puntuacion_media = ? WHERE id = ? """, (nueva_puntuacion_media, id_juego))

                self.gestor_db.conexion.commit() # Confirmar la transacción
                print(f"[{origen} {threading.current_thread().name}]: Reseña de {id_usuario} para juego {id_juego} enviada. Nueva puntuación media: {nueva_puntuacion_media:.2f}")
                return True
            except Exception as e:
                print(f"[{origen} {threading.current_thread().name}]: Error al enviar reseña: {e}")
                self.gestor_db.conexion.rollback() # Deshacer si hay un error
                return False
            finally:
                self.gestor_db.cerrar() # Cerramos la conexión después de la transacción
                print(f"[{origen} {threading.current_thread().name}]: Liberando bloqueo para juego ID {id_juego}.")

    def obtener_detalles_juego(self, id_juego):
        self.gestor_db.conectar()
        try:
            cursor = self.gestor_db.conexion.cursor()
            cursor.execute("SELECT * FROM juegos WHERE id = ?", (id_juego,))
            juego_data = cursor.fetchone()
            if not juego_data:
                print(f"Juego con ID {id_juego} no encontrado.")
                return None

            juego = Juego(juego_data['id'], juego_data['titulo'], juego_data['genero'], juego_data['anio_lanzamiento'], juego_data['puntuacion_media'])

            cursor.execute(""" SELECT r.*, u.nombre_usuario, u.es_critico FROM resenas r JOIN usuarios u ON r.id_usuario = u.id WHERE r.id_juego = ? ORDER BY r.marca_tiempo DESC """, (id_juego,))
            resenas_data = cursor.fetchall()
            
            resenas_completas = []
            for r_data in resenas_data:
                resenas_completas.append({
                    "resena": Resena(r_data['id'], r_data['id_juego'], r_data['id_usuario'], r_data['puntuacion'], r_data['comentario'], r_data['tipo_resena'], r_data['marca_tiempo']),
                    "usuario": Usuario(r_data['id_usuario'], r_data['nombre_usuario'], bool(r_data['es_critico']))
                })
            
            return {"juego": juego, "resenas": resenas_completas}

        except Exception as e:
            print(f"Error al obtener detalles del juego ID {id_juego}: {e}")
            return None
        finally:
            self.gestor_db.cerrar()

    def listar_juegos(self):
        self.gestor_db.conectar()
        try:
            cursor = self.gestor_db.conexion.cursor()
            cursor.execute("SELECT * FROM juegos ORDER BY titulo")
            juegos_data = cursor.fetchall()

            juegos_lista = [
                Juego(data['id'], data['titulo'], data['genero'], data['anio_lanzamiento'], data['puntuacion_media'])
                for data in juegos_data
            ]
            return juegos_lista
        except Exception as e:
            print(f"Error al listar juegos: {e}")
            return []
        finally:
            self.gestor_db.cerrar()

    def obtener_juego_por_titulo(self, titulo):
        self.gestor_db.conectar()
        try:
            cursor = self.gestor_db.conexion.cursor()
            cursor.execute("SELECT * FROM juegos WHERE titulo = ?", (titulo,))
            juego_data = cursor.fetchone()
            if juego_data:
                return Juego(juego_data['id'], juego_data['titulo'], juego_data['genero'],
                             juego_data['anio_lanzamiento'], juego_data['puntuacion_media'])
            return None
        except Exception as e:
            print(f"Error al obtener juego por título: {e}")
            return None
        finally:
            self.gestor_db.cerrar()
            
    def obtener_usuario_por_nombre(self, nombre_usuario):
        self.gestor_db.conectar()
        try:
            cursor = self.gestor_db.conexion.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = ?", (nombre_usuario,))
            usuario_data = cursor.fetchone()
            if usuario_data:
                return Usuario(usuario_data['id'], usuario_data['nombre_usuario'], bool(usuario_data['es_critico']))
            return None
        except Exception as e:
            print(f"Error al obtener usuario por nombre: {e}")
            return None
        finally:
            self.gestor_db.cerrar()
