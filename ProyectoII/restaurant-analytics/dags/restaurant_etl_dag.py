"""
DAG de Orquestación para Análisis OLAP del Restaurante
=====================================================

Este DAG implementa el pipeline completo de datos:
1. Extracción de datos de PostgreSQL
2. Transformación con Spark  
3. Carga en el Data Warehouse
4. Reindexado de ElasticSearch
5. Actualización de vistas OLAP

Autor: Proyecto Base de Datos 2 - TEC Cartago
Fecha: Junio 2025
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
import pandas as pd
import psycopg2
import requests
import json
import logging

# Configuración del DAG
default_args = {
    'owner': 'restaurant-analytics',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

dag = DAG(
    'restaurant_etl_pipeline',
    default_args=default_args,
    description='Pipeline ETL completo para análisis OLAP del restaurante',
    schedule_interval=timedelta(hours=6),  # Ejecutar cada 6 horas
    tags=['restaurant', 'etl', 'olap', 'spark'],
    max_active_runs=1
)

# ===============================================
# TAREAS DE VALIDACIÓN Y PREPARACIÓN
# ===============================================

def check_data_quality():
    """Verificar la calidad de los datos antes del procesamiento"""
    logging.info("🔍 Verificando calidad de datos...")
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_restaurant')
        
        # Verificar que existan datos recientes
        sql_check_recent_data = """
        SELECT COUNT(*) as recent_orders 
        FROM pedidos 
        WHERE fecha_pedido >= NOW() - INTERVAL '24 hours'
        """
        
        recent_orders = pg_hook.get_first(sql_check_recent_data)[0]
        logging.info(f"📊 Pedidos recientes (24h): {recent_orders}")
        
        # Verificar integridad referencial
        sql_check_integrity = """
        SELECT 
            COUNT(*) as total_detalle,
            COUNT(DISTINCT pedido_id) as pedidos_con_detalle,
            COUNT(DISTINCT producto_id) as productos_activos
        FROM detalle_pedidos dp
        JOIN pedidos p ON dp.pedido_id = p.id
        JOIN productos pr ON dp.producto_id = pr.id
        WHERE p.estado = 'completado'
        """
        
        integrity_data = pg_hook.get_first(sql_check_integrity)
        logging.info(f"✅ Verificación de integridad: {integrity_data}")
        
        # Verificar datos de clientes
        sql_check_clients = """
        SELECT COUNT(DISTINCT id) as total_clientes,
               COUNT(DISTINCT zona_geografica) as zonas_activas
        FROM clientes
        """
        
        client_data = pg_hook.get_first(sql_check_clients)
        logging.info(f"👥 Datos de clientes: {client_data}")
        
        return {
            'recent_orders': recent_orders,
            'integrity_check': integrity_data,
            'client_data': client_data,
            'status': 'success'
        }
        
    except Exception as e:
        logging.error(f"❌ Error en verificación de calidad: {e}")
        raise

def extract_data_from_postgres():
    """Extraer datos de PostgreSQL para procesamiento"""
    logging.info("📤 Extrayendo datos de PostgreSQL...")
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_restaurant')
        
        # Extraer resumen de datos para validación
        sql_extract_summary = """
        SELECT 
            DATE_TRUNC('month', p.fecha_pedido) as mes,
            COUNT(*) as total_pedidos,
            COUNT(CASE WHEN p.estado = 'completado' THEN 1 END) as pedidos_completados,
            SUM(CASE WHEN p.estado = 'completado' THEN p.total ELSE 0 END) as ingresos_mes,
            COUNT(DISTINCT p.cliente_id) as clientes_activos
        FROM pedidos p
        WHERE p.fecha_pedido >= DATE_TRUNC('year', CURRENT_DATE)
        GROUP BY DATE_TRUNC('month', p.fecha_pedido)
        ORDER BY mes DESC
        """
        
        monthly_data = pg_hook.get_records(sql_extract_summary)
        logging.info(f"📊 Datos mensuales extraídos: {len(monthly_data)} registros")
        
        # Validar productos activos
        sql_products_check = """
        SELECT c.nombre as categoria, COUNT(p.id) as productos_activos
        FROM categorias c
        LEFT JOIN productos p ON c.id = p.categoria_id AND p.activo = true
        GROUP BY c.nombre
        ORDER BY productos_activos DESC
        """
        
        products_data = pg_hook.get_records(sql_products_check)
        logging.info(f"🍽️ Productos por categoría: {products_data}")
        
        return {
            'monthly_summary': monthly_data,
            'products_by_category': products_data,
            'extraction_timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
    except Exception as e:
        logging.error(f"❌ Error en extracción: {e}")
        raise

def create_data_warehouse_schema():
    """Crear/actualizar esquema del Data Warehouse"""
    logging.info("🏗️ Creando esquemas del Data Warehouse...")
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_restaurant')
        
        # Crear tablas del Data Warehouse si no existen
        dwh_schema_sql = """
        -- Tabla de hechos para el DWH
        CREATE TABLE IF NOT EXISTS dwh_fact_ventas (
            id SERIAL PRIMARY KEY,
            fecha_key DATE,
            cliente_key INTEGER,
            producto_key INTEGER,
            categoria_key INTEGER,
            cantidad INTEGER,
            precio_unitario DECIMAL(10,2),
            subtotal DECIMAL(10,2),
            total_pedido DECIMAL(10,2),
            zona_entrega VARCHAR(100),
            fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de dimensión tiempo
        CREATE TABLE IF NOT EXISTS dwh_dim_tiempo (
            fecha_key DATE PRIMARY KEY,
            anio INTEGER,
            mes INTEGER,
            dia INTEGER,
            trimestre INTEGER,
            mes_nombre VARCHAR(20),
            dia_semana INTEGER,
            nombre_dia_semana VARCHAR(20),
            es_fin_semana BOOLEAN,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Índices para optimización
        CREATE INDEX IF NOT EXISTS idx_dwh_fact_fecha ON dwh_fact_ventas(fecha_key);
        CREATE INDEX IF NOT EXISTS idx_dwh_fact_cliente ON dwh_fact_ventas(cliente_key);
        CREATE INDEX IF NOT EXISTS idx_dwh_fact_producto ON dwh_fact_ventas(producto_key);
        
        -- Vista materializada para dashboards
        DROP MATERIALIZED VIEW IF EXISTS mv_dashboard_ingresos_categoria;
        CREATE MATERIALIZED VIEW mv_dashboard_ingresos_categoria AS
        SELECT 
            dt.anio,
            dt.mes,
            dt.mes_nombre,
            c.nombre as categoria,
            SUM(fv.subtotal) as ingresos_categoria,
            COUNT(DISTINCT fv.cliente_key) as clientes_unicos,
            SUM(fv.cantidad) as productos_vendidos,
            AVG(fv.precio_unitario) as precio_promedio
        FROM dwh_fact_ventas fv
        JOIN dwh_dim_tiempo dt ON fv.fecha_key = dt.fecha_key
        JOIN productos p ON fv.producto_key = p.id
        JOIN categorias c ON p.categoria_id = c.id
        GROUP BY dt.anio, dt.mes, dt.mes_nombre, c.nombre
        ORDER BY dt.anio, dt.mes, ingresos_categoria DESC;
        
        CREATE INDEX IF NOT EXISTS idx_mv_dashboard_fecha_cat 
        ON mv_dashboard_ingresos_categoria(anio, mes, categoria);
        """
        
        pg_hook.run(dwh_schema_sql)
        logging.info("✅ Esquema del Data Warehouse creado/actualizado")
        
        return {'status': 'success', 'message': 'DWH schema updated'}
        
    except Exception as e:
        logging.error(f"❌ Error creando esquema DWH: {e}")
        raise

def check_elasticsearch_status():
    """Verificar estado de ElasticSearch"""
    logging.info("🔍 Verificando estado de ElasticSearch...")
    
    try:
        # Verificar conectividad
        response = requests.get('http://elasticsearch:9200/_cluster/health', timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            logging.info(f"✅ ElasticSearch status: {health_data.get('status', 'unknown')}")
            
            # Verificar índices existentes
            indices_response = requests.get('http://elasticsearch:9200/_cat/indices?format=json', timeout=10)
            if indices_response.status_code == 200:
                indices = indices_response.json()
                logging.info(f"📊 Índices existentes: {len(indices)}")
            
            return {
                'cluster_health': health_data,
                'indices_count': len(indices) if indices_response.status_code == 200 else 0,
                'status': 'healthy'
            }
        else:
            logging.warning(f"⚠️ ElasticSearch respuesta no OK: {response.status_code}")
            return {'status': 'unhealthy', 'code': response.status_code}
            
    except Exception as e:
        logging.error(f"❌ Error verificando ElasticSearch: {e}")
        return {'status': 'error', 'message': str(e)}

def reindex_products_elasticsearch():
    """Reindexar productos en ElasticSearch"""
    logging.info("🔄 Reindexando productos en ElasticSearch...")
    
    try:
        # Obtener productos de PostgreSQL
        pg_hook = PostgresHook(postgres_conn_id='postgres_restaurant')
        
        sql_get_products = """
        SELECT 
            p.id,
            p.nombre,
            p.precio,
            p.descripcion,
            c.nombre as categoria,
            p.activo,
            COALESCE(SUM(dp.cantidad), 0) as total_vendido,
            COALESCE(COUNT(DISTINCT dp.pedido_id), 0) as pedidos_con_producto
        FROM productos p
        JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN detalle_pedidos dp ON p.id = dp.producto_id
        LEFT JOIN pedidos pe ON dp.pedido_id = pe.id AND pe.estado = 'completado'
        GROUP BY p.id, p.nombre, p.precio, p.descripcion, c.nombre, p.activo
        ORDER BY total_vendido DESC
        """
        
        products = pg_hook.get_records(sql_get_products)
        logging.info(f"📦 Productos a indexar: {len(products)}")
        
        # Preparar índice en ElasticSearch
        index_name = "restaurant_products"
        
        # Eliminar índice anterior si existe
        try:
            requests.delete(f'http://elasticsearch:9200/{index_name}')
        except:
            pass
        
        # Crear nuevo índice con mapping
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "nombre": {"type": "text", "analyzer": "spanish"},
                    "precio": {"type": "float"},
                    "descripcion": {"type": "text", "analyzer": "spanish"},
                    "categoria": {"type": "keyword"},
                    "activo": {"type": "boolean"},
                    "total_vendido": {"type": "integer"},
                    "pedidos_con_producto": {"type": "integer"},
                    "popularidad_score": {"type": "float"},
                    "fecha_indexacion": {"type": "date"}
                }
            }
        }
        
        requests.put(f'http://elasticsearch:9200/{index_name}', 
                    json=mapping, headers={'Content-Type': 'application/json'})
        
        # Indexar productos
        indexed_count = 0
        for product in products:
            doc = {
                "id": product[0],
                "nombre": product[1],
                "precio": float(product[2]),
                "descripcion": product[3] or "",
                "categoria": product[4],
                "activo": product[5],
                "total_vendido": product[6],
                "pedidos_con_producto": product[7],
                "popularidad_score": (product[6] * 0.7) + (product[7] * 0.3),
                "fecha_indexacion": datetime.now().isoformat()
            }
            
            response = requests.post(
                f'http://elasticsearch:9200/{index_name}/_doc/{product[0]}',
                json=doc,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201]:
                indexed_count += 1
        
        logging.info(f"✅ Productos indexados: {indexed_count}/{len(products)}")
        
        return {
            'products_indexed': indexed_count,
            'total_products': len(products),
            'index_name': index_name,
            'status': 'success'
        }
        
    except Exception as e:
        logging.error(f"❌ Error reindexando productos: {e}")
        raise

def update_olap_views():
    """Actualizar vistas OLAP para Metabase"""
    logging.info("🔄 Actualizando vistas OLAP...")
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_restaurant')
        
        # Actualizar vista materializada
        refresh_mv_sql = """
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_ingresos_categoria;
        """
        
        pg_hook.run(refresh_mv_sql)
        
        # Actualizar estadísticas de tablas
        analyze_sql = """
        ANALYZE pedidos;
        ANALYZE detalle_pedidos;  
        ANALYZE productos;
        ANALYZE clientes;
        ANALYZE reservas;
        """
        
        pg_hook.run(analyze_sql)
        
        logging.info("✅ Vistas OLAP actualizadas")
        
        return {'status': 'success', 'message': 'OLAP views updated'}
        
    except Exception as e:
        logging.error(f"❌ Error actualizando vistas OLAP: {e}")
        raise

# ===============================================
# DEFINICIÓN DE TAREAS DEL DAG
# ===============================================

# Tarea inicial - Dummy
start_task = DummyOperator(
    task_id='start_pipeline',
    dag=dag
)

# Tarea 1: Verificación de calidad de datos
data_quality_task = PythonOperator(
    task_id='check_data_quality',
    python_callable=check_data_quality,
    dag=dag
)

# Tarea 2: Extracción de datos
extract_data_task = PythonOperator(
    task_id='extract_data_postgres',
    python_callable=extract_data_from_postgres,
    dag=dag
)

# Tarea 3: Crear esquema DWH
create_dwh_task = PythonOperator(
    task_id='create_dwh_schema',
    python_callable=create_data_warehouse_schema,
    dag=dag
)

# Tarea 4: Procesamiento con Spark
spark_processing_task = DockerOperator(
    task_id='spark_transformation',
    image='spark_analytics:latest',
    container_name='airflow_spark_processing',
    docker_url='unix://var/run/docker.sock',
    network_mode='restaurant_network',
    auto_remove=True,
    dag=dag,
    mount_tmp_dir=False
)

# Tarea 5: Verificar ElasticSearch  
check_es_task = PythonOperator(
    task_id='check_elasticsearch',
    python_callable=check_elasticsearch_status,
    dag=dag
)

# Tarea 6: Reindexar productos
reindex_products_task = PythonOperator(
    task_id='reindex_products_elasticsearch',
    python_callable=reindex_products_elasticsearch,
    dag=dag
)

# Tarea 7: Actualizar vistas OLAP
update_views_task = PythonOperator(
    task_id='update_olap_views',
    python_callable=update_olap_views,
    dag=dag
)

# Tarea final - Dummy
end_task = DummyOperator(
    task_id='end_pipeline',
    dag=dag
)

# ===============================================
# DEPENDENCIAS DEL DAG
# ===============================================

# Flujo principal del pipeline
start_task >> data_quality_task >> extract_data_task >> create_dwh_task

# Procesamiento paralelo
create_dwh_task >> [spark_processing_task, check_es_task]

# Spark debe completarse antes de actualizar vistas
spark_processing_task >> update_views_task

# ElasticSearch debe estar OK antes de reindexar
check_es_task >> reindex_products_task

# Ambas ramas convergen al final
[update_views_task, reindex_products_task] >> end_task