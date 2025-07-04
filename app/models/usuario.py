from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(64), unique=True, index=True)
    correo = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    
    # Relaciones
    ventas = db.relationship('Venta', backref='comprador', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('password no es un atributo legible')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_tickets(self):
        """Obtiene todos los tickets comprados por el usuario"""
        from app.models.venta import Venta
        from app.models.evento import Evento
        from app.models.asiento import Asiento
        
        # Obtener ventas con estado de pago completado
        return Venta.query.filter_by(
            usuario_id=self.id, 
            estado_pago='completado'
        ).order_by(Venta.fecha_compra.desc()).all()
    
    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'id': self.id,
            'nombre_usuario': self.nombre_usuario,
            'correo': self.correo
        }
    
    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
