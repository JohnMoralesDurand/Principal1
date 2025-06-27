from clases.conexion import Conexion

class Eventos:
    def __init__(self):
        self.conexion = Conexion()
    
    def crear_evento(self, nombre, descripcion, fecha, hora, lugar):
        """Crea un nuevo evento en la base de datos."""
        conexion_local = self.conexion.obtener_conexion()
        cursor = conexion_local.cursor()
        cursor.execute("""
            INSERT INTO eventos (nombre, descripcion, fecha, hora, lugar)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, descripcion, fecha, hora, lugar))
        conexion_local.commit()
        conexion_local.close()

    def obtener_eventos(self):
        """Obtiene todos los eventos disponibles en la base de datos."""
        conexion_local = self.conexion.obtener_conexion()
        cursor = conexion_local.cursor()
        cursor.execute("SELECT * FROM eventos")
        eventos = cursor.fetchall()
        conexion_local.close()
        return eventos

    def eliminar_evento(self, evento_id):
        """Elimina un evento por su ID."""
        conexion_local = self.conexion.obtener_conexion()
        cursor = conexion_local.cursor()
        cursor.execute("DELETE FROM eventos WHERE id = %s", (evento_id,))
        conexion_local.commit()
        conexion_local.close()