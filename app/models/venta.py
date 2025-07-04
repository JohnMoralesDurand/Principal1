from datetime import datetime
from app import db

class Venta(db.Model):
    __tablename__ = 'ventas'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    asiento_id = db.Column(db.Integer, db.ForeignKey('asientos.id'), nullable=False)
    fecha_compra = db.Column(db.DateTime, default=datetime.utcnow)
    precio = db.Column(db.Float, nullable=False)
    codigo_ticket = db.Column(db.String(50), unique=True, nullable=False)
    estado_pago = db.Column(db.String(20), default='pendiente')  # pendiente, completado, cancelado
    stripe_payment_intent_id = db.Column(db.String(100), nullable=True)  # ID del intento de pago en Stripe
    stripe_payment_status = db.Column(db.String(50), nullable=True)  # Estado del pago en Stripe
    
    def __repr__(self):
        return f'<Venta {self.id} - {self.codigo_ticket}>'
    
    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'evento_id': self.evento_id,
            'asiento_id': self.asiento_id,
            'fecha_compra': self.fecha_compra.isoformat() if self.fecha_compra else None,
            'precio': self.precio,
            'codigo_ticket': self.codigo_ticket,
            'estado_pago': self.estado_pago,
            'stripe_payment_status': self.stripe_payment_status
        }
