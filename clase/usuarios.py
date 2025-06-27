from clases.conexion import Conexion

class Usuarios:
    def __init__(self):
        self.conexion = Conexion()

    def registrar_usuario(self, nombre_usuario, correo, contrasena):
        """Registra un nuevo usuario en la base de datos."""
        conexion_local = self.conexion.obtener_conexion()
        cursor = conexion_local.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nombre_usuario, correo, contrasena)
            VALUES (%s, %s, %s)
        """, (nombre_usuario, correo, contrasena))
        conexion_local.commit()
        conexion_local.close()

    def verificar_usuario(self, correo, contrasena):
        """Verifica si un usuario existe en la base de datos."""
        conexion_local = self.conexion.obtener_conexion()
        cursor = conexion_local.cursor()
        cursor.execute("""
            SELECT * FROM usuarios WHERE correo = %s AND contrasena = %s
        """, (correo, contrasena))
        usuario = cursor.fetchone()
        conexion_local.close()
        return usuario