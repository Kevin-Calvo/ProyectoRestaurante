-- Crear tablas del restaurante
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    categoria_id INTEGER REFERENCES categorias(id),
    descripcion TEXT,
    activo BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    telefono VARCHAR(20),
    zona_geografica VARCHAR(100),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pedidos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'pendiente', -- pendiente, completado, cancelado
    total DECIMAL(10,2) NOT NULL,
    zona_entrega VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS detalle_pedidos (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER REFERENCES pedidos(id),
    producto_id INTEGER REFERENCES productos(id),
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

-- Nueva tabla de reservas
CREATE TABLE IF NOT EXISTS reservas (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    fecha_reserva TIMESTAMP NOT NULL,
    numero_personas INTEGER NOT NULL,
    estado VARCHAR(20) DEFAULT 'confirmada', -- confirmada, cancelada, completada
    mesa_asignada INTEGER,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar categorías
INSERT INTO categorias (nombre, descripcion) VALUES
('Entradas', 'Platos de entrada y aperitivos'),
('Platos Principales', 'Platos principales del menú'),
('Postres', 'Dulces y postres'),
('Bebidas', 'Bebidas frías y calientes'),
('Ensaladas', 'Ensaladas frescas y saludables'),
('Especiales', 'Platos especiales de temporada');

-- Insertar productos (ampliado)
INSERT INTO productos (nombre, precio, categoria_id, descripcion) VALUES
('Patacones con Guacamole', 3500.00, 1, 'Patacones fritos con guacamole casero'),
('Ceviche de Pescado', 4200.00, 1, 'Ceviche fresco con pescado del día'),
('Empanadas de Queso', 2800.00, 1, 'Empanadas criollas rellenas de queso'),
('Casado Típico', 5500.00, 2, 'Arroz, frijoles, carne, plátano y ensalada'),
('Gallo Pinto', 2800.00, 2, 'Tradicional gallo pinto costarricense'),
('Olla de Carne', 6200.00, 2, 'Sopa tradicional con carne y vegetales'),
('Pescado a la Plancha', 7500.00, 2, 'Pescado fresco a la plancha con vegetales'),
('Pollo en Salsa', 6800.00, 2, 'Pollo en salsa especial de la casa'),
('Tres Leches', 2500.00, 3, 'Tradicional postre de tres leches'),
('Flan Caramelizado', 2200.00, 3, 'Flan casero con caramelo'),
('Torta de Chocolate', 3200.00, 3, 'Torta húmeda de chocolate con betún'),
('Café Gourmet', 1200.00, 4, 'Café de especialidad costarricense'),
('Agua de Tamarindo', 800.00, 4, 'Refrescante agua de tamarindo natural'),
('Jugo Natural', 1500.00, 4, 'Jugos naturales variados'),
('Ensalada César', 3800.00, 5, 'Ensalada césar con pollo a la parrilla'),
('Ensalada Tropical', 4200.00, 5, 'Ensalada con frutas tropicales'),
('Plato del Chef', 8500.00, 6, 'Creación especial del chef'),
('Paella Costarricense', 9200.00, 6, 'Paella con mariscos locales');

-- Insertar clientes con diferentes zonas (ampliado)
INSERT INTO clientes (nombre, email, telefono, zona_geografica) VALUES
('María González', 'maria@email.com', '8888-1111', 'San José Centro'),
('Carlos Rodríguez', 'carlos@email.com', '8888-2222', 'Cartago'),
('Ana Jiménez', 'ana@email.com', '8888-3333', 'Heredia'),
('Luis Morales', 'luis@email.com', '8888-4444', 'San José Centro'),
('Carmen Solano', 'carmen@email.com', '8888-5555', 'Alajuela'),
('Roberto Chacón', 'roberto@email.com', '8888-6666', 'Cartago'),
('Patricia Vega', 'patricia@email.com', '8888-7777', 'Heredia'),
('Miguel Arias', 'miguel@email.com', '8888-8888', 'San José Centro'),
('Sofía Castro', 'sofia@email.com', '8888-9999', 'Puntarenas'),
('Diego Hernández', 'diego@email.com', '8888-0000', 'Guanacaste'),
('Elena Rojas', 'elena@email.com', '8888-1234', 'San José Centro'),
('Fernando Mata', 'fernando@email.com', '8888-5678', 'Alajuela'),
('Gabriela Soto', 'gabriela@email.com', '8888-9012', 'Heredia'),
('Andrés Villalobos', 'andres@email.com', '8888-3456', 'Cartago'),
('Lucía Ramírez', 'lucia@email.com', '8888-7890', 'Puntarenas');

-- Insertar pedidos con más datos y diferentes horarios
INSERT INTO pedidos (cliente_id, fecha_pedido, estado, total, zona_entrega) VALUES
-- Enero 2024
(1, '2024-01-15 12:30:00', 'completado', 8700.00, 'San José Centro'),
(2, '2024-01-18 19:45:00', 'completado', 12400.00, 'Cartago'),
(3, '2024-01-22 13:15:00', 'cancelado', 5500.00, 'Heredia'),
(4, '2024-01-25 20:30:00', 'completado', 15200.00, 'San José Centro'),
(5, '2024-01-28 14:45:00', 'completado', 9800.00, 'Alajuela'),
-- Febrero 2024
(6, '2024-02-05 14:20:00', 'completado', 9800.00, 'Cartago'),
(7, '2024-02-12 18:30:00', 'completado', 15600.00, 'Heredia'),
(8, '2024-02-20 12:45:00', 'completado', 7300.00, 'San José Centro'),
(9, '2024-02-22 19:15:00', 'completado', 11800.00, 'Puntarenas'),
(10, '2024-02-25 13:30:00', 'completado', 8900.00, 'Guanacaste'),
-- Marzo 2024
(11, '2024-03-08 13:00:00', 'completado', 11200.00, 'San José Centro'),
(12, '2024-03-15 19:15:00', 'cancelado', 6800.00, 'Alajuela'),
(13, '2024-03-25 14:45:00', 'completado', 13400.00, 'Heredia'),
(14, '2024-03-28 20:00:00', 'completado', 16500.00, 'Cartago'),
(15, '2024-03-30 12:15:00', 'completado', 9200.00, 'Puntarenas'),
-- Abril 2024
(1, '2024-04-02 12:15:00', 'completado', 8900.00, 'San José Centro'),
(2, '2024-04-10 18:20:00', 'completado', 10500.00, 'Cartago'),
(3, '2024-04-18 13:30:00', 'completado', 7800.00, 'Heredia'),
(4, '2024-04-22 19:45:00', 'completado', 14200.00, 'San José Centro'),
(5, '2024-04-25 14:00:00', 'completado', 12300.00, 'Alajuela'),
-- Mayo 2024
(6, '2024-05-05 19:00:00', 'completado', 14200.00, 'Cartago'),
(7, '2024-05-12 12:45:00', 'cancelado', 9100.00, 'Heredia'),
(8, '2024-05-20 14:15:00', 'completado', 11800.00, 'San José Centro'),
(9, '2024-05-25 18:30:00', 'completado', 13500.00, 'Puntarenas'),
(10, '2024-05-28 13:45:00', 'completado', 10800.00, 'Guanacaste'),
-- Junio 2024
(11, '2024-06-03 13:45:00', 'completado', 16500.00, 'San José Centro'),
(12, '2024-06-15 18:30:00', 'completado', 12900.00, 'Alajuela'),
(13, '2024-06-22 12:30:00', 'completado', 8400.00, 'Heredia'),
(14, '2024-06-25 19:00:00', 'completado', 15800.00, 'Cartago'),
(15, '2024-06-28 14:20:00', 'completado', 11200.00, 'Puntarenas');

-- Insertar más detalles de pedidos
INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, precio_unitario, subtotal) VALUES
-- Pedido 1
(1, 1, 2, 3500.00, 7000.00),
(1, 12, 1, 1200.00, 1200.00),
(1, 9, 1, 2500.00, 2500.00),
-- Pedido 2
(2, 4, 2, 5500.00, 11000.00),
(2, 13, 2, 800.00, 1600.00),
-- Pedido 4
(4, 6, 1, 6200.00, 6200.00),
(4, 10, 1, 2200.00, 2200.00),
(4, 12, 1, 1200.00, 1200.00),
(4, 17, 1, 8500.00, 8500.00),
-- Pedido 5
(5, 4, 1, 5500.00, 5500.00),
(5, 15, 1, 3800.00, 3800.00),
(5, 13, 1, 800.00, 800.00),
-- Pedido 6
(6, 2, 1, 4200.00, 4200.00),
(6, 5, 1, 2800.00, 2800.00),
(6, 9, 1, 2500.00, 2500.00),
-- Pedido 7
(7, 7, 2, 7500.00, 15000.00),
(7, 14, 1, 1500.00, 1500.00),
-- Pedido 8
(8, 3, 2, 2800.00, 5600.00),
(8, 14, 1, 1500.00, 1500.00),
-- Pedido 9
(9, 8, 1, 6800.00, 6800.00),
(9, 11, 1, 3200.00, 3200.00),
(9, 12, 2, 1200.00, 2400.00),
-- Pedido 10
(10, 18, 1, 9200.00, 9200.00),
-- Más pedidos...
(11, 17, 1, 8500.00, 8500.00),
(11, 16, 1, 4200.00, 4200.00),
(13, 18, 1, 9200.00, 9200.00),
(13, 11, 1, 3200.00, 3200.00),
(14, 7, 2, 7500.00, 15000.00),
(14, 12, 1, 1200.00, 1200.00),
(15, 4, 1, 5500.00, 5500.00),
(15, 15, 1, 3800.00, 3800.00),
(16, 6, 1, 6200.00, 6200.00),
(16, 10, 1, 2200.00, 2200.00),
(17, 8, 1, 6800.00, 6800.00),
(17, 11, 1, 3200.00, 3200.00),
(18, 2, 1, 4200.00, 4200.00),
(18, 15, 1, 3800.00, 3800.00),
(19, 17, 1, 8500.00, 8500.00),
(19, 16, 1, 4200.00, 4200.00),
(20, 18, 1, 9200.00, 9200.00),
(20, 11, 1, 3200.00, 3200.00);

-- Insertar reservas
INSERT INTO reservas (cliente_id, fecha_reserva, numero_personas, estado, mesa_asignada, observaciones) VALUES
-- Enero 2024
(1, '2024-01-20 19:00:00', 4, 'completada', 5, 'Mesa junto a la ventana'),
(2, '2024-01-25 20:00:00', 2, 'completada', 2, 'Aniversario de bodas'),
(3, '2024-01-28 18:30:00', 6, 'cancelada', 8, 'Celebración familiar'),
-- Febrero 2024
(4, '2024-02-14 19:30:00', 2, 'completada', 1, 'Cena de San Valentín'),
(5, '2024-02-18 13:00:00', 8, 'completada', 10, 'Almuerzo de negocios'),
(6, '2024-02-22 20:00:00', 4, 'completada', 6, 'Cena con amigos'),
-- Marzo 2024
(7, '2024-03-05 18:00:00', 3, 'completada', 3, 'Cumpleaños'),
(8, '2024-03-10 19:00:00', 5, 'completada', 7, 'Reunión familiar'),
(9, '2024-03-15 20:30:00', 2, 'cancelada', 4, 'Cena romántica'),
(10, '2024-03-20 12:30:00', 6, 'completada', 9, 'Almuerzo de trabajo'),
-- Abril 2024
(11, '2024-04-05 19:00:00', 4, 'completada', 5, 'Cena de amigos'),
(12, '2024-04-12 13:30:00', 2, 'completada', 2, 'Almuerzo de pareja'),
(13, '2024-04-18 20:00:00', 8, 'completada', 10, 'Celebración de ascenso'),
(14, '2024-04-25 18:30:00', 3, 'completada', 3, 'Cena familiar'),
-- Mayo 2024
(15, '2024-05-02 19:30:00', 5, 'completada', 7, 'Reunión de excompañeros'),
(1, '2024-05-10 20:00:00', 2, 'completada', 1, 'Cena de aniversario'),
(2, '2024-05-15 12:00:00', 6, 'completada', 8, 'Almuerzo familiar'),
(3, '2024-05-20 19:00:00', 4, 'cancelada', 6, 'Cena con colegas'),
-- Junio 2024
(4, '2024-06-05 18:00:00', 3, 'completada', 4, 'Graduación'),
(5, '2024-06-12 13:00:00', 7, 'completada', 9, 'Almuerzo de equipo'),
(6, '2024-06-18 20:30:00', 2, 'completada', 2, 'Cena especial'),
(7, '2024-06-25 19:00:00', 5, 'confirmada', 7, 'Próxima reserva');

-- Crear vistas para facilitar el análisis
CREATE OR REPLACE VIEW vista_ingresos_mes_categoria AS
SELECT 
    DATE_TRUNC('month', p.fecha_pedido) as mes,
    EXTRACT(YEAR FROM p.fecha_pedido) as anio,
    EXTRACT(MONTH FROM p.fecha_pedido) as mes_num,
    c.nombre as categoria,
    SUM(dp.subtotal) as ingresos_total,
    COUNT(dp.id) as cantidad_items,
    AVG(dp.subtotal) as ticket_promedio_item
FROM pedidos p
JOIN detalle_pedidos dp ON p.id = dp.pedido_id
JOIN productos pr ON dp.producto_id = pr.id
JOIN categorias c ON pr.categoria_id = c.id
WHERE p.estado = 'completado'
GROUP BY DATE_TRUNC('month', p.fecha_pedido), EXTRACT(YEAR FROM p.fecha_pedido), 
         EXTRACT(MONTH FROM p.fecha_pedido), c.nombre
ORDER BY mes, categoria;

CREATE OR REPLACE VIEW vista_actividad_clientes_zona AS
SELECT 
    cl.zona_geografica,
    COUNT(DISTINCT cl.id) as total_clientes,
    COUNT(p.id) as total_pedidos,
    COUNT(r.id) as total_reservas,
    SUM(CASE WHEN p.estado = 'completado' THEN p.total ELSE 0 END) as ingresos_total,
    AVG(CASE WHEN p.estado = 'completado' THEN p.total ELSE NULL END) as ticket_promedio,
    COUNT(CASE WHEN r.estado = 'completada' THEN 1 END) as reservas_completadas
FROM clientes cl
LEFT JOIN pedidos p ON cl.id = p.cliente_id
LEFT JOIN reservas r ON cl.id = r.cliente_id
GROUP BY cl.zona_geografica
ORDER BY ingresos_total DESC;

CREATE OR REPLACE VIEW vista_estadisticas_pedidos AS
SELECT 
    DATE_TRUNC('month', fecha_pedido) as mes,
    EXTRACT(YEAR FROM fecha_pedido) as anio,
    EXTRACT(MONTH FROM fecha_pedido) as mes_num,
    COUNT(*) as total_pedidos,
    SUM(CASE WHEN estado = 'completado' THEN 1 ELSE 0 END) as pedidos_completados,
    SUM(CASE WHEN estado = 'cancelado' THEN 1 ELSE 0 END) as pedidos_cancelados,
    SUM(CASE WHEN estado = 'completado' THEN total ELSE 0 END) as ingresos_totales,
    ROUND(
        (SUM(CASE WHEN estado = 'completado' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2
    ) as porcentaje_completados
FROM pedidos
GROUP BY DATE_TRUNC('month', fecha_pedido), EXTRACT(YEAR FROM fecha_pedido), 
         EXTRACT(MONTH FROM fecha_pedido)
ORDER BY mes;

CREATE OR REPLACE VIEW vista_estadisticas_reservas AS
SELECT 
    DATE_TRUNC('month', fecha_reserva) as mes,
    EXTRACT(YEAR FROM fecha_reserva) as anio,
    EXTRACT(MONTH FROM fecha_reserva) as mes_num,
    COUNT(*) as total_reservas,
    SUM(CASE WHEN estado = 'completada' THEN 1 ELSE 0 END) as reservas_completadas,
    SUM(CASE WHEN estado = 'cancelada' THEN 1 ELSE 0 END) as reservas_canceladas,
    AVG(numero_personas) as promedio_personas,
    ROUND(
        (SUM(CASE WHEN estado = 'completada' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2
    ) as porcentaje_completadas
FROM reservas
GROUP BY DATE_TRUNC('month', fecha_reserva), EXTRACT(YEAR FROM fecha_reserva), 
         EXTRACT(MONTH FROM fecha_reserva)
ORDER BY mes;

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_pedidos_fecha ON pedidos(fecha_pedido);
CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado);
CREATE INDEX IF NOT EXISTS idx_pedidos_cliente ON pedidos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_reservas_fecha ON reservas(fecha_reserva);
CREATE INDEX IF NOT EXISTS idx_reservas_estado ON reservas(estado);
CREATE INDEX IF NOT EXISTS idx_detalle_pedido ON detalle_pedidos(pedido_id);
CREATE INDEX IF NOT EXISTS idx_detalle_producto ON detalle_pedidos(producto_id);
CREATE INDEX IF NOT EXISTS idx_clientes_zona ON clientes(zona_geografica);