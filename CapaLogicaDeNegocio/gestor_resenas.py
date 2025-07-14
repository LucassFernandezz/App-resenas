import sqlite3
from CapaDeDatos.daos import JuegoDAO, UsuarioDAO, ReseñaDAO
from CapaLogicaDeNegocio.modelos import Juego, Usuario, Reseña
import threading
import multiprocessing
import time

class GestorResenas:
    def __init__(self):
        self.juego_dao = JuegoDAO()
        self.usuario_dao = UsuarioDAO()
        self.reseña_dao = ReseñaDAO()
        self.lock_envio_reseña = threading.Lock() 
        self.lock_actualizacion_juego = threading.Lock() 

        self._inicializar_datos_base()

    def _inicializar_datos_base(self):
        print("\n--- Inicializando datos base (GestorResenas) ---")
        # Insertar juegos si no existen
        if not self.juego_dao.obtener_juego_por_nombre("The Witcher 3"):
            self.juego_dao.insertar_juego("The Witcher 3", "Un RPG épico de fantasía oscura.")
        if not self.juego_dao.obtener_juego_por_nombre("Cyberpunk 2077"):
            self.juego_dao.insertar_juego("Cyberpunk 2077", "Un RPG futurista en un mundo distópico.")
        if not self.juego_dao.obtener_juego_por_nombre("Elden Ring"):
            self.juego_dao.insertar_juego("Elden Ring", "Un desafiante ARPG de mundo abierto.")

        # Insertar usuarios si no existen
        if not self.usuario_dao.obtener_usuario_por_nombre("Usuario Normal 1"):
            self.usuario_dao.insertar_usuario("Usuario Normal 1", "usuario_normal")
        if not self.usuario_dao.obtener_usuario_por_nombre("Usuario Normal 2"):
            self.usuario_dao.insertar_usuario("Usuario Normal 2", "usuario_normal")
        if not self.usuario_dao.obtener_usuario_por_nombre("Critico Pro"):
            self.usuario_dao.insertar_usuario("Critico Pro", "critico")
        if not self.usuario_dao.obtener_usuario_por_nombre("Gamer X"):
            self.usuario_dao.insertar_usuario("Gamer X", "usuario_normal")
        if not self.usuario_dao.obtener_usuario_por_nombre("Developer Y"):
            self.usuario_dao.insertar_usuario("Developer Y", "critico")

        print("--- Datos base inicializados. ---\n")


    def _mapear_datos_a_objeto(self, datos, clase_modelo):
        if not datos:
            return None
        return clase_modelo(*datos)

    def obtener_juegos(self):
        juegos_raw = self.juego_dao.obtener_todos_los_juegos()
        return [self._mapear_datos_a_objeto(j, Juego) for j in juegos_raw]

    def obtener_usuarios(self):
        usuarios_raw = self.usuario_dao.obtener_todos_los_usuarios()
        return [self._mapear_datos_a_objeto(u, Usuario) for u in usuarios_raw]

    def obtener_juego_por_id(self, id_juego):
        juego_raw = self.juego_dao.obtener_juego_por_id(id_juego)
        return self._mapear_datos_a_objeto(juego_raw, Juego)

    def obtener_usuario_por_id(self, id_usuario):
        usuario_raw = self.usuario_dao.obtener_usuario_por_id(id_usuario)
        return self._mapear_datos_a_objeto(usuario_raw, Usuario)
    
    def obtener_usuario_por_nombre(self, nombre_usuario):
        usuario_raw = self.usuario_dao.obtener_usuario_por_nombre(nombre_usuario)
        return self._mapear_datos_a_objeto(usuario_raw, Usuario)

    def obtener_reseñas_por_juego(self, id_juego):
        reseñas_raw = self.reseña_dao.obtener_reseñas_por_juego(id_juego)
        return [self._mapear_datos_a_objeto(r, Reseña) for r in reseñas_raw]

    def _recalcular_puntuacion_media_juego(self, id_juego):
        total_reseñas, puntuacion_acumulada = self.reseña_dao.obtener_total_reseñas_y_puntuacion_acumulada_para_juego(id_juego)
        
        puntuacion_media = puntuacion_acumulada / total_reseñas if total_reseñas > 0 else 0.0
        
        with self.lock_actualizacion_juego:
            self.juego_dao.actualizar_puntuacion_juego(id_juego, puntuacion_media, total_reseñas, puntuacion_acumulada)
            print(f"DEBUG: Juego ID {id_juego} - Media: {puntuacion_media:.2f}, Total: {total_reseñas}, Acumulado: {puntuacion_acumulada}")


    def enviar_reseña(self, id_juego, id_usuario, puntuacion, contenido="", origen_simulado_ip=""):
        # Verificamos si el usuario y el juego existen y los mapeamos a objetos de modelo
        # FIX: Mapear las tuplas a objetos de modelo
        juego = self._mapear_datos_a_objeto(self.juego_dao.obtener_juego_por_id(id_juego), Juego)
        usuario = self._mapear_datos_a_objeto(self.usuario_dao.obtener_usuario_por_id(id_usuario), Usuario)

        if not juego:
            print(f"Error: El juego con ID {id_juego} no existe.")
            return False
        if not usuario:
            print(f"Error: El usuario con ID {id_usuario} no existe.")
            return False
        
        #Logica de Concurrencia (Exclusión Mutua)
        with self.lock_envio_reseña:
            print(f"Hilo/Proceso {threading.current_thread().name} o {multiprocessing.current_process().name}: Intentando enviar reseña...")
            
            time.sleep(0.01)

            if self.reseña_dao.verificar_existencia_reseña(id_juego, id_usuario):
                print(f"Hilo/Proceso {threading.current_thread().name} o {multiprocessing.current_process().name}: "
                    f"El usuario '{usuario.nombre_usuario}' (ID: {id_usuario}) ya ha enviado una reseña para '{juego.nombre}' (ID: {id_juego}). Reseña rechazada.")
                return False

            try:
                id_reseña = self.reseña_dao.insertar_reseña(id_juego, id_usuario, puntuacion, contenido, origen_simulado_ip)
                if id_reseña:
                    print(f"Hilo/Proceso {threading.current_thread().name} o {multiprocessing.current_process().name}: "
                        f"Reseña enviada exitosamente por '{usuario.nombre_usuario}' para '{juego.nombre}' (Puntuación: {puntuacion}).")
                    
                    self._recalcular_puntuacion_media_juego(id_juego)
                    return True
                else:
                    print(f"Hilo/Proceso {threading.current_thread().name} o {multiprocessing.current_process().name}: "
                        f"Fallo al enviar reseña. Es posible que ya exista una reseña de este usuario para este juego (duplicado detectado).")
                    return False
            except sqlite3.IntegrityError as e:
                print(f"Hilo/Proceso {threading.current_thread().name} o {multiprocessing.current_process().name}: "
                    f"Error de integridad (posible duplicado) al intentar insertar reseña: {e}")
                return False
            except Exception as e:
                print(f"Hilo/Proceso {threading.current_thread().name} o {multiprocessing.current_process().name}: "
                    f"Error inesperado al enviar reseña: {e}")
                return False

    def obtener_detalles_juego_con_reseñas(self, id_juego):
        juego_obj = self.obtener_juego_por_id(id_juego)
        if not juego_obj:
            return None, []
        
        reseñas_obj = []
        reseñas_raw = self.reseña_dao.obtener_reseñas_por_juego(id_juego)
        for r in reseñas_raw:
            reseñas_obj.append(self._mapear_datos_a_objeto(r, Reseña))
        
        return juego_obj, reseñas_obj

if __name__ == '__main__':
    from CapaDeDatos.conexion_bd import crear_tablas
    crear_tablas()

    gestor = GestorResenas()

    juego_thewitcher = gestor.obtener_juego_por_nombre("The Witcher 3")
    usuario_normal1 = gestor.obtener_usuario_por_nombre("Usuario Normal 1")
    critico_pro = gestor.obtener_usuario_por_nombre("Critico Pro")
    gamer_x = gestor.obtener_usuario_por_nombre("Gamer X")
    developer_y = gestor.obtener_usuario_por_nombre("Developer Y")
    
    if not (juego_thewitcher and usuario_normal1 and critico_pro and gamer_x and developer_y):
        print("Error: No se pudieron obtener los IDs de juego o usuario para la prueba. Asegúrate de que _inicializar_datos_base() funcione.")
    else:
        id_juego_thewitcher = juego_thewitcher.id_juego
        id_usuario_normal1 = usuario_normal1.id_usuario
        id_critico_pro = critico_pro.id_usuario
        id_gamer_x = gamer_x.id_usuario
        id_developer_y = developer_y.id_usuario

        print(f"\n--- Puntuación inicial de The Witcher 3 ---")
        juego_actual = gestor.obtener_juego_por_id(id_juego_thewitcher)
        if juego_actual:
            print(f"Juego: {juego_actual.nombre}, Puntuación Media: {juego_actual.puntuacion_media:.2f}, Total Reseñas: {juego_actual.total_reseñas}")
        
        print("\n--- SIMULACIÓN DE CONFLICTO (CON LOCKS Y BD UNIQUE CONSTRAINT) ---")
        print("   Intentaremos que el Usuario Normal 1 envíe múltiples reseñas al mismo tiempo para The Witcher 3.")
        print("   Esperamos que SOLO la primera sea aceptada por el control de concurrencia y la BD UNIQUE constraint.")

        def tarea_envio_reseña(id_hilo, id_juego, id_usuario, puntuacion, contenido, gestor_resenas, ip_simulada):
            print(f"HILO {id_hilo}: Intentando enviar reseña para Juego {id_juego} por Usuario {id_usuario} (Puntuación: {puntuacion})...")
            contenido_hilo = f"{contenido} (Desde Hilo {id_hilo})"
            puntuacion_hilo = puntuacion - (id_hilo % 2)

            gestor_resenas.enviar_reseña(
                id_juego=id_juego,
                id_usuario=id_usuario,
                puntuacion=puntuacion_hilo,
                contenido=contenido_hilo,
                origen_simulado_ip=ip_simulada
            )

        print("\n--- SIMULACIÓN CON HILOS ---")
        hilos = []
        num_hilos = 5
        
        print(f"Usuario {usuario_normal1.nombre_usuario} (ID: {id_usuario_normal1}) intenta reseñar '{juego_thewitcher.nombre}'")
        for i in range(num_hilos):
            hilo = threading.Thread(target=tarea_envio_reseña, args=(i+1, id_juego_thewitcher, id_usuario_normal1, 7, f"Reseña intento {i+1}", gestor, f"192.168.1.{100 + i}"), name=f"Hilo-{i+1}")
            hilos.append(hilo)
            hilo.start()

        for hilo in hilos:
            hilo.join()

        print("\n--- Después de la simulación de HILOS ---")
        juego_final = gestor.obtener_juego_por_id(id_juego_thewitcher)
        if juego_final:
            print(f"Juego: {juego_final.nombre}, Puntuación Media Final: {juego_final.puntuacion_media:.2f}, Total Reseñas Final: {juego_final.total_reseñas}")
            print(f"Puntuación acumulada: {juego_final.puntuacion_acumulada}")
            print("Reseñas registradas para este juego y usuario:")
            reseñas_registradas = gestor.obtener_reseñas_por_juego(juego_thewitcher.id_juego)
            for r in reseñas_registradas:
                if r.id_usuario == usuario_normal1.id_usuario: 
                    print(f"    - Reseña ID: {r.id_reseña}, Puntuación: {r.puntuacion}, Contenido: '{r.contenido}', Usuario ID: {r.id_usuario}")

        print("\n--- SIMULACIÓN CON PROCESOS (Usando la protección de la BD) ---")
        print("   Intentaremos que el Crítico Pro envíe múltiples reseñas al mismo tiempo para Cyberpunk 2077.")
        print("   Aunque los procesos no comparten locks de hilos, la restricción UNIQUE de la BD prevendrá duplicados.")
        
        juego_cyberpunk = gestor.obtener_juego_por_nombre("Cyberpunk 2077")
        if not juego_cyberpunk:
            print("Error: No se encontró Cyberpunk 2077 para la prueba de procesos.")
        else:
            id_juego_cyberpunk = juego_cyberpunk.id_juego
            
            print(f"Usuario {critico_pro.nombre_usuario} (ID: {id_critico_pro}) intenta reseñar '{juego_cyberpunk.nombre}'")
            
            procesos = []
            num_procesos = 3

            def tarea_envio_reseña_proceso_consola(id_proceso, id_juego, id_usuario, puntuacion_base, contenido_base, ip_base):
                from CapaLogicaDeNegocio.gestor_resenas import GestorResenas
                gestor_local = GestorResenas()
                
                puntuacion_intento = puntuacion_base + (id_proceso % 2)
                contenido_intento = f"{contenido_base} (Desde Proceso {id_proceso})"
                ip_intento = f"{ip_base}.{id_proceso}"

                print(f"PROCESO {id_proceso}: Intentando enviar reseña para Juego {id_juego} por Usuario {id_usuario} (Puntuación: {puntuacion_intento})...")
                gestor_local.enviar_reseña(
                    id_juego=id_juego,
                    id_usuario=id_usuario,
                    puntuacion=puntuacion_intento,
                    contenido=contenido_intento,
                    origen_simulado_ip=ip_intento
                )

            for i in range(num_procesos):
                proceso = multiprocessing.Process(
                    target=tarea_envio_reseña_proceso_consola,
                    args=(i+1, id_juego_cyberpunk, id_critico_pro, 8, "Reseña de proceso simulada", "10.0.0.1"),
                    name=f"Proceso-{i+1}"
                )
                procesos.append(proceso)
                proceso.start()

            for proceso in procesos:
                proceso.join()

            print("\n--- Simulación con PROCESOS finalizada ---")
            juego_final = gestor.obtener_juego_por_id(id_juego_cyberpunk)
            if juego_final:
                print(f"Estado Final del Juego '{juego_final.nombre}':")
                print(f"  Puntuación Media: {juego_final.puntuacion_media:.2f}")
                print(f"  Total de Reseñas: {juego_final.total_reseñas}")
                print("  Reseñas registradas para este juego y usuario:")
                reseñas_registradas = gestor.obtener_reseñas_por_juego(juego_cyberpunk.id_juego)
                for r in reseñas_registradas:
                    if r.id_usuario == critico_pro.id_usuario: 
                        print(f"    - Reseña ID: {r.id_reseña}, Puntuación: {r.puntuacion}, Contenido: '{r.contenido}', Usuario ID: {r.id_usuario}")

        print("\n--- Añadiendo reseñas normales a The Witcher 3 para ver el promedio ---")
        gestor.enviar_reseña(id_juego_thewitcher, id_critico_pro, 9, "Un clásico atemporal!")
        gestor.enviar_reseña(id_juego_thewitcher, id_gamer_x, 6, "Bueno, pero no me enganchó.", "172.16.0.5")
        gestor.enviar_reseña(id_juego_thewitcher, id_developer_y, 9, "Técnicamente impresionante.", "10.10.10.1")

        time.sleep(0.5)

        juego_thewitcher_final_final = gestor.obtener_juego_por_id(id_juego_thewitcher)
        print(f"\n--- Estado final de The Witcher 3 (después de todas las operaciones) ---")
        if juego_thewitcher_final_final:
            print(f"Juego: {juego_thewitcher_final_final.nombre}, Puntuación Media: {juego_thewitcher_final_final.puntuacion_media:.2f}, Total Reseñas: {juego_thewitcher_final_final.total_reseñas}")
            print("Reseñas detalladas:")
            reseñas_detalles = gestor.obtener_reseñas_por_juego(id_juego_thewitcher)
            for r in reseñas_detalles:
                usuario_reseña = gestor.obtener_usuario_por_id(r.id_usuario)
                nombre_usuario = usuario_reseña.nombre_usuario if usuario_reseña else "Desconocido"
                print(f"  - Usuario: {nombre_usuario}, Puntuación: {r.puntuacion} - '{r.contenido}'")