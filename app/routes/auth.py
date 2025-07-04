from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db, csrf
from app.models.usuario import Usuario
from flask_wtf.csrf import generate_csrf
from flasgger import swag_from

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
@swag_from({
    'tags': ['Autenticación'],
    'summary': 'Iniciar sesión de usuario',
    'description': 'Permite a un usuario iniciar sesión con su correo y contraseña',
    'parameters': [
        {
            'name': 'correo',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Correo electrónico del usuario'
        },
        {
            'name': 'contrasena',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Contraseña del usuario'
        }
    ],
    'responses': {
        '200': {
            'description': 'Inicio de sesión exitoso'
        },
        '401': {
            'description': 'Credenciales inválidas'
        }
    }
})
def login():
    # Si el usuario ya está autenticado, redirigir a la lista de eventos
    if current_user.is_authenticated:
        flash('Ya has iniciado sesión', 'info')
        return redirect(url_for('eventos.lista'))
    
    if request.method == 'POST':
        # El CSRF token es validado automáticamente por Flask-WTF
            
        correo = request.form.get('correo')
        contrasena = request.form.get('contrasena')
        
        if not correo or not contrasena:
            flash('Por favor, completa todos los campos', 'danger')
            return render_template('auth/login.html')
        
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return render_template('auth/login.html')
            
        if not usuario.verify_password(contrasena):
            flash('Contraseña incorrecta', 'danger')
            return render_template('auth/login.html')
        
        # Login exitoso
        login_user(usuario, remember=True)
        flash(f'Bienvenido, {usuario.nombre_usuario}!', 'success')
        
        # Redirigir a la página solicitada o a la página principal
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('eventos.lista')
        
        return redirect(next_page)
    
    return render_template('auth/login.html')

@auth_bp.route('/registro', methods=['GET', 'POST'])
@swag_from({
    'tags': ['Autenticación'],
    'summary': 'Registrar nuevo usuario',
    'description': 'Permite registrar un nuevo usuario en el sistema',
    'parameters': [
        {
            'name': 'nombre_usuario',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Nombre de usuario'
        },
        {
            'name': 'correo',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Correo electrónico'
        },
        {
            'name': 'contrasena',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Contraseña'
        }
    ],
    'responses': {
        '200': {
            'description': 'Usuario registrado exitosamente'
        },
        '400': {
            'description': 'Error en el registro'
        }
    }
})
def registro():
    # Si el usuario ya está autenticado, redirigir a la lista de eventos
    if current_user.is_authenticated:
        flash('Ya has iniciado sesión. Cierra sesión para crear una nueva cuenta.', 'info')
        return redirect(url_for('eventos.lista'))
    
    if request.method == 'POST':
        try:
            # El CSRF token es validado automáticamente por Flask-WTF
                
            nombre_usuario = request.form.get('nombre_usuario')
            correo = request.form.get('correo')
            contrasena = request.form.get('contrasena')
            confirmar_contrasena = request.form.get('confirmar_contrasena')
            
            # Validaciones básicas
            if not nombre_usuario or not correo or not contrasena:
                flash('Por favor, completa todos los campos obligatorios', 'danger')
                return render_template('auth/registro.html')
                
            if contrasena != confirmar_contrasena:
                flash('Las contraseñas no coinciden', 'danger')
                return render_template('auth/registro.html')
                
            if len(contrasena) < 8:
                flash('La contraseña debe tener al menos 8 caracteres', 'danger')
                return render_template('auth/registro.html')
            
            # Verificar si el usuario ya existe
            usuario_existente = Usuario.query.filter((Usuario.correo == correo) | 
                                                (Usuario.nombre_usuario == nombre_usuario)).first()
            if usuario_existente:
                if usuario_existente.correo == correo:
                    flash('Este correo electrónico ya está registrado', 'danger')
                else:
                    flash('Este nombre de usuario ya está en uso', 'danger')
                return render_template('auth/registro.html')
            
            # Crear nuevo usuario
            nuevo_usuario = Usuario(nombre_usuario=nombre_usuario, correo=correo)
            nuevo_usuario.password = contrasena
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error en el registro: {str(e)}', 'danger')
    
    return render_template('auth/registro.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('eventos.lista'))
