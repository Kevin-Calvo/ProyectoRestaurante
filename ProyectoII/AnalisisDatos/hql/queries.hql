docker-compose exec hive-server bash

/opt/hive/bin/beeline -u jdbc:hive2://localhost:10000

Create database Restaurante;

Use Restaurante;

Ejecutar los Create

Cargar los Datos a las tablas desde los csv

LOAD DATA LOCAL INPATH '/data/dim_restaurante.csv' INTO TABLE dim_restaurante;
LOAD DATA LOCAL INPATH '/data/dim_tiempo.csv' INTO TABLE dim_tiempo;
LOAD DATA LOCAL INPATH '/data/dim_usuario.csv' INTO TABLE dim_usuario;
LOAD DATA LOCAL INPATH '/data/hechos_pedidos.csv' INTO TABLE hechos_pedidos;
LOAD DATA LOCAL INPATH '/data/hechos_resrvaciones.csv' INTO TABLE hechos_reservaciones;

Vistas
1. Pedidos por mes por restaurante

CREATE VIEW pedidos_por_mes_restaurante AS
SELECT
  t.mes,
  r.nombre AS restaurante,
  COUNT(p.id) AS total_pedidos
FROM hechos_pedidos p
JOIN dim_tiempo t ON p.fecha = t.fecha
JOIN dim_restaurante r ON p.id_restaurante = r.id
GROUP BY t.mes, r.nombre;

2. Cantidad de reservaciones por trimestre

CREATE VIEW reservaciones_por_trimestre AS
SELECT
  t.trimestre,
  COUNT(r.id) AS total_reservaciones
FROM hechos_reservaciones r
JOIN dim_tiempo t ON r.fecha = t.fecha
GROUP BY t.trimestre;

3. PEdido por zona

CREATE VIEW pedidos_por_provincia AS
SELECT
  SUBSTRING_INDEX(r.direccion, ',', 1) AS provincia,
  COUNT(p.id) AS total_pedidos
FROM hechos_pedidos p
JOIN dim_restaurante r ON p.id_restaurante = r.id
GROUP BY SUBSTRING_INDEX(r.direccion, ',', 1);


4. Acciones por usuario 

CREATE VIEW actividad_usuario_total AS
SELECT
  u.nombre,
  COUNT(DISTINCT p.id) AS pedidos,
  COUNT(DISTINCT r.id) AS reservaciones
FROM dim_usuario u
LEFT JOIN hechos_pedidos p ON u.id = p.id_usuario
LEFT JOIN hechos_reservaciones r ON u.id = r.id_usuario
GROUP BY u.nombre;

5. Pedidos por dia del mes

CREATE VIEW pedidos_dia AS
SELECT
  t.dia,
  COUNT(p.id) AS total_pedidos
FROM hechos_pedidos p
JOIN dim_tiempo t ON p.fecha = t.fecha
GROUP BY t.dia;



