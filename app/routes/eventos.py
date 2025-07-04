from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.evento import Evento
from app.models.asiento import Asiento
from flasgger import swag_from

eventos_bp = Blueprint('eventos', __name__, url_prefix='/eventos')

@eventos_bp.route('/')
@swag_from({
    'tags': ['Eventos'],
    'summary': 'Lista de eventos',
    'description': 'Muestra la lista de todos los eventos disponibles',
    'responses': {
        '200': {
            'description': 'Lista de eventos'
        }
    }
})
def lista():
    eventos = Evento.query.all()
    return render_template('eventos/lista.html', eventos=eventos)

@eventos_bp.route('/<int:evento_id>')
@swag_from({
    'tags': ['Eventos'],
    'summary': 'Detalle de evento',
    'description': 'Muestra los detalles de un evento específico',
    'parameters': [
        {
            'name': 'evento_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del evento'
        }
    ],
    'responses': {
        '200': {
            'description': 'Detalle del evento'
        },
        '404': {
            'description': 'Evento no encontrado'
        }
    }
})
def detalle(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    return render_template('eventos/detalle.html', evento=evento)

@eventos_bp.route('/<int:evento_id>/asientos')
@login_required
@swag_from({
    'tags': ['Eventos'],
    'summary': 'Selección de asientos',
    'description': 'Muestra la interfaz para seleccionar asientos para un evento',
    'parameters': [
        {
            'name': 'evento_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del evento'
        }
    ],
    'responses': {
        '200': {
            'description': 'Interfaz de selección de asientos'
        },
        '404': {
            'description': 'Evento no encontrado'
        }
    }
})
def asientos(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    asientos = Asiento.query.filter_by(evento_id=evento_id).all()
    
    # Organizar asientos por filas para facilitar la visualización
    asientos_por_fila = {}
    for asiento in asientos:
        if asiento.fila not in asientos_por_fila:
            asientos_por_fila[asiento.fila] = []
        asientos_por_fila[asiento.fila].append(asiento)
    
    # Ordenar asientos por número dentro de cada fila
    for fila in asientos_por_fila:
        asientos_por_fila[fila] = sorted(asientos_por_fila[fila], key=lambda x: x.numero_asiento)
    
    # Ordenar las filas
    filas_ordenadas = sorted(asientos_por_fila.keys())
    
    return render_template('eventos/asientos.html', 
                           evento=evento, 
                           asientos_por_fila=asientos_por_fila,
                           filas_ordenadas=filas_ordenadas)

@eventos_bp.route('/api/asiento/<int:asiento_id>/estado')
@login_required
@swag_from({
    'tags': ['API'],
    'summary': 'Verificar estado de asiento',
    'description': 'Verifica el estado actual de un asiento específico',
    'parameters': [
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
            'description': 'Estado del asiento',
            'content': {
                'application/json': {}
            }
        },
        '404': {
            'description': 'Asiento no encontrado'
        }
    }
})
def verificar_estado_asiento(asiento_id):
    asiento = Asiento.query.get_or_404(asiento_id)
    return jsonify({
        'id': asiento.id,
        'estado': asiento.estado,
        'disponible': asiento.estado == 'disponible'
    })

# API Endpoints
@eventos_bp.route('/api/eventos')
@swag_from({
    'tags': ['API'],
    'summary': 'API de eventos',
    'description': 'Retorna la lista de eventos en formato JSON',
    'responses': {
        '200': {
            'description': 'Lista de eventos',
            'content': {
                'application/json': {}
            }
        }
    }
})
def api_eventos():
    eventos = Evento.query.all()
    return jsonify([{
        'id': e.id,
        'nombre': e.nombre,
        'descripcion': e.descripcion,
        'fecha': e.fecha.strftime('%Y-%m-%d'),
        'hora': e.hora.strftime('%H:%M'),
        'ubicacion': e.ubicacion,
        'imagen': e.imagen,
        'capacidad': e.capacidad
    } for e in eventos])

@eventos_bp.route('/api/eventos/<int:evento_id>')
@swag_from({
    'tags': ['API'],
    'summary': 'API de detalle de evento',
    'description': 'Retorna los detalles de un evento específico en formato JSON',
    'parameters': [
        {
            'name': 'evento_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del evento'
        }
    ],
    'responses': {
        '200': {
            'description': 'Detalle del evento',
            'content': {
                'application/json': {}
            }
        },
        '404': {
            'description': 'Evento no encontrado'
        }
    }
})
def api_evento_detalle(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    return jsonify({
        'id': evento.id,
        'nombre': evento.nombre,
        'descripcion': evento.descripcion,
        'fecha': evento.fecha.strftime('%Y-%m-%d'),
        'hora': evento.hora.strftime('%H:%M'),
        'ubicacion': evento.ubicacion,
        'imagen': evento.imagen,
        'capacidad': evento.capacidad
    })

@eventos_bp.route('/api/eventos/<int:evento_id>/asientos')
@swag_from({
    'tags': ['API'],
    'summary': 'API de asientos de evento',
    'description': 'Retorna la lista de asientos para un evento específico en formato JSON',
    'parameters': [
        {
            'name': 'evento_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del evento'
        }
    ],
    'responses': {
        '200': {
            'description': 'Lista de asientos',
            'content': {
                'application/json': {}
            }
        },
        '404': {
            'description': 'Evento no encontrado'
        }
    }
})
def api_asientos(evento_id):
    asientos = Asiento.query.filter_by(evento_id=evento_id).all()
    return jsonify([{
        'id': a.id,
        'fila': a.fila,
        'numero_asiento': a.numero_asiento,
        'estado': a.estado,
        'precio': a.precio,
        'posicion_x': a.posicion_x,
        'posicion_y': a.posicion_y,
        'tipo': a.tipo
    } for a in asientos])
