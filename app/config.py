import os
from dotenv import load_dotenv

# Cargar variables de entorno
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-por-defecto'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(basedir), 'artevivo.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de Stripe para pagos
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY') or os.environ.get('STRIPE_PUBLIC_KEY') or 'pk_test_your_stripe_key'
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY') or 'sk_test_your_stripe_key'
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET') or 'whsec_your_stripe_webhook_secret'
    STRIPE_BUY_BUTTON_ID = os.environ.get('STRIPE_BUY_BUTTON_ID') or 'buy_btn_default'
    
    # Configuración de Swagger
    SWAGGER = {
        'title': 'API ArteVivo',
        'uiversion': 3,
        'version': '1.0',
        'description': 'API para la plataforma de venta de entradas ArteVivo',
        'termsOfService': '',
        'hide_top_bar': True
    }
