-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS sistema_eventos;
USE sistema_eventos;

-- Tabla de eventos
CREATE TABLE IF NOT EXISTS eventos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    lugar VARCHAR(255) NOT NULL
);

-- Tabla de asientos disponibles en un evento
CREATE TABLE IF NOT EXISTS asientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evento_id INT NOT NULL,
    fila VARCHAR(10) NOT NULL,
    numero_asiento INT NOT NULL,
    estado ENUM('disponible', 'reservado', 'vendido') DEFAULT 'disponible',
    FOREIGN KEY (evento_id) REFERENCES eventos(id)
);

-- Tabla de usuarios registrados (clientes)
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(255) UNIQUE NOT NULL,
    correo VARCHAR(255) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    tipo_usuario ENUM('cliente', 'administrador') DEFAULT 'cliente'
);

-- Tabla de ventas (entradas compradas)
CREATE TABLE IF NOT EXISTS ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    evento_id INT NOT NULL,
    asiento_id INT NOT NULL,
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    precio DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (evento_id) REFERENCES eventos(id),
    FOREIGN KEY (asiento_id) REFERENCES asientos(id)
);