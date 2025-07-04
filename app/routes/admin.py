from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.evento import Evento
from app.models.asiento import Asiento
from app.models.venta import Venta
from app.models.usuario import Usuario
from flasgger import swag_from
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorador para verificar si el usuario es administrador
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.es_admin:
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('eventos.lista'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
@swag_from({
    'tags': ['Administración'],
    'summary': 'Panel de administración',
    'description': 'Muestra el panel principal de administración',
    'responses': {
        '200': {
            'description': 'Panel de administración'
        },
        '401': {
            'description': 'Acceso denegado'
        }
    }
})
def dashboard():
    eventos_count = Evento.query.count()
    ventas_count = Venta.query.count()
    usuarios_count = Usuario.query.count()
    ingresos_total = db.session.query(db.func.sum(Venta.precio)).scalar() or 0
    
    return render_template('admin/dashboard.html', 
                           eventos_count=eventos_count,
                           ventas_count=ventas_count,
                           usuarios_count=usuarios_count,
                           ingresos_total=ingresos_total)

@admin_bp.route('/eventos')
@login_required
@admin_required
@swag_from({
    'tags': ['Administración'],
    'summary': 'Gestión de eventos',
    'description': 'Muestra la lista de eventos para administración',
    'responses': {
        '200': {
            'description': 'Lista de eventos'
        },
        '401': {
            'description': 'Acceso denegado'
        }
    }
})
def eventos():
    eventos = Evento.query.all()
    return render_template('admin/eventos.html', eventos=eventos)

@admin_bp.route('/eventos/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
@swag_from({
    'tags': ['Administración'],
    'summary': 'Crear nuevo evento',
    'description': 'Permite crear un nuevo evento',
    'parameters': [
        {
            'name': 'nombre',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Nombre del evento'
        },
        {
            'name': 'descripcion',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Descripción del evento'
        },
        {
            'name': 'fecha',
            'in': 'formData',
            'type': 'string',
            'format': 'date',
            'required': True,
            'description': 'Fecha del evento (YYYY-MM-DD)'
        },
        {
            'name': 'hora',
            'in': 'formData',
            'type': 'string',
            'format': 'time',
            'required': True,
            'description': 'Hora del evento (HH:MM)'
        },
        {
            'name': 'lugar',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Lugar del evento'
        },
        {
            'name': 'imagen',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'URL de la imagen del evento'
        }
    ],
    'responses': {
        '200': {
            'description': 'Evento creado exitosamente'
        },
        '400': {
            'description': 'Error en la creación del evento'
        }
    }
})
def nuevo_evento():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        fecha_str = request.form['fecha']
        hora_str = request.form['hora']
        lugar = request.form['lugar']
        imagen = request.form.get('imagen', '')
        
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora = datetime.strptime(hora_str, '%H:%M').time()
            
            nuevo_evento = Evento(
                nombre=nombre,
                descripcion=descripcion,
                fecha=fecha,
                hora=hora,
                lugar=lugar,
                imagen=imagen
            )
            
            db.session.add(nuevo_evento)
            db.session.commit()
            
            flash('Evento creado exitosamente', 'success')
            return redirect(url_for('admin.eventos'))
        except ValueError:
            flash('Formato de fecha u hora incorrecto', 'danger')
    
    return render_template('admin/nuevo_evento.html')

@admin_bp.route('/eventos/<int:evento_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
@swag_from({
    'tags': ['Administración'],
    'summary': 'Editar evento',
    'description': 'Permite editar un evento existente',
    'parameters': [
        {
            'name': 'evento_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del evento'
        },
        {
            'name': 'nombre',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Nombre del evento'
        },
        {
            'name': 'descripcion',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Descripción del evento'
        },
        {
            'name': 'fecha',
            'in': 'formData',
            'type': 'string',
            'format': 'date',
            'required': True,
            'description': 'Fecha del evento (YYYY-MM-DD)'
        },
        {
            'name': 'hora',
            'in': 'formData',
            'type': 'string',
            'format': 'time',
            'required': True,
            'description': 'Hora del evento (HH:MM)'
        },
        {
            'name': 'lugar',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Lugar del evento'
        },
        {
            'name': 'imagen',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'URL de la imagen del evento'
        }
    ],
    'responses': {
        '200': {
            'description': 'Evento actualizado exitosamente'
        },
        '400': {
            'description': 'Error en la actualización del evento'
        },
        '404': {
            'description': 'Evento no encontrado'
        }
    }
})
def editar_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    
    if request.method == 'POST':
        evento.nombre = request.form['nombre']
        evento.descripcion = request.form['descripcion']
        evento.fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        evento.hora = datetime.strptime(request.form['hora'], '%H:%M').time()
        evento.lugar = request.form['lugar']
        evento.imagen = request.form.get('imagen', '')
        
        db.session.commit()
        flash('Evento actualizado exitosamente', 'success')
        return redirect(url_for('admin.eventos'))
    
    return render_template('admin/editar_evento.html', evento=evento)

@admin_bp.route('/eventos/<int:evento_id>/asientos')
@login_required
@admin_required
@swag_from({
    'tags': ['Administración'],
    'summary': 'Gestión de asientos',
    'description': 'Muestra los asientos de un evento para su gestión',
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
            'description': 'Lista de asientos'
        },
        '404': {
            'description': 'Evento no encontrado'
        }
    }
})
def asientos_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    asientos = Asiento.query.filter_by(evento_id=evento_id).all()
    return render_template('admin/asientos.html', evento=evento, asientos=asientos)

@admin_bp.route('/eventos/<int:evento_id>/asientos/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
@swag_from({
    'tags': ['Administración'],
    'summary': 'Crear asientos',
    'description': 'Permite crear asientos para un evento',
    'parameters': [
        {
            'name': 'evento_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID del evento'
        },
        {
            'name': 'fila',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Fila del asiento'
        },
        {
            'name': 'cantidad',
            'in': 'formData',
            'type': 'integer',
            'required': True,
            'description': 'Cantidad de asientos a crear'
        },
        {
            'name': 'precio',
            'in': 'formData',
            'type': 'number',
            'required': True,
            'description': 'Precio del asiento'
        }
    ],
    'responses': {
        '200': {
            'description': 'Asientos creados exitosamente'
        },
        '400': {
            'description': 'Error en la creación de asientos'
        }
    }
})
def crear_asientos(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    
    if request.method == 'POST':
        fila = request.form['fila']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        
        for i in range(1, cantidad + 1):
            nuevo_asiento = Asiento(
                evento_id=evento_id,
                fila=fila,
                numero_asiento=i,
                estado='disponible',
                precio=precio
            )
            db.session.add(nuevo_asiento)
        
        db.session.commit()
        flash(f'Se han creado {cantidad} asientos en la fila {fila}', 'success')
        return redirect(url_for('admin.asientos_evento', evento_id=evento_id))
    
    return render_template('admin/crear_asientos.html', evento=evento)

@admin_bp.route('/ventas')
@login_required
@admin_required
@swag_from({
    'tags': ['Administración'],
    'summary': 'Gestión de ventas',
    'description': 'Muestra la lista de ventas para administración',
    'responses': {
        '200': {
            'description': 'Lista de ventas'
        },
        '401': {
            'description': 'Acceso denegado'
        }
    }
})
def ventas():
    ventas = Venta.query.all()
    return render_template('admin/ventas.html', ventas=ventas)
