from app import db

class Asiento(db.Model):
    __tablename__ = 'asientos'
    
    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    fila = db.Column(db.String(10), nullable=False)
    numero_asiento = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(20), default='disponible')  # disponible, reservado, vendido
    precio = db.Column(db.Float, nullable=False, default=0.0)
    posicion_x = db.Column(db.Integer, nullable=False)  # Posición X en el diagrama (columna)
    posicion_y = db.Column(db.Integer, nullable=False)  # Posición Y en el diagrama (fila)
    tipo = db.Column(db.String(20), default='normal')  # normal, vip, discapacitados, etc.
    
    # Relaciones
    ventas = db.relationship('Venta', backref='asiento_relacionado', lazy='dynamic')
    
    def __repr__(self):
        return f'<Asiento {self.fila}{self.numero_asiento} - {self.estado}>'
    
    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'id': self.id,
            'evento_id': self.evento_id,
            'fila': self.fila,
            'numero_asiento': self.numero_asiento,
            'estado': self.estado,
            'precio': self.precio,
            'posicion_x': self.posicion_x,
            'posicion_y': self.posicion_y,
            'tipo': self.tipo
        }
