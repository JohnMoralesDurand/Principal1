from flask import Flask, render_template, request, redirect, url_for, session, flash
from clases.eventos import Eventos
from clases.asientos import Asientos
from clases.usuarios import Usuarios
from clases.conexion import Conexion
import functools

app = Flask(__name__)

# Inicializar las clases
eventos = Eventos()
asientos = Asientos()
usuarios = Usuarios()

# Configuración de la clave secreta para sesiones
app.secret_key = 'super_secret_key'

# Función para requerir inicio de sesión
def inicio_de_sesion_requerido(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('usuario') is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

# Ruta para la página de inicio
@app.route('/')
def inicio():
    return render_template('index.html')

# Ruta para la visualización de los eventos
@app.route('/eventos/')
def ver_eventos():
    lista_eventos = eventos.obtener_eventos()
    return render_template('eventos.html', eventos=lista_eventos)

# Ruta para ver el detalle de un evento y elegir asientos
@app.route('/comprar/<int:evento_id>', methods=['GET', 'POST'])
@inicio_de_sesion_requerido
def comprar_entrada(evento_id):
    if request.method == 'POST':
        asiento_id = request.form['asiento_id']
        precio = request.form['precio']

        # Marcar asiento como vendido
        asientos.marcar_asiento_vendido(asiento_id)

        # Registrar la venta
        cur = Conexion().obtener_conexion().cursor()
        cur.execute("""
            INSERT INTO ventas(usuario_id, evento_id, asiento_id, precio)
            VALUES (%s, %s, %s, %s)
        """, (session['usuario'], evento_id, asiento_id, precio))
        Conexion().obtener_conexion().commit()

        # Redirigir a la página de confirmación o generar el ticket
        return redirect(url_for('exito_pago', evento_id=evento_id, asiento_id=asiento_id))
    else:
        # Obtener los asientos disponibles para el evento
        asientos_disponibles = asientos.obtener_asientos_disponibles(evento_id)
        return render_template('comprar.html', asientos=asientos_disponibles, evento_id=evento_id)

# Ruta para mostrar el ticket de compra exitosa
@app.route('/exito_pago/<int:evento_id>/<int:asiento_id>')
def exito_pago(evento_id, asiento_id):
    # Aquí generas el ticket PDF (usando ReportLab u otro sistema)
    pdf = generar_ticket(evento_id, asiento_id, session['usuario'])

    # Devolver el PDF al usuario
    return send_file(pdf, as_attachment=True, download_name="ticket_evento.pdf", mimetype='application/pdf')

# Ruta para registrarse
@app.route('/registro/', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        usuarios.registrar_usuario(nombre_usuario, correo, contrasena)
        flash("Registro exitoso! Ahora puedes iniciar sesión.")
        return redirect(url_for('login'))
    return render_template('registro.html')

# Ruta para iniciar sesión
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        usuario = usuarios.verificar_usuario(correo, contrasena)
        if usuario:
            session['usuario'] = usuario[0]
            return redirect(url_for('ver_eventos'))
        else:
            flash("Usuario o contraseña incorrectos.")
    return render_template('login.html')

# Ruta para cerrar sesión
@app.route('/cerrar-sesion')
def cerrar_sesion():
    session.clear()
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.run(debug=True)