from CapaDeDatos.conexion_bd import crear_tablas # Importamos para asegurar que la DB esté lista
from CapaLogicaDeNegocio.gestor_resenas import GestorResenas
from CapaDePresentacion.consola import InterfazConsola

def main():
    print("Iniciando la aplicación de reseñas de videojuegos...")
    crear_tablas()
    gestor_resenas = GestorResenas()
    interfaz = InterfazConsola(gestor_resenas)
    interfaz.ejecutar()
    print("Aplicación finalizada.")

if __name__ == '__main__':
    main()