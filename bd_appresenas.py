import sqlite3
import os

def crear_base_de_datos_y_tablas():
    
    nombre_carpeta_db = "Base de datos"
    nombre_archivo_db = "base_de_datos_simple.db" 

    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    ruta_directorio_db = os.path.join(script_dir, nombre_carpeta_db)
    
    if not os.path.exists(ruta_directorio_db):
        os.makedirs(ruta_directorio_db)
        print(f"✅ Carpeta '{nombre_carpeta_db}' creada.")
    
    ruta_db_completa = os.path.join(ruta_directorio_db, nombre_archivo_db)

    conexion = None
    try:
        conexion = sqlite3.connect(ruta_db_completa)
        cursor = conexion.cursor()
        conexion.execute("PRAGMA foreign_keys = ON")
        print(f"✅ Conexión a la base de datos '{nombre_archivo_db}' exitosa.")

        # Tabla juegos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS juegos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL UNIQUE,
                genero TEXT,
                anio_lanzamiento INTEGER,
                puntuacion_media REAL DEFAULT 0.0
            )
        """)
        print("✅ Tabla 'juegos' verificada/creada.")

        # Tabla usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_usuario TEXT NOT NULL UNIQUE,
                es_critico BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        print("✅ Tabla 'usuarios' verificada/creada.")

        # Tabla resenas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resenas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_juego INTEGER NOT NULL,
                id_usuario INTEGER NOT NULL,
                puntuacion INTEGER NOT NULL,
                comentario TEXT,
                tipo_resena TEXT NOT NULL,
                marca_tiempo DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_juego) REFERENCES juegos (id) ON DELETE CASCADE,
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id) ON DELETE CASCADE,
                CHECK (puntuacion >= 0 AND puntuacion <= 100)
            )
        """)
        print("✅ Tabla 'resenas' verificada/creada.")

        conexion.commit() 
        print("🎉 Todas las tablas necesarias han sido creadas o ya existen.")

    except sqlite3.Error as e:
        print(f"❌ Error durante la operación de base de datos: {e}")
    finally:
        if conexion:
            conexion.close()
            print("Conexión a la base de datos cerrada.")
    
    if os.path.exists(ruta_db_completa):
        print(f"\n✨ ¡Confirmado! El archivo de base de datos '{nombre_archivo_db}' existe en: {ruta_directorio_db}")
    else:
        print(f"\n❌ ERROR: El archivo de base de datos '{nombre_archivo_db}' NO se encontró en: {ruta_directorio_db}")

if __name__ == "__main__":
    crear_base_de_datos_y_tablas()