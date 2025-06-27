import MySQLdb

class Conexion:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.db = "sistema_eventos"

    def obtener_conexion(self):
        """Método para obtener la conexión a la base de datos."""
        conexion = MySQLdb.connect(
            host=self.host,
            user=self.user,
            passwd=self.password,
            db=self.db
        )
        return conexion