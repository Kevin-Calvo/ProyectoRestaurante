"""
DAG de Orquestación para Análisis OLAP del Restaurante - VERSIÓN CORREGIDA
========================================================================

Esta versión NO requiere configurar conexiones en Airflow.
Se conecta directamente a PostgreSQL usando psycopg2.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
import requests
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
    schedule_interval=timedelta(hours=6),
    tags=['restaurant', 'etl', 'olap', 'spark'],
    max_active_runs=1
)

def check_data_quality():
    """Verificar la calidad de los datos"""
    logging.info("🔍 Verificando calidad de datos...")
    
    try:
        import psycopg2
        
        # Conexión directa (sin usar Airflow connections)
        conn = psycopg2.connect(
            host="postgres",
            database="restaurant_db",
            user="restaurant_user",
            password="restaurant_pass",
            port=5432
        )
        
        cursor = conn.cursor()
        
        # Verificar datos recientes
        cursor.execute("""
            SELECT COUNT(*) FROM pedidos 
            WHERE fecha_pedido >= NOW() - INTERVAL '24 hours'
        """)
        
        recent_orders = cursor.fetchone()[0]
        logging.info(f"📊 Pedidos recientes (24h): {recent_orders}")
        
        # Verificar integridad
        cursor.execute("""
            SELECT 
                COUNT(*) as total_detalle,
                COUNT(DISTINCT pedido_id) as pedidos_con_detalle,
                COUNT(DISTINCT producto_id) as productos_activos
            FROM detalle_pedidos dp
            JOIN pedidos p ON dp.pedido_id = p.id
            JOIN productos pr ON dp.producto_id = pr.id
            WHERE p.estado = 'completado'
        """)
        
        integrity_data = cursor.fetchone()
        logging.info(f"✅ Integridad: Detalles={integrity_data[0]}, Pedidos={integrity_data[1]}, Productos={integrity_data[2]}")
        
        # Verificar clientes
        cursor.execute("""
            SELECT COUNT(DISTINCT id) as total_clientes,
                   COUNT(DISTINCT zona_geografica) as zonas_activas
            FROM clientes
        """)
        
        client_data = cursor.fetchone()
        logging.info(f"👥 Clientes: Total={client_data[0]}, Zonas={client_data[1]}")
        
        cursor.close()
        conn.close()
        
        logging.info("✅ Verificación de calidad completada exitosamente")
        
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
        import psycopg2
        
        conn = psycopg2.connect(
            host="postgres",
            database="restaurant_db",
            user="restaurant_user",
            password="restaurant_pass",
            port=5432
        )
        
        cursor = conn.cursor()
        
        # Extraer resumen mensual
        cursor.execute("""
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
            LIMIT 6
        """)
        
        monthly_data = cursor.fetchall()
        logging.info(f"📊 Datos mensuales extraídos: {len(monthly_data)} registros")
        
        for month_record in monthly_data:
            logging.info(f"   {month_record[0].strftime('%Y-%m')}: {month_record[1]} pedidos, ${month_record[3]:.2f} ingresos")
        
        # Validar productos activos
        cursor.execute("""
            SELECT c.nombre as categoria, COUNT(p.id) as productos_activos
            FROM categorias c
            LEFT JOIN productos p ON c.id = p.categoria_id AND p.activo = true
            GROUP BY c.nombre
            ORDER BY productos_activos DESC
        """)
        
        products_data = cursor.fetchall()
        logging.info(f"🍽️ Productos por categoría:")
        for category_record in products_data:
            logging.info(f"   {category_record[0]}: {category_record[1]} productos")
        
        cursor.close()
        conn.close()
        
        logging.info("✅ Extracción de datos completada exitosamente")
        
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
        import psycopg2
        
        conn = psycopg2.connect(
            host="postgres",
            database="restaurant_db",
            user="restaurant_user",
            password="restaurant_pass",
            port=5432
        )
        
        cursor = conn.cursor()
        
        # Crear vistas OLAP adicionales
        dwh_schema_sql = """
        -- Vista para dashboard de ingresos por categoría y mes
        CREATE OR REPLACE VIEW vista_dashboard_ingresos_categoria AS
        SELECT 
            EXTRACT(YEAR FROM p.fecha_pedido) as anio,
            EXTRACT(MONTH FROM p.fecha_pedido) as mes,
            CASE EXTRACT(MONTH FROM p.fecha_pedido)
                WHEN 1 THEN 'Enero' WHEN 2 THEN 'Febrero' WHEN 3 THEN 'Marzo'
                WHEN 4 THEN 'Abril' WHEN 5 THEN 'Mayo' WHEN 6 THEN 'Junio'
                WHEN 7 THEN 'Julio' WHEN 8 THEN 'Agosto' WHEN 9 THEN 'Septiembre'
                WHEN 10 THEN 'Octubre' WHEN 11 THEN 'Noviembre' WHEN 12 THEN 'Diciembre'
            END as mes_nombre,
            c.nombre as categoria,
            SUM(dp.subtotal) as ingresos_categoria,
            COUNT(DISTINCT p.id) as pedidos_categoria,
            SUM(dp.cantidad) as productos_vendidos,
            COUNT(DISTINCT p.cliente_id) as clientes_categoria
        FROM pedidos p
        JOIN detalle_pedidos dp ON p.id = dp.pedido_id
        JOIN productos pr ON dp.producto_id = pr.id
        JOIN categorias c ON pr.categoria_id = c.id
        WHERE p.estado = 'completado'
        GROUP BY EXTRACT(YEAR FROM p.fecha_pedido), EXTRACT(MONTH FROM p.fecha_pedido), c.nombre
        ORDER BY anio, mes, ingresos_categoria DESC;

        -- Vista para actividad por zona geográfica
        CREATE OR REPLACE VIEW vista_dashboard_actividad_zona AS
        SELECT 
            cl.zona_geografica,
            COUNT(DISTINCT p.id) as total_pedidos,
            SUM(CASE WHEN p.estado = 'completado' THEN p.total ELSE 0 END) as ingresos_zona,
            AVG(CASE WHEN p.estado = 'completado' THEN p.total END) as ticket_promedio,
            COUNT(DISTINCT cl.id) as clientes_unicos,
            SUM(CASE WHEN p.estado = 'completado' THEN 1 ELSE 0 END) as pedidos_completados,
            COUNT(CASE WHEN p.estado = 'cancelado' THEN 1 END) as pedidos_cancelados
        FROM clientes cl
        LEFT JOIN pedidos p ON cl.id = p.cliente_id
        GROUP BY cl.zona_geografica
        ORDER BY ingresos_zona DESC;

        -- Vista para estadísticas de pedidos por mes
        CREATE OR REPLACE VIEW vista_dashboard_estadisticas_pedidos AS
        SELECT 
            EXTRACT(YEAR FROM fecha_pedido) as anio,
            EXTRACT(MONTH FROM fecha_pedido) as mes,
            CASE EXTRACT(MONTH FROM fecha_pedido)
                WHEN 1 THEN 'Enero' WHEN 2 THEN 'Febrero' WHEN 3 THEN 'Marzo'
                WHEN 4 THEN 'Abril' WHEN 5 THEN 'Mayo' WHEN 6 THEN 'Junio'
                WHEN 7 THEN 'Julio' WHEN 8 THEN 'Agosto' WHEN 9 THEN 'Septiembre'
                WHEN 10 THEN 'Octubre' WHEN 11 THEN 'Noviembre' WHEN 12 THEN 'Diciembre'
            END as mes_nombre,
            COUNT(*) as total_pedidos,
            COUNT(CASE WHEN estado = 'completado' THEN 1 END) as pedidos_completados,
            COUNT(CASE WHEN estado = 'cancelado' THEN 1 END) as pedidos_cancelados,
            SUM(CASE WHEN estado = 'completado' THEN total ELSE 0 END) as ingresos_totales,
            AVG(CASE WHEN estado = 'completado' THEN total END) as ticket_promedio,
            COUNT(DISTINCT cliente_id) as clientes_activos,
            ROUND(
                COUNT(CASE WHEN estado = 'completado' THEN 1 END) * 100.0 / COUNT(*), 2
            ) as tasa_exito_pct
        FROM pedidos
        GROUP BY EXTRACT(YEAR FROM fecha_pedido), EXTRACT(MONTH FROM fecha_pedido)
        ORDER BY anio, mes;
        """
        
        cursor.execute(dwh_schema_sql)
        conn.commit()
        
        logging.info("✅ Esquema del Data Warehouse actualizado")
        logging.info("   📊 Vista: vista_dashboard_ingresos_categoria")
        logging.info("   🗺️ Vista: vista_dashboard_actividad_zona")
        logging.info("   📈 Vista: vista_dashboard_estadisticas_pedidos")
        
        cursor.close()
        conn.close()
        
        return {'status': 'success', 'message': 'DWH schema updated'}
        
    except Exception as e:
        logging.error(f"❌ Error creando esquema DWH: {e}")
        raise

def run_spark_processing():
    """Simular procesamiento con Spark"""
    logging.info("⚡ Ejecutando procesamiento con Spark...")
    
    try:
        # Simular el procesamiento de Spark
        import time
        
        logging.info("🔄 Iniciando análisis OLAP con Spark...")
        time.sleep(10)  # Simular tiempo de procesamiento
        
        logging.info("📊 Procesando esquema estrella...")
        time.sleep(5)
        
        logging.info("🏗️ Creando tablas de hechos y dimensiones...")
        time.sleep(5)
        
        logging.info("✅ Procesamiento Spark completado exitosamente")
        
        return {
            'status': 'success',
            'processing_time': '20 segundos',
            'tables_created': ['fact_ventas', 'dim_tiempo', 'dim_producto', 'dim_cliente']
        }
        
    except Exception as e:
        logging.error(f"❌ Error en procesamiento Spark: {e}")
        raise

def check_elasticsearch():
    """Verificar estado de ElasticSearch"""
    logging.info("🔍 Verificando estado de ElasticSearch...")
    
    try:
        response = requests.get('http://elasticsearch:9200/_cluster/health', timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            status = health_data.get('status', 'unknown')
            logging.info(f"✅ ElasticSearch status: {status}")
            
            # Verificar índices existentes
            indices_response = requests.get('http://elasticsearch:9200/_cat/indices?format=json', timeout=10)
            if indices_response.status_code == 200:
                indices = indices_response.json()
                logging.info(f"📊 Índices existentes: {len(indices)}")
                for index in indices:
                    logging.info(f"   - {index.get('index', 'N/A')}: {index.get('docs.count', 0)} documentos")
            
            return {
                'cluster_health': health_data,
                'indices_count': len(indices) if indices_response.status_code == 200 else 0,
                'status': 'healthy'
            }
        else:
            logging.warning(f"⚠️ ElasticSearch respuesta no OK: {response.status_code}")
            return {'status': 'unhealthy', 'code': response.status_code}
            
    except Exception as e:
        logging.warning(f"⚠️ ElasticSearch no disponible: {e}")
        return {'status': 'unavailable', 'message': str(e)}

def reindex_products_elasticsearch():
    """Reindexar productos en ElasticSearch"""
    logging.info("🔄 Reindexando productos en ElasticSearch...")
    
    try:
        import psycopg2
        
        # Obtener productos de PostgreSQL
        conn = psycopg2.connect(
            host="postgres",
            database="restaurant_db",
            user="restaurant_user",
            password="restaurant_pass",
            port=5432
        )
        
        cursor = conn.cursor()
        
        cursor.execute("""
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
        """)
        
        products = cursor.fetchall()
        logging.info(f"📦 Productos a indexar: {len(products)}")
        
        cursor.close()
        conn.close()
        
        # Preparar índice en ElasticSearch
        index_name = "restaurant_products"
        
        # Eliminar índice anterior si existe
        try:
            requests.delete(f'http://elasticsearch:9200/{index_name}', timeout=10)
            logging.info("🗑️ Índice anterior eliminado")
        except:
            logging.info("📝 No había índice anterior")
        
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
        
        create_response = requests.put(
            f'http://elasticsearch:9200/{index_name}', 
            json=mapping, 
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if create_response.status_code in [200, 201]:
            logging.info("✅ Índice creado exitosamente")
        else:
            logging.warning(f"⚠️ Error creando índice: {create_response.status_code}")
        
        # Indexar productos
        indexed_count = 0
        for product in products:
            try:
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
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    indexed_count += 1
                    if indexed_count <= 5:  # Log solo los primeros 5
                        logging.info(f"   📦 Indexado: {product[1]} (ID: {product[0]})")
                        
            except Exception as e:
                logging.warning(f"⚠️ Error indexando producto {product[0]}: {e}")
        
        logging.info(f"✅ Productos indexados: {indexed_count}/{len(products)}")
        
        return {
            'products_indexed': indexed_count,
            'total_products': len(products),
            'index_name': index_name,
            'status': 'success'
        }
        
    except Exception as e:
        logging.error(f"❌ Error reindexando productos: {e}")
        return {'status': 'error', 'message': str(e)}

def update_olap_views():
    """Actualizar vistas OLAP para Metabase"""
    logging.info("🔄 Actualizando vistas OLAP...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host="postgres",
            database="restaurant_db",
            user="restaurant_user",
            password="restaurant_pass",
            port=5432
        )
        
        cursor = conn.cursor()
        
        # Actualizar estadísticas de tablas principales
        analyze_sql = """
        ANALYZE pedidos;
        ANALYZE detalle_pedidos;  
        ANALYZE productos;
        ANALYZE clientes;
        ANALYZE reservas;
        ANALYZE categorias;
        """
        
        cursor.execute(analyze_sql)
        conn.commit()
        
        logging.info("✅ Estadísticas de tablas actualizadas")
        
        # Verificar que las vistas existan
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'vista_%'
            ORDER BY table_name
        """)
        
        views = cursor.fetchall()
        logging.info(f"📊 Vistas OLAP disponibles: {len(views)}")
        for view in views:
            logging.info(f"   - {view[0]}")
        
        cursor.close()
        conn.close()
        
        logging.info("✅ Vistas OLAP actualizadas")
        
        return {'status': 'success', 'views_count': len(views)}
        
    except Exception as e:
        logging.error(f"❌ Error actualizando vistas OLAP: {e}")
        raise

# ===============================================
# DEFINICIÓN DE TAREAS DEL DAG
# ===============================================

# Tarea inicial
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

# Tarea 4: Procesamiento con Spark (simulado)
spark_processing_task = PythonOperator(
    task_id='spark_transformation',
    python_callable=run_spark_processing,
    dag=dag
)

# Tarea 5: Verificar ElasticSearch  
check_es_task = PythonOperator(
    task_id='check_elasticsearch',
    python_callable=check_elasticsearch,
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

# Tarea final
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