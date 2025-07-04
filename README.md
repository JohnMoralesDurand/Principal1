# ArteVivo - Sistema de Venta de Entradas

ArteVivo es una plataforma para la venta de entradas a eventos culturales y artísticos. Permite a los usuarios registrarse, iniciar sesión, explorar eventos, seleccionar asientos y comprar entradas de forma segura utilizando Stripe como procesador de pagos.

## Características

- Registro y autenticación de usuarios
- Exploración de eventos disponibles
- Selección visual de asientos
- Procesamiento de pagos con Stripe
- Generación y descarga de tickets
- Historial de compras para usuarios

## Requisitos

- Python 3.8+
- Flask
- SQLAlchemy
- Stripe API

## Configuración

1. Clonar el repositorio:

```bash
git clone https://github.com/yourusername/artevivo.git
cd artevivo
```

2. Crear y activar un entorno virtual:

```bash
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
SECRET_KEY=tu_clave_secreta_aqui
DATABASE_URL=sqlite:///artevivo.db
DEBUG=True

# Stripe API Keys
STRIPE_PUBLISHABLE_KEY=pk_test_tu_clave_publicable_de_stripe
STRIPE_SECRET_KEY=sk_test_tu_clave_secreta_de_stripe
STRIPE_WEBHOOK_SECRET=whsec_tu_clave_webhook_de_stripe
STRIPE_BUY_BUTTON_ID=buy_btn_tu_id_de_boton_de_compra
```

5. Inicializar la base de datos:

```bash
python -m flask db upgrade
```

6. Ejecutar la aplicación:

```bash
python -m flask run
```

## Integración con Stripe

Esta aplicación utiliza Stripe para procesar pagos. Para configurar Stripe:

1. Crea una cuenta en [Stripe](https://stripe.com)
2. Obtén tus claves API desde el Dashboard de Stripe
3. Configura un Webhook para recibir notificaciones de pagos completados
4. Crea un botón de compra en Stripe y obtén su ID

## Seguridad

La aplicación implementa las siguientes medidas de seguridad:

- Protección CSRF en todos los formularios
- Autenticación de usuarios con Flask-Login
- Contraseñas hasheadas
- Validación de datos de entrada
- Manejo seguro de pagos con Stripe