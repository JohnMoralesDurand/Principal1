from datetime import datetime
from app import db

class Evento(db.Model):
    __tablename__ = 'eventos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    lugar = db.Column(db.String(255), nullable=False)
    imagen = db.Column(db.String(255), nullable=True)  # URL o ruta a la imagen del evento
    capacidad = db.Column(db.Integer, default=30)  # Capacidad total del evento (30 asientos por defecto)
    
    # Relaciones
    asientos = db.relationship('Asiento', backref='evento', lazy='dynamic', cascade='all, delete-orphan')
    ventas = db.relationship('Venta', backref='evento_relacionado', lazy='dynamic')
    
    def __repr__(self):
        return f'<Evento {self.nombre}>'
    
    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'hora': self.hora.isoformat() if self.hora else None,
            'lugar': self.lugar,
            'imagen': self.imagen,
            'capacidad': self.capacidad,
            'asientos_disponibles': self.asientos.filter_by(estado='disponible').count()
        }
