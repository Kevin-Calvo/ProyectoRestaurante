# 🍽️ Proyecto de Análisis OLAP para Restaurante

**Análisis y Procesamiento OLAP - Base de Datos 2**  
**Tecnológico de Costa Rica - Sede Cartago**

## 📋 Descripción del Proyecto

Este proyecto implementa un sistema completo de análisis OLAP (Online Analytical Processing) para un restaurante costarricense, utilizando tecnologías modernas de Big Data y visualización. El sistema procesa datos de pedidos, reservas, productos y clientes para generar insights estratégicos del negocio.

## 🎯 Objetivos Cumplidos

### ✅ Arquitectura OLAP y Almacén de Datos (20%)
- Esquema estrella con tablas de hechos y dimensiones
- Data Warehouse optimizado para consultas analíticas
- 5+ vistas OLAP para análisis multidimensional

### ✅ Procesamiento con Apache Spark (20%)
- Transformaciones avanzadas con Spark DataFrames y SparkSQL
- Análisis de tendencias de consumo
- Identificación de horarios pico
- Análisis de crecimiento mensual

### ✅ Visualización de Datos (15%)
- Dashboards interactivos con Metabase
- 3 dashboards principales requeridos
- Métricas clave y KPIs del negocio

### ✅ Orquestación con Apache Airflow (15%)
- **DAG principal**: `restaurant_etl_pipeline` (cada 6 horas)
  - Extracción de datos de PostgreSQL
  - Transformación con Spark
  - Carga en Data Warehouse
  - Reindexado de ElasticSearch
- **DAG de mantenimiento**: `restaurant_maintenance` (diario)
  - Limpieza de datos antiguos
  - Optimización de índices
  - Backup de vistas críticas

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker y Docker Compose instalados
- Al menos 4GB de RAM disponible
- Puertos 3000 y 5432 libres

### Instalación y Ejecución

1. **Clonar el repositorio**
```bash
git clone [tu-repo]
cd proyecto-olap-restaurante
```

2. **Ejecutar el script de inicio**
```bash
chmod +x start.sh
./start.sh
```

3. **Acceder a los servicios**
- **Metabase**: http://localhost:3000
- **Airflow**: http://localhost:8080
- **ElasticSearch**: http://localhost:9200
- **PostgreSQL**: localhost:5432

## 🏗️ Arquitectura del Sistema

```
📊 CAPA DE VISUALIZACIÓN
    ├── Metabase Dashboards
    └── Reportes Exportables

🌬️ CAPA DE ORQUESTACIÓN
    ├── Apache Airflow DAGs
    ├── Pipeline ETL Automatizado
    └── Tareas de Mantenimiento

⚡ CAPA DE PROCESAMIENTO
    ├── Apache Spark
    ├── Transformaciones ETL
    └── Análisis OLAP

🔍 CAPA DE INDEXACIÓN
    ├── ElasticSearch
    └── Búsquedas Optimizadas

💾 CAPA DE DATOS
    ├── PostgreSQL (OLTP)
    ├── Esquema Estrella (OLAP)
    └── Vistas Materializadas
```

## 📊 Dashboards Implementados

### 1. 💰 Ingresos por Mes y Categoría
- Tendencias mensuales de ingresos
- Participación por categoría de producto
- Análisis estacional de ventas

### 2. 🗺️ Actividad por Zona Geográfica
- Distribución de clientes por zona
- Rendimiento de ventas por región
- Ticket promedio por ubicación

### 3. 📈 Estadísticas de Pedidos
- Tasa de éxito vs cancelación
- Evolución mensual de pedidos
- Métricas operativas clave

## 🎛️ Configuración de Metabase

### Conexión a Base de Datos
```
Host: postgres
Puerto: 5432
Base de datos: restaurant_db
Usuario: restaurant_user
Contraseña: restaurant_pass
```

### Configuración Inicial
```
Email: admin@restaurant.com
Contraseña: admin123456
```

## 📈 Análisis OLAP Disponibles

### 🔍 Análisis Multidimensional
- **Tiempo**: Año, mes, trimestre, día de la semana
- **Geografía**: Zona de entrega, región
- **Producto**: Categoría, producto específico
- **Cliente**: Segmentación por zona y comportamiento

### 📊 Métricas Clave
- Ingresos totales y por categoría
- Ticket promedio por pedido
- Productos más vendidos
- Clientes más valiosos
- Tendencias estacionales
- Horarios de mayor demanda

## 🔧 Comandos Útiles

### Docker
```bash
# Ver logs en tiempo real
docker-compose logs -f spark
docker-compose logs -f metabase

# Reiniciar servicios
docker-compose restart

# Limpiar y reiniciar
docker-compose down -v
docker-compose up --build
```

### PostgreSQL
```bash
# Conectar a la base de datos
docker exec -it restaurant_postgres psql -U restaurant_user -d restaurant_db

# Ver tablas disponibles
\dt

# Consultar vistas OLAP
SELECT * FROM vista_olap_ingresos_categoria LIMIT 10;
```

## 📝 Vistas OLAP Creadas

### Vistas Principales
1. **vista_olap_ingresos_categoria**: Ingresos por mes y categoría
2. **vista_olap_actividad_zona**: Actividad de clientes por zona
3. **vista_olap_estadisticas_pedidos**: Estadísticas de pedidos por mes

### Vistas Nativas (SQL)
1. **vista_ingresos_mes_categoria**: Análisis temporal de ingresos
2. **vista_actividad_clientes_zona**: Actividad completa por zona
3. **vista_estadisticas_pedidos**: Métricas mensuales de pedidos
4. **vista_estadisticas_reservas**: Análisis de reservas

## 🎨 Datos de Muestra

El sistema incluye datos realistas de un restaurante costarricense:
- **6 meses** de datos históricos (Enero - Junio 2024)
- **15 clientes** distribuidos en diferentes zonas
- **18 productos** en 6 categorías
- **50+ pedidos** completados
- **20+ reservas** de mesa

## 🔍 Consultas SQL Útiles

### Top 5 Productos Más Vendidos
```sql
SELECT 
    p.nombre,
    SUM(dp.cantidad) as cantidad_vendida,
    SUM(dp.subtotal) as ingresos
FROM detalle_pedidos dp
JOIN productos p ON dp.producto_id = p.id
JOIN pedidos pe ON dp.pedido_id = pe.id
WHERE pe.estado = 'completado'
GROUP BY p.nombre
ORDER BY cantidad_vendida DESC
LIMIT 5;
```

### Ingresos por Zona
```sql
SELECT 
    cliente_zona,
    ingresos_zona,
    clientes_unicos
FROM vista_olap_actividad_zona
ORDER BY ingresos_zona DESC;
```

## 🛠️ Tecnologías Utilizadas

- **Apache Spark 3.5.1**: Procesamiento distribuido de datos
- **Apache Airflow 2.8.1**: Orquestación de workflows
- **PostgreSQL 15**: Base de datos relacional
- **ElasticSearch 8.11.0**: Motor de búsqueda y análisis
- **Metabase**: Visualización y dashboards
- **Docker**: Containerización
- **Python/PySpark**: Desarrollo de análisis
- **SQL**: Consultas y vistas OLAP

## 📊 Requisitos del Proyecto Completados

- ✅ **Esquema estrella** con datos históricos
- ✅ **Procesamiento Spark** con transformaciones
- ✅ **3 tipos de análisis** implementados
- ✅ **3 dashboards** funcionales en Metabase
- ✅ **Vistas OLAP** optimizadas
- ✅ **Métricas clave** del negocio

## 🚨 Solución de Problemas

### Problema: Metabase no inicia
```bash
# Verificar logs
docker-compose logs metabase

# Reiniciar con más memoria
docker-compose down
docker-compose up --build
```

### Problema: Spark falla al conectar
```bash
# Verificar que PostgreSQL esté listo
docker exec restaurant_postgres pg_isready -U restaurant_user

# Ejecutar Spark manualmente
docker-compose run spark python3 /app/analisis_restaurantes_spark.py
```

### Problema: Datos no aparecen en Metabase
1. Verificar conexión a PostgreSQL en Metabase
2. Sincronizar esquema de base de datos
3. Verificar que las vistas OLAP existan:
```sql
SELECT table_name FROM information_schema.views WHERE table_schema = 'public';
```

## 👥 Contribuidores


- **Profesor**: Kenneth Obando Rodríguez
- **Curso**: Base de Datos 2
- **Institución**: TEC - Sede Cartago

## 📄 Licencia

Este proyecto es parte del curso de Base de Datos 2 del Tecnológico de Costa Rica.

---

**🎉 ¡Disfruta explorando los datos de tu restaurante con análisis OLAP!**