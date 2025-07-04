from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flasgger import Swagger
from app.config import Config
import stripe

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
swagger = Swagger()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    swagger.init_app(app)
    
    # Configurar Stripe
    stripe.api_key = app.config.get('STRIPE_SECRET_KEY')
    
    # Añadir context processor global para la variable now
    @app.context_processor
    def inject_now():
        import datetime
        return {'now': datetime.datetime.now()}
    
    # Añadir context processor para Stripe
    @app.context_processor
    def inject_stripe_key():
        return {'stripe_public_key': app.config.get('STRIPE_PUBLIC_KEY')}
    
    # Configurar login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    
    # Registrar blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.eventos import eventos_bp
    from app.routes.tickets import tickets_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(eventos_bp)
    app.register_blueprint(tickets_bp)
    
    return app
