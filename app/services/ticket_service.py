import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import qr
from reportlab.graphics.barcode.qr import QrCodeWidget

def generar_ticket_pdf(venta, evento, asiento, usuario):
    """Genera un PDF con el ticket para un evento"""
    # Crear un buffer para el PDF
    buffer = io.BytesIO()
    
    # Configurar el documento
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Título
    title_style = styles['Title']
    title = Paragraph(f"ENTRADA - {evento.nombre}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.25*inch))
    
    # Información del evento
    info_style = styles['Normal']
    info_style.fontSize = 12
    
    # Formatear fecha y hora
    fecha_str = evento.fecha.strftime("%d/%m/%Y")
    hora_str = evento.hora.strftime("%H:%M")
    
    # Datos del evento
    event_info = [
        [Paragraph("<b>Evento:</b>", info_style), Paragraph(evento.nombre, info_style)],
        [Paragraph("<b>Fecha:</b>", info_style), Paragraph(fecha_str, info_style)],
        [Paragraph("<b>Hora:</b>", info_style), Paragraph(hora_str, info_style)],
        [Paragraph("<b>Lugar:</b>", info_style), Paragraph(evento.lugar, info_style)],
        [Paragraph("<b>Asiento:</b>", info_style), Paragraph(f"Fila {asiento.fila}, Asiento {asiento.numero_asiento}", info_style)],
        [Paragraph("<b>Precio:</b>", info_style), Paragraph(f"${asiento.precio:.2f}", info_style)],
        [Paragraph("<b>Código:</b>", info_style), Paragraph(venta.codigo_ticket, info_style)],
    ]
    
    # Crear tabla con la información
    event_table = Table(event_info, colWidths=[1.5*inch, 4*inch])
    event_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.white),
    ]))
    
    elements.append(event_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Agregar código QR
    qr_code = QrCodeWidget(venta.codigo_ticket)
    qr_code.barWidth = 2
    qr_code.barHeight = 2
    qr_code.qrVersion = 1
    d = Drawing(2*inch, 2*inch, transform=[2, 0, 0, 2, 0, 0])
    d.add(qr_code)
    elements.append(d)
    
    # Agregar nota de pie
    elements.append(Spacer(1, 0.5*inch))
    footer_text = """Este ticket es válido solo para la fecha y hora indicadas. 
    Debe presentarse al momento de ingresar al evento. ArteVivo no se responsabiliza 
    por tickets extraviados o robados."""
    footer = Paragraph(footer_text, styles['Italic'])
    elements.append(footer)
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el valor del buffer y guardarlo en un archivo temporal
    buffer.seek(0)
    
    # Crear directorio para tickets si no existe
    tickets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'tickets')
    if not os.path.exists(tickets_dir):
        os.makedirs(tickets_dir)
    
    # Guardar el PDF en un archivo
    pdf_path = os.path.join(tickets_dir, f"ticket_{venta.codigo_ticket}.pdf")
    with open(pdf_path, 'wb') as f:
        f.write(buffer.read())
    
    return pdf_path
