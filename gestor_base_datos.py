import sqlite3
import os

class GestorBaseDatos:
    """
    Clase para gestionar la conexión y operaciones con la base de datos SQLite.
    """
    def __init__(self, nombre_db="resenas.db"):
        
        self.ruta_db = os.path.join("App de reseñas", nombre_db)
        self.conexion = None
        
        
        directorio_db = os.path.dirname(self.ruta_db)
        if directorio_db and not os.path.exists(directorio_db):
            os.makedirs(directorio_db)
            print(f"Directorio '{directorio_db}' creado para la base de datos.")


    def conectar(self):
        """Establece la conexión con la base de datos."""
        try:
            self.conexion = sqlite3.connect(self.ruta_db)
            self.conexion.row_factory = sqlite3.Row 
            self.conexion.execute("PRAGMA foreign_keys = ON")
            print("✅ Conexión a la base de datos exitosa.")
        except sqlite3.Error as e:
            print(f"❌ Error al conectar a la base de datos: {e}")

    def cerrar(self):
        """Cierra la conexión con la base de datos."""
        if self.conexion:
            self.conexion.close()

    def crear_tablas(self):
        """Crea las tablas 'juegos', 'usuarios' y 'resenas' si no existen."""
        self.conectar()
        try:
            cursor = self.conexion.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS juegos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL UNIQUE,
                    genero TEXT,
                    anio_lanzamiento INTEGER,
                    puntuacion_media REAL DEFAULT 0.0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_usuario TEXT NOT NULL UNIQUE,
                    es_critico BOOLEAN NOT NULL DEFAULT 0 -- 0 para usuario normal, 1 para crítico
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resenas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_juego INTEGER NOT NULL,
                    id_usuario INTEGER NOT NULL,
                    puntuacion INTEGER NOT NULL,
                    comentario TEXT,
                    tipo_resena TEXT NOT NULL, -- 'usuario' o 'critico'
                    marca_tiempo DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_juego) REFERENCES juegos (id) ON DELETE CASCADE,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios (id) ON DELETE CASCADE,
                    CHECK (puntuacion >= 0 AND puntuacion <= 100)
                )
            """)

            self.conexion.commit()
            print("Tablas creadas exitosamente o ya existen.")
        except sqlite3.Error as e:
            print(f"❌ Error al crear tablas: {e}")
        finally:
            self.cerrar()

    def obtener_juego_por_titulo(self, titulo):
        """Obtiene un juego por su título."""
        self.conectar()
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT * FROM juegos WHERE titulo = ?", (titulo,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"❌ Error BD al obtener juego por título: {e}")
            return None
        finally:
            self.cerrar()

    def obtener_usuario_por_nombre(self, nombre_usuario):
        """Obtiene un usuario por su nombre de usuario."""
        self.conectar()
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = ?", (nombre_usuario,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"❌ Error BD al obtener usuario por nombre: {e}")
            return None
        finally:
            self.cerrar()
            
    def obtener_juego_por_id(self, id_juego):
        """Obtiene un juego por su ID."""
        self.conectar()
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT * FROM juegos WHERE id = ?", (id_juego,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"❌ Error BD al obtener juego por ID: {e}")
            return None
        finally:
            self.cerrar()

    def obtener_usuario_por_id(self, id_usuario):
        """Obtiene un usuario por su ID."""
        self.conectar()
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id_usuario,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"❌ Error BD al obtener usuario por ID: {e}")
            return None
        finally:
            self.cerrar()

    def listar_juegos_db(self):
        """Lista todos los juegos de la base de datos."""
        self.conectar()
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT * FROM juegos ORDER BY titulo")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Error BD al listar juegos: {e}")
            return []
        finally:
            self.cerrar()

    def obtener_resenas_para_juego(self, id_juego):
        """Obtiene todas las reseñas para un juego dado su ID."""
        self.conectar()
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT * FROM resenas WHERE id_juego = ?", (id_juego,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Error BD al obtener reseñas para juego: {e}")
            return []
        finally:
            self.cerrar()

    def insertar_resena_db(self, id_juego, id_usuario, puntuacion, comentario, tipo_resena):
        """Inserta una nueva reseña en la base de datos."""
        cursor = self.conexion.cursor()
        cursor.execute("""
            INSERT INTO resenas (id_juego, id_usuario, puntuacion, comentario, tipo_resena)
            VALUES (?, ?, ?, ?, ?)
        """, (id_juego, id_usuario, puntuacion, comentario, tipo_resena))
        return cursor.lastrowid

    def actualizar_puntuacion_media_juego_db(self, id_juego, puntuacion_media):
        """Actualiza la puntuación media de un juego en la base de datos."""
        cursor = self.conexion.cursor()
        cursor.execute("""
            UPDATE juegos
            SET puntuacion_media = ?
            WHERE id = ?
        """, (puntuacion_media, id_juego))


# --- Bloque de prueba para verificar la creación de la DB y tablas ---
if __name__ == "__main__":
    gestor_db = GestorBaseDatos()
    gestor_db.crear_tablas()

    ruta_archivo_db = os.path.join("App de reseñas", "resenas.db")

    if os.path.exists(ruta_archivo_db):
        print(f"\nArchivo '{os.path.basename(ruta_archivo_db)}' creado exitosamente en '{os.path.dirname(ruta_archivo_db)}/'.")
    else:
        print(f"\n❌ ERROR: El archivo '{os.path.basename(ruta_archivo_db)}' NO se encontró donde se esperaba.")

    gestor_db.conectar()
    try:
        if not gestor_db.obtener_juego_por_titulo("The Witcher 3"):
            print("Insertando juego de prueba: The Witcher 3...")
            gestor_db.conexion.execute("INSERT INTO juegos (titulo, genero, anio_lanzamiento) VALUES (?, ?, ?)", ("The Witcher 3", "RPG", 2015))
            gestor_db.conexion.commit()
        else:
            print("El juego 'The Witcher 3' ya existe.")

        if not gestor_db.obtener_usuario_por_nombre("GamerPro"):
            print("Insertando usuario de prueba: GamerPro...")
            gestor_db.conexion.execute("INSERT INTO usuarios (nombre_usuario, es_critico) VALUES (?, ?)", ("GamerPro", 0))
            gestor_db.conexion.commit()
        else:
            print("El usuario 'GamerPro' ya existe.")

        juego_data = gestor_db.obtener_juego_por_titulo("The Witcher 3")
        if juego_data:
            print(f"Juego obtenido por título: {juego_data['titulo']}, ID: {juego_data['id']}")

        usuario_data = gestor_db.obtener_usuario_por_nombre("GamerPro")
        if usuario_data:
            print(f"Usuario obtenido por nombre: {usuario_data['nombre_usuario']}, ID: {usuario_data['id']}")

    except Exception as e:
        print(f"❌ Error durante la prueba de inserción/obtención: {e}")
    finally:
        gestor_db.cerrar()
