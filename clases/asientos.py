from clases.conexion import Conexion

class Asientos:
    def __init__(self):
        self.conexion = Conexion()

    def obtener_asientos_disponibles(self, evento_id):
        """Obtiene los asientos disponibles para un evento específico."""
        conexion_local = self.conexion.obtener_conexion()
        cursor = conexion_local.cursor()
        cursor.execute("""
            SELECT * FROM asientos WHERE evento_id = %s AND estado = 'disponible'
        """, (evento_id,))
        asientos = cursor.fetchall()
        conexion_local.close()
        return asientos

    def marcar_asiento_vendido(self, asiento_id):
        """Marca un asiento como 'vendido' en la base de datos."""
        conexion_local = self.conexion.obtener_conexion()
        cursor = conexion_local.cursor()
        cursor.execute("""
            UPDATE asientos SET estado = 'vendido' WHERE id = %s
        """, (asiento_id,))
        conexion_local.commit()
        conexion_local.close()