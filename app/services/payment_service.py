import stripe
from flask import current_app, url_for
import uuid

def crear_sesion_checkout(venta, evento, asiento, success_url=None, cancel_url=None):
    """Crea una sesión de checkout de Stripe para una venta"""
    # Si no se proporcionan URLs, usar las predeterminadas
    if not success_url:
        success_url = url_for('tickets.confirmacion', venta_id=venta.id, _external=True)
    if not cancel_url:
        cancel_url = url_for('eventos.asientos', evento_id=evento.id, _external=True)
    
    try:
        # Crear la sesión de checkout
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'mxn',  # Cambiar según la moneda necesaria
                    'product_data': {
                        'name': f"Entrada para {evento.nombre}",
                        'description': f"Asiento: Fila {asiento.fila}, Número {asiento.numero_asiento}",
                        'images': [evento.imagen] if evento.imagen else [],
                    },
                    'unit_amount': int(asiento.precio * 100),  # Stripe trabaja con centavos
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'venta_id': venta.id,
                'evento_id': evento.id,
                'asiento_id': asiento.id,
                'usuario_id': venta.usuario_id
            },
            client_reference_id=str(venta.id)
        )
        
        return {
            'id': checkout_session.id,
            'url': checkout_session.url,
            'status': 'created'
        }
    except Exception as e:
        return {'error': str(e)}

def verificar_estado_pago(session_id):
    """Verifica el estado de una sesión de checkout"""
    try:
        # Obtener información de la sesión de checkout
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        return {
            'id': checkout_session.id,
            'status': checkout_session.payment_status,
            'success': checkout_session.payment_status == 'paid'
        }
    except Exception as e:
        return {'error': str(e)}

def generar_codigo_ticket():
    """Genera un código único para el ticket"""
    return str(uuid.uuid4().hex)[:10].upper()

def procesar_pago_exitoso(session_id):
    """Procesa un pago exitoso de Stripe"""
    from app import db
    from app.models.venta import Venta
    from app.models.asiento import Asiento
    
    try:
        # Obtener información de la sesión de checkout
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Verificar que el pago esté completado
        if checkout_session.payment_status != 'paid':
            return {'success': False, 'message': 'El pago no está completado'}
        
        # Obtener la venta asociada
        venta_id = int(checkout_session.metadata.get('venta_id'))
        venta = Venta.query.get(venta_id)
        
        if not venta:
            return {'success': False, 'message': 'Venta no encontrada'}
        
        # Actualizar el estado de la venta
        venta.estado_pago = 'completado'
        venta.stripe_payment_status = checkout_session.payment_status
        
        # Actualizar el estado del asiento
        asiento = Asiento.query.get(venta.asiento_id)
        if asiento:
            asiento.estado = 'vendido'
        
        db.session.commit()
        
        return {
            'success': True,
            'venta_id': venta.id,
            'codigo_ticket': venta.codigo_ticket
        }
    except Exception as e:
        return {'error': str(e)}

def webhook_handler(payload, signature):
    """Maneja los webhooks de Stripe"""
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, current_app.config['STRIPE_WEBHOOK_SECRET']
        )
        
        # Manejar diferentes tipos de eventos
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # Procesar el pago completado
            result = procesar_pago_exitoso(session.id)
            return {
                'success': True,
                'session_id': session.id,
                'payment_status': session.payment_status,
                'result': result
            }
        
        return {'success': True, 'event_type': event['type']}
    except Exception as e:
        return {'error': str(e)}
