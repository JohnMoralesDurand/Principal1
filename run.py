import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app import create_app, db
from app.models.usuario import Usuario
from app.models.evento import Evento
from app.models.asiento import Asiento
from app.models.venta import Venta

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Crear la aplicación
app = create_app()

# Crear un contexto de aplicación
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Usuario': Usuario,
        'Evento': Evento,
        'Asiento': Asiento,
        'Venta': Venta
    }

# Crear tablas de la base de datos y datos de ejemplo
def create_tables_and_seed_data():
    with app.app_context():
        db.create_all()
        
        # Solo crear datos de ejemplo si no hay eventos
        if Evento.query.count() == 0:
            print("Creando datos de ejemplo...")
            
            # Crear eventos de ejemplo
            eventos = [
                {
                    "nombre": "Concierto de Rock",
                    "descripcion": "Un increíble concierto con las mejores bandas de rock.",
                    "fecha": datetime.now() + timedelta(days=30),
                    "hora": datetime.strptime("20:00", "%H:%M").time(),
                    "lugar": "Estadio Principal",
                    "imagen": "https://images.unsplash.com/photo-1540039155733-5bb30b53aa14?w=800&auto=format",
                    "precio_base": 50.0
                },
                {
                    "nombre": "Festival de Jazz",
                    "descripcion": "Disfruta de los mejores artistas de jazz en un ambiente único.",
                    "fecha": datetime.now() + timedelta(days=45),
                    "hora": datetime.strptime("19:30", "%H:%M").time(),
                    "lugar": "Parque Central",
                    "imagen": "https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=800&auto=format",
                    "precio_base": 45.0
                },
                {
                    "nombre": "Obra de Teatro: Romeo y Julieta",
                    "descripcion": "La clásica obra de Shakespeare interpretada por actores de renombre.",
                    "fecha": datetime.now() + timedelta(days=15),
                    "hora": datetime.strptime("18:00", "%H:%M").time(),
                    "lugar": "Teatro Municipal",
                    "imagen": "https://images.unsplash.com/photo-1503095396549-807759245b35?w=800&auto=format",
                    "precio_base": 35.0
                },
                {
                    "nombre": "Exposición de Arte Moderno",
                    "descripcion": "Una colección única de obras de arte contemporáneo de artistas internacionales.",
                    "fecha": datetime.now() + timedelta(days=10),
                    "hora": datetime.strptime("10:00", "%H:%M").time(),
                    "lugar": "Galería de Arte",
                    "imagen": "https://images.unsplash.com/photo-1531913764164-f85c52d7e6a9?w=800&auto=format",
                    "precio_base": 25.0
                },
                {
                    "nombre": "Concierto Sinfónico",
                    "descripcion": "La orquesta sinfónica interpreta obras maestras de la música clásica.",
                    "fecha": datetime.now() + timedelta(days=60),
                    "hora": datetime.strptime("20:30", "%H:%M").time(),
                    "lugar": "Auditorio Nacional",
                    "imagen": "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=800&auto=format",
                    "precio_base": 60.0
                }
            ]
            
            # Crear eventos y asientos
            for evento_data in eventos:
                evento = Evento(
                    nombre=evento_data["nombre"],
                    descripcion=evento_data["descripcion"],
                    fecha=evento_data["fecha"].date(),
                    hora=evento_data["hora"],
                    lugar=evento_data["lugar"],
                    imagen=evento_data["imagen"],
                    capacidad=30
                )
                db.session.add(evento)
                db.session.flush()  # Para obtener el ID del evento
                
                # Crear 30 asientos para cada evento (5 filas x 6 columnas)
                filas = ['A', 'B', 'C', 'D', 'E']
                for fila_idx, fila in enumerate(filas):
                    for num in range(1, 7):
                        # Calcular precio basado en la fila (las primeras filas son más caras)
                        precio_factor = 1.0 - (fila_idx * 0.1)  # A=1.0, B=0.9, C=0.8, etc.
                        precio = round(evento_data["precio_base"] * precio_factor, 2)
                        
                        # Crear asiento
                        asiento = Asiento(
                            evento_id=evento.id,
                            fila=fila,
                            numero_asiento=num,
                            estado='disponible',
                            precio=precio,
                            posicion_x=num,
                            posicion_y=fila_idx + 1,
                            tipo='normal'
                        )
                        db.session.add(asiento)
            
            # Crear un usuario de ejemplo
            if Usuario.query.count() == 0:
                usuario = Usuario(
                    nombre_usuario='usuario_ejemplo',
                    correo='usuario@ejemplo.com'
                )
                usuario.password = 'password123'
                db.session.add(usuario)
            
            db.session.commit()
            print("Datos de ejemplo creados exitosamente.")

# Ejecutar la creación de tablas y datos de ejemplo
create_tables_and_seed_data()

if __name__ == '__main__':
    app.run(debug=True)
