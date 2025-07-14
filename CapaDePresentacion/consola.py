import time
import threading
import multiprocessing

def _tarea_envio_reseña_hilos_target(id_hilo, id_juego, id_usuario, puntuacion, contenido, gestor_resenas, ip_simulada):
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

def _tarea_envio_reseña_procesos_target(id_proceso, id_juego, id_usuario, puntuacion_base, contenido_base, ip_base):
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

#Fin de funciones auxiliares


class InterfazConsola:
    def __init__(self, gestor_resenas):
        self.gestor = gestor_resenas

    def _limpiar_pantalla(self):
        print("\n" * 5) # Simula una limpieza imprimiendo varias líneas en blanco

    def _pausar(self):
        input("\nPresiona Enter para continuar...")

    def mostrar_menu_principal(self):
        self._limpiar_pantalla()
        print("█████████████████████████████████████████")
        print("█  APLICACIÓN DE RESEÑAS DE VIDEOJUEGOS █")
        print("█████████████████████████████████████████")
        print("\nOpciones:")
        print("1. Ver juegos disponibles y sus puntuaciones")
        print("2. Enviar una reseña")
        print("3. Simular conflicto de concurrencia (Hilos)")
        print("4. Simular conflicto de concurrencia (Procesos)")
        print("5. Salir")
        print("█████████████████████████████████████████")

    def ejecutar(self):
        while True:
            self.mostrar_menu_principal()
            opcion = input("Selecciona una opción: ")

            if opcion == '1':
                self.ver_juegos_y_puntuaciones()
            elif opcion == '2':
                self.enviar_reseña_interactivo()
            elif opcion == '3':
                self.simular_hilos_concurrencia()
            elif opcion == '4':
                self.simular_procesos_concurrencia()
            elif opcion == '5':
                print("Saliendo de la aplicación. ¡Hasta luego!")
                break
            else:
                print("Opción no válida. Por favor, intenta de nuevo.")
            
            if opcion != '5':
                self._pausar()


    def ver_juegos_y_puntuaciones(self):
        self._limpiar_pantalla()
        print("--- JUEGOS DISPONIBLES Y SUS PUNTUACIONES ---")
        juegos = self.gestor.obtener_juegos()

        if not juegos:
            print("No hay juegos registrados en el sistema.")
            return

        for juego in juegos:
            print(f"\nID: {juego.id_juego}")
            print(f"Nombre: {juego.nombre}")
            print(f"Descripción: {juego.descripcion}")
            print(f"Puntuación Media: {juego.puntuacion_media:.2f} / 10")
            print(f"Total de Reseñas: {juego.total_reseñas}")
            print("--------------------")
        
        id_juego_ver = input("\n¿Quieres ver las reseñas de un juego en específico? (Ingresa ID o 'no'): ").strip().lower()
        if id_juego_ver != 'no':
            try:
                id_juego_ver = int(id_juego_ver)
                juego_obj, reseñas_obj = self.gestor.obtener_detalles_juego_con_reseñas(id_juego_ver)
                if juego_obj:
                    print(f"\n--- Reseñas para {juego_obj.nombre} ---")
                    if reseñas_obj:
                        for reseña in reseñas_obj:
                            usuario = self.gestor.obtener_usuario_por_id(reseña.id_usuario)
                            nombre_usuario = usuario.nombre_usuario if usuario else "Desconocido"
                            print(f"  - Usuario: {nombre_usuario}, Puntuación: {reseña.puntuacion}/10, Contenido: '{reseña.contenido}', Fecha: {reseña.fecha_reseña}")
                    else:
                        print("No hay reseñas para este juego aún.")
                else:
                    print("Juego no encontrado.")
            except ValueError:
                print("ID de juego no válido.")


    def enviar_reseña_interactivo(self):
        self._limpiar_pantalla()
        print("--- ENVIAR NUEVA RESEÑA ---")
        
        # Mostrar usuarios disponibles
        print("\nUsuarios disponibles:")
        usuarios = self.gestor.obtener_usuarios()
        if not usuarios:
            print("No hay usuarios registrados. Por favor, contacta al administrador.")
            return
        for u in usuarios:
            print(f"ID: {u.id_usuario}, Nombre: {u.nombre_usuario} ({u.tipo_usuario})")

        try:
            id_usuario = int(input("Ingresa el ID de tu usuario: "))
            usuario_obj = self.gestor.obtener_usuario_por_id(id_usuario)
            if not usuario_obj:
                print("ID de usuario no válido.")
                return

            # Mostrar juegos disponibles
            print("\nJuegos disponibles:")
            juegos = self.gestor.obtener_juegos()
            if not juegos:
                print("No hay juegos registrados. Por favor, contacta al administrador.")
                return
            for j in juegos:
                print(f"ID: {j.id_juego}, Nombre: {j.nombre} (Media: {j.puntuacion_media:.2f})")

            id_juego = int(input("Ingresa el ID del juego a reseñar: "))
            juego_obj = self.gestor.obtener_juego_por_id(id_juego)
            if not juego_obj:
                print("ID de juego no válido.")
                return

            puntuacion = int(input("Ingresa tu puntuación (1-10): "))
            if not (1 <= puntuacion <= 10):
                print("Puntuación fuera del rango válido (1-10).")
                return

            contenido = input("Escribe tu reseña (opcional): ")
            origen_ip = input("Ingresa IP simulada (opcional, ej: 192.168.1.1): ")

            print("\nIntentando enviar reseña...")
            exito = self.gestor.enviar_reseña(
                id_juego=id_juego,
                id_usuario=id_usuario,
                puntuacion=puntuacion,
                contenido=contenido,
                origen_simulado_ip=origen_ip
            )

            if exito:
                print("\nReseña enviada exitosamente.")
            else:
                print("\nNo se pudo enviar la reseña. Revisa los mensajes anteriores para más detalles.")

        except ValueError:
            print("Entrada no válida. Por favor, ingresa un número para los IDs y la puntuación.")
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")

    # Simulación de concurrencia

    def simular_hilos_concurrencia(self):
        self._limpiar_pantalla()
        print("--- SIMULACIÓN DE CONFLICTO DE CONCURRENCIA (HILOS) ---")
        print("\nEste escenario simula a un USUARIO intentando enviar MÚLTIPLES RESEÑAS al mismo juego al mismo tiempo.")
        print("La base de datos (con UNIQUE constraint) y la lógica de negocio (con locks) DEBEN prevenir los duplicados.")

        juegos = self.gestor.obtener_juegos()
        if not juegos:
            print("No hay juegos para simular. Crea algunos primero.")
            return
        juego_simulacion = juegos[0] 
        
        usuarios = self.gestor.obtener_usuarios()
        if not usuarios:
            print("No hay usuarios para simular. Crea algunos primero.")
            return
        usuario_simulacion = None
        for u in usuarios:
            if u.tipo_usuario == 'usuario_normal':
                usuario_simulacion = u
                break
        if not usuario_simulacion:
            usuario_simulacion = usuarios[0]
        
        print(f"\nJuego para simular: {juego_simulacion.nombre} (ID: {juego_simulacion.id_juego})")
        print(f"Usuario para simular: {usuario_simulacion.nombre_usuario} (ID: {usuario_simulacion.id_usuario})")
        print(f"Puntuación inicial del juego: {juego_simulacion.puntuacion_media:.2f} (Total reseñas: {juego_simulacion.total_reseñas})")

        num_hilos = 5
        print(f"\nCreando {num_hilos} hilos para que el usuario '{usuario_simulacion.nombre_usuario}' intente reseñar el juego '{juego_simulacion.nombre}' simultáneamente...")

        hilos = []
        for i in range(num_hilos):
            puntuacion_intento = 7 + (i % 3)
            contenido_intento = f"Reseña simulada (Intento {i+1}) desde IP 192.168.1.{100+i}"
            hilo = threading.Thread(
                target=_tarea_envio_reseña_hilos_target,
                args=(i+1, juego_simulacion.id_juego, usuario_simulacion.id_usuario, puntuacion_intento, contenido_intento, self.gestor, f"192.168.1.{100+i}"),
                name=f"Hilo-{i+1}"
            )
            hilos.append(hilo)
            hilo.start()

        for hilo in hilos:
            hilo.join()

        print("\n--- Simulación con HILOS finalizada ---")
        juego_final = self.gestor.obtener_juego_por_id(juego_simulacion.id_juego)
        if juego_final:
            print(f"Estado Final del Juego '{juego_final.nombre}':")
            print(f"  Puntuación Media: {juego_final.puntuacion_media:.2f}")
            print(f"  Total de Reseñas: {juego_final.total_reseñas}")
            print("  Reseñas registradas para este juego y usuario (debería ser solo 1):")
            reseñas_registradas = self.gestor.obtener_reseñas_por_juego(juego_simulacion.id_juego)
            for r in reseñas_registradas:
                if r.id_usuario == usuario_simulacion.id_usuario:
                    print(f"    - Reseña ID: {r.id_reseña}, Puntuación: {r.puntuacion}, Contenido: '{r.contenido}', Usuario ID: {r.id_usuario}")
        else:
            print("No se pudo obtener el estado final del juego.")

    def simular_procesos_concurrencia(self):
        self._limpiar_pantalla()
        print("--- SIMULACIÓN DE CONFLICTO DE CONCURRENCIA (PROCESOS) ---")
        print("\nEste escenario simula a VARIOS PROCESOS intentando que un mismo USUARIO envíe reseñas al mismo juego al mismo tiempo.")
        print("Los procesos no comparten locks de memoria, pero la restricción UNIQUE de la BD es la protección final.")

        juegos = self.gestor.obtener_juegos()
        if not juegos:
            print("No hay juegos para simular. Crea algunos primero.")
            return
        juego_simulacion = juegos[1] if len(juegos) > 1 else juegos[0] 
        
        usuarios = self.gestor.obtener_usuarios()
        if not usuarios:
            print("No hay usuarios para simular. Crea algunos primero.")
            return
        usuario_simulacion = None
        for u in usuarios:
            if u.tipo_usuario == 'critico':
                usuario_simulacion = u
                break
        if not usuario_simulacion:
            usuario_simulacion = usuarios[1] if len(usuarios) > 1 else usuarios[0]
            
        print(f"\nJuego para simular: {juego_simulacion.nombre} (ID: {juego_simulacion.id_juego})")
        print(f"Usuario para simular: {usuario_simulacion.nombre_usuario} (ID: {usuario_simulacion.id_usuario})")
        print(f"Puntuación inicial del juego: {juego_simulacion.puntuacion_media:.2f} (Total reseñas: {juego_simulacion.total_reseñas})")

        num_procesos = 3
        print(f"\nCreando {num_procesos} procesos para que el usuario '{usuario_simulacion.nombre_usuario}' intente reseñar el juego '{juego_simulacion.nombre}' simultáneamente...")

        procesos = []
        for i in range(num_procesos):
            proceso = multiprocessing.Process(
                target=_tarea_envio_reseña_procesos_target, # Ahora usa la función global
                args=(i+1, juego_simulacion.id_juego, usuario_simulacion.id_usuario, 8, "Reseña de proceso simulada", "10.0.0.1"),
                name=f"Proceso-{i+1}"
            )
            procesos.append(proceso)
            proceso.start()

        for proceso in procesos:
            proceso.join()

        print("\n--- Simulación con PROCESOS finalizada ---")
        juego_final = self.gestor.obtener_juego_por_id(juego_simulacion.id_juego)
        if juego_final:
            print(f"Estado Final del Juego '{juego_final.nombre}':")
            print(f"  Puntuación Media: {juego_final.puntuacion_media:.2f}")
            print(f"  Total de Reseñas: {juego_final.total_reseñas}")
            print("  Reseñas registradas para este juego y usuario (debería ser solo 1):")
            reseñas_registradas = self.gestor.obtener_reseñas_por_juego(juego_simulacion.id_juego)
            for r in reseñas_registradas:
                if r.id_usuario == usuario_simulacion.id_usuario:
                    print(f"    - Reseña ID: {r.id_reseña}, Puntuación: {r.puntuacion}, Contenido: '{r.contenido}', Usuario ID: {r.id_usuario}")
        else:
            print("No se pudo obtener el estado final del juego.")