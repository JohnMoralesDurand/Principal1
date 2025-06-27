from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def generar_ticket(evento_id, asiento_id, usuario_id):
    cur = Conexion().obtener_conexion().cursor()
    cur.execute("SELECT * FROM eventos WHERE id = %s", [evento_id])
    evento = cur.fetchone()
    cur.execute("SELECT * FROM asientos WHERE id = %s", [asiento_id])
    asiento = cur.fetchone()
    cur.execute("SELECT * FROM usuarios WHERE id = %s", [usuario_id])
    usuario = cur.fetchone()
    cur.close()

    # Crear el PDF en memoria
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, f"Ticket de Entrada - Evento: {evento[1]}")
    c.drawString(100, 730, f"Asiento: Fila {asiento[1]} - Asiento {asiento[3]}")
    c.drawString(100, 710, f"Usuario: {usuario[1]}")
    c.drawString(100, 690, f"Precio: ${asiento[3]}")
    c.drawString(100, 670, f"Fecha: {evento[2]} {evento[3]}")

    # Finalizar el PDF
    c.save()

    # Guardar el PDF en memoria
    buffer.seek(0)
    return buffer