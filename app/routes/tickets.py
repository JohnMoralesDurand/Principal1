import uuid
import stripe
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app import db, csrf
from app.models.evento import Evento
from app.models.asiento import Asiento
from app.models.venta import Venta
from app.models.usuario import Usuario
from app.services.ticket_service import generar_ticket_pdf
from app.services.payment_service import crear_sesion_checkout, verificar_estado_pago, webhook_handler, generar_codigo_ticket
from flasgger import swag_from

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')

@tickets_bp.route('/comprar/<int:evento_id>/<int:asiento_id>', methods=['POST'])
@login_required
@swag_from({
    'tags': ['Compras'],
    'summary': 'Comprar entrada',
    'description': 'Permite comprar una entrada para un evento',
    'parameters': [
        {
            'name': 'evento_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del evento'
        },
        {
            'name': 'asiento_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del asiento'
        }
    ],
    'responses': {
        '200': {
            'description': 'Compra exitosa'
        },
        '400': {
            'description': 'Error en la compra'
        },
        '404': {
            'description': 'Evento o asiento no encontrado'
        }
    }
})
def comprar(evento_id, asiento_id):
    # El CSRF token es validado automáticamente por Flask-WTF
        
    evento = Evento.query.get_or_404(evento_id)
    asiento = Asiento.query.get_or_404(asiento_id)
    
    if asiento.estado != 'disponible':
        flash('El asiento seleccionado ya no está disponible', 'danger')
        return redirect(url_for('eventos.asientos', evento_id=evento_id))
    
    # Marcar asiento como reservado temporalmente
    asiento.estado = 'reservado'
    
    # Generar código único para el ticket
    codigo_ticket = generar_codigo_ticket()
    
    # Registrar la venta con estado pendiente
    nueva_venta = Venta(
        usuario_id=current_user.id,
        evento_id=evento_id,
        asiento_id=asiento_id,
        precio=asiento.precio,
        codigo_ticket=codigo_ticket,
        estado_pago='pendiente'
    )
    
    db.session.add(nueva_venta)
    db.session.commit()
    
    # Crear sesión de checkout en Stripe
    checkout_result = crear_sesion_checkout(nueva_venta, evento, asiento)
    
    if 'error' in checkout_result:
        # Si hay error, revertir la reserva
        asiento.estado = 'disponible'
        db.session.delete(nueva_venta)
        db.session.commit()
        flash(f"Error al crear la sesión de pago: {checkout_result['error']}", 'danger')
        return redirect(url_for('eventos.asientos', evento_id=evento_id))
    
    # Guardar el ID de la sesión de checkout en la venta
    nueva_venta.stripe_payment_intent_id = checkout_result['id']
    db.session.commit()
    
    # Redirigir al usuario a la página de checkout de Stripe
    return redirect(checkout_result['url'])

@tickets_bp.route('/confirmacion/<int:venta_id>')
@login_required
@swag_from({
    'tags': ['Compras'],
    'summary': 'Confirmación de compra',
    'description': 'Muestra la confirmación de una compra exitosa',
    'parameters': [
        {
            'name': 'venta_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la venta'
        }
    ],
    'responses': {
        '200': {
            'description': 'Confirmación exitosa'
        },
        '404': {
            'description': 'Venta no encontrada'
        }
    }
})
def confirmacion(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    
    # Verificar que el usuario actual es el propietario de la venta
    if venta.usuario_id != current_user.id:
        flash('No tienes permiso para ver esta información', 'danger')
        return redirect(url_for('eventos.lista'))
    
    evento = Evento.query.get(venta.evento_id)
    asiento = Asiento.query.get(venta.asiento_id)
    
    # Verificar el estado del pago si está pendiente
    if venta.estado_pago == 'pendiente' and venta.stripe_payment_intent_id:
        payment_status = verificar_estado_pago(venta.stripe_payment_intent_id)
        
        if 'error' not in payment_status:
            if payment_status.get('success', False):
                # Actualizar el estado de la venta y del asiento
                venta.estado_pago = 'completado'
                venta.stripe_payment_status = payment_status.get('status')
                asiento.estado = 'vendido'
                db.session.commit()
            elif payment_status.get('status') != 'pending':
                # Si el pago falló (no está pendiente ni exitoso)
                venta.stripe_payment_status = payment_status.get('status')
                db.session.commit()
    
    # Si el pago no está completado, redirigir a la página de pago pendiente
    if venta.estado_pago != 'completado':
        return render_template('compra/pago_pendiente.html', venta=venta, evento=evento, asiento=asiento)
    
    return render_template('compra/confirmacion.html', venta=venta, evento=evento, asiento=asiento)

@tickets_bp.route('/mis-tickets')
@login_required
def mis_tickets():
    """Muestra los tickets comprados por el usuario"""
    tickets = current_user.get_tickets()
    return render_template('tickets/mis_tickets.html', tickets=tickets)

@tickets_bp.route('/descargar/<int:venta_id>')
@login_required
@swag_from({
    'tags': ['Tickets'],
    'summary': 'Descargar ticket',
    'description': 'Permite descargar el ticket en formato PDF',
    'parameters': [
        {
            'name': 'venta_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la venta'
        }
    ],
    'responses': {
        '200': {
            'description': 'PDF del ticket',
            'content': {
                'application/pdf': {}
            }
        },
        '404': {
            'description': 'Venta no encontrada'
        }
    }
})
def descargar_ticket(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    
    # Verificar que el usuario actual es el propietario de la venta
    if venta.usuario_id != current_user.id:
        flash('No tienes permiso para ver esta información', 'danger')
        return redirect(url_for('eventos.lista'))
    
    # Verificar que el pago está completado
    if venta.estado_pago != 'completado':
        flash('El ticket no está disponible porque el pago no ha sido completado', 'warning')
        return redirect(url_for('tickets.confirmacion', venta_id=venta_id))
    
    evento = Evento.query.get(venta.evento_id)
    asiento = Asiento.query.get(venta.asiento_id)
    
    # Generar el PDF del ticket
    pdf_path = generar_ticket_pdf(venta, evento, asiento, current_user)
    
    return send_file(pdf_path, as_attachment=True, download_name=f"ticket_{venta.codigo_ticket}.pdf")

@tickets_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Endpoint para recibir webhooks de Stripe"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    result = webhook_handler(payload, sig_header)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 400
    
    return jsonify(result)

# Funciones auxiliares para Stripe
def crear_sesion_checkout(venta, evento, asiento):
    """Crea una sesión de checkout en Stripe"""
    try:
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        
        # Crear sesión de checkout
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'mxn',
                    'product_data': {
                        'name': f'Entrada para {evento.nombre}',
                        'description': f'Asiento: {asiento.fila}{asiento.numero_asiento} - {evento.fecha.strftime("%d/%m/%Y %H:%M")}',
                        'images': [evento.imagen_url] if evento.imagen_url else [],
                    },
                    'unit_amount': int(asiento.precio * 100),  # Stripe usa centavos
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.host_url.rstrip('/') + 
                url_for('tickets.confirmacion', venta_id=venta.id, _external=True),
            cancel_url=request.host_url.rstrip('/') + 
                url_for('eventos.asientos', evento_id=evento.id, _external=True),
            client_reference_id=str(venta.id),
            customer_email=current_user.correo,
            metadata={
                'venta_id': venta.id,
                'evento_id': evento.id,
                'asiento_id': asiento.id,
                'usuario_id': current_user.id
            }
        )
        
        return {
            'id': checkout_session.id,
            'url': checkout_session.url
        }
        
    except Exception as e:
        return {'error': str(e)}

def verificar_estado_pago(session_id):
    """Verifica el estado de un pago en Stripe"""
    try:
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Verificar si el pago fue exitoso
        payment_status = checkout_session.payment_status
        success = payment_status == 'paid'
        
        return {
            'success': success,
            'status': payment_status
        }
        
    except Exception as e:
        return {'error': str(e)}

def webhook_handler(payload, signature):
    """Maneja los webhooks de Stripe"""
    try:
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        webhook_secret = current_app.config['STRIPE_WEBHOOK_SECRET']
        
        # Verificar la firma del webhook
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
        
        # Manejar diferentes tipos de eventos
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            venta_id = session.get('client_reference_id')
            
            if venta_id:
                venta = Venta.query.get(int(venta_id))
                if venta:
                    # Actualizar el estado de la venta
                    venta.estado_pago = 'completado'
                    venta.stripe_payment_status = 'paid'
                    
                    # Actualizar el estado del asiento
                    asiento = Asiento.query.get(venta.asiento_id)
                    if asiento:
                        asiento.estado = 'vendido'
                    
                    db.session.commit()
        
        return {'success': True}
        
    except Exception as e:
        return {'error': str(e)}
