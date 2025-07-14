import sqlite3
import os

NOMBRE_BASE_DE_DATOS = 'resenas_db.sqlite'

def obtener_ruta_base_de_datos():
    dir_actual = os.path.dirname(__file__)
    ruta_proyecto = os.path.join(dir_actual, '..')
    ruta_bd = os.path.join(ruta_proyecto, NOMBRE_BASE_DE_DATOS)
    return os.path.abspath(ruta_bd)

def obtener_conexion():
    try:
        ruta_bd = obtener_ruta_base_de_datos()
        conexion = sqlite3.connect(ruta_bd)
        conexion.execute("PRAGMA foreign_keys = ON;") 
        return conexion
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def crear_tablas():
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:
            # Tabla Juegos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Juegos (
                    id_juego INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    puntuacion_media REAL DEFAULT 0.0,
                    total_reseñas INTEGER DEFAULT 0,
                    puntuacion_acumulada INTEGER DEFAULT 0
                );
            ''')
            print("Tabla 'Juegos' verificada/creada exitosamente.")

            # Tabla Usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Usuarios (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_usuario TEXT UNIQUE NOT NULL,
                    tipo_usuario TEXT NOT NULL -- Ej: 'critico', 'usuario_normal'
                );
            ''')
            print("Tabla 'Usuarios' verificada/creada exitosamente.")

            # Tabla Reseñas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Reseñas (
                    id_reseña INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_juego INTEGER NOT NULL,
                    id_usuario INTEGER NOT NULL,
                    puntuacion INTEGER NOT NULL CHECK (puntuacion >= 1 AND puntuacion <= 10),
                    contenido TEXT,
                    fecha_reseña DATETIME DEFAULT CURRENT_TIMESTAMP,
                    origen_simulado_ip TEXT,
                    UNIQUE(id_juego, id_usuario),
                    FOREIGN KEY (id_juego) REFERENCES Juegos(id_juego),
                    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
                );
            ''')
            print("Tabla 'Reseñas' verificada/creada exitosamente.")

            conexion.commit() 
        except sqlite3.Error as e:
            print(f"Error al crear tablas: {e}")
        finally:
            conexion.close()
    else:
        print("No se pudo obtener una conexión a la base de datos para crear las tablas.")


if __name__ == '__main__':
    crear_tablas()
    print(f"Base de datos '{NOMBRE_BASE_DE_DATOS}' y tablas inicializadas en: {obtener_ruta_base_de_datos()}")