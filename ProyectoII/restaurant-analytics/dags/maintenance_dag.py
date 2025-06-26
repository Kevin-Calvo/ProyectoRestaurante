"""
DAG de Mantenimiento para el Sistema de Restaurante
==================================================

Este DAG se encarga de tareas de mantenimiento periódico:
- Limpieza de datos antiguos
- Optimización de índices
- Backup de vistas críticas
- Monitoreo de salud del sistema

Programado para ejecutarse diariamente a las 2:00 AM
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import requests
import logging

# Configuración del DAG de mantenimiento
default_args = {
    'owner': 'restaurant-admin',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10)
}

maintenance_dag = DAG(
    'restaurant_maintenance',
    default_args=default_args,
    description='Tareas de mantenimiento del sistema de restaurante',
    schedule_interval='0 2 * * *',  # Diario a las 2:00 AM
    tags=['maintenance', 'cleanup', 'monitoring'],
    catchup=False
)

def system_health_check():
    """Verificar salud general del sistema"""
    logging.info("🏥 Verificando salud del sistema...")
    
    health_report = {
        'timestamp': datetime.now().isoformat(),
        'postgres': 'unknown',
        'elasticsearch': 'unknown',
        'data_freshness': 'unknown'
    }
    
    try:
        # Verificar PostgreSQL
        pg_hook = PostgresHook(postgres_conn_id='postgres_restaurant')
        
        # Verificar última actividad
        sql_last_activity = """
        SELECT 
            MAX(fecha_pedido) as ultimo_pedido,
            COUNT(*) as pedidos_hoy
        FROM pedidos 
        WHERE fecha_pedido >= CURRENT_DATE
        """
        
        activity = pg_hook.get_first(sql_last_activity)
        if activity:
            health_report['postgres'] = 'healthy'
            health_report['data_freshness'] = f"Último pedido: {activity[0]}, Pedidos hoy: {activity[1]}"
        
        # Verificar ElasticSearch
        try:
            es_response = requests.get('http://elasticsearch:9200/_cluster/health', timeout=10)
            if es_response.status_code == 200:
                es_health = es_response.json()
                health_report['elasticsearch'] = es_health.get('status', 'unknown')
            else:
                health_report['elasticsearch'] = 'unhealthy'
        except:
            health_report['elasticsearch'] = 'unreachable'
        
        logging.info(f"📊 Reporte de salud: {health_report}")
        return health_report
        
    except Exception as e:
        logging.error(f"❌ Error en verificación de salud: {e}")
        raise

def cleanup_old_logs():
    """Limpiar logs antiguos del sistema"""
    logging.info("🧹 Limpiando logs antiguos...")
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_restaurant')
        
        # Simular limpieza de logs (en un sistema real, esto sería más complejo)
        cleanup_sql = """
        -- Archivar pedidos muy antiguos (simulación)
        UPDATE pedidos 
        SET estado = 'archivado' 
        WHERE fecha_pedido < CURRENT_DATE - INTERVAL '1 year' 
        AND estado = 'cancelado';
        
        -- Limpiar datos temporales si existieran
        DELETE FROM dwh_fact_ventas 
        WHERE fecha_procesamiento < CURRENT_DATE - INTERVAL '6 months';
        """
        
        pg_hook.run(cleanup_sql)
        logging.info("✅ Limpieza de datos completada")
        
        return {'status': 'success', 'message': 'Old data cleaned'}
        
    except Exception as e:
        logging.error(f"❌ Error en limpieza: {e}")
        raise

def optimize_database():
    """Optimizar índices y estadísticas de la base de datos"""
    logging.info("⚡ Optimizando base de datos...")
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_restaurant')
        
        # Actualizar estadísticas
        analyze_sql = """
        ANALYZE pedidos;
        ANALYZE detalle_pedidos;
        ANALYZE productos;
        ANALYZE clientes;
        ANALYZE reservas;
        ANALYZE categorias;
        """
        
        pg_hook.run(analyze_sql)
        
        # VACUUM en tablas críticas
        vacuum_sql = """
        VACUUM ANALYZE dwh_fact_ventas;
        VACUUM ANALYZE dwh_dim_tiempo;
        """
        
        pg_hook.run(vacuum_sql)
        
        logging.info("✅ Optimización de base de datos completada")
        
        return {'status': 'success', 'message': 'Database optimized'}
        
    except Exception as e:
        logging.error(f"❌ Error en optimización: {e}")
        raise

def backup_critical_views():
    """Backup de vistas críticas del sistema"""
    logging.info("💾 Realizando backup de vistas críticas...")
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_restaurant')
        
        # Crear tabla de backup con timestamp
        backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        backup_sql = f"""
        -- Backup de vista de ingresos por categoría
        CREATE TABLE IF NOT EXISTS backup_ingresos_categoria_{backup_timestamp} AS
        SELECT * FROM vista_olap_ingresos_categoria;
        
        -- Backup de vista de actividad por zona
        CREATE TABLE IF NOT EXISTS backup_actividad_zona_{backup_timestamp} AS
        SELECT * FROM vista_olap_actividad_zona;
        
        -- Backup de estadísticas de pedidos
        CREATE TABLE IF NOT EXISTS backup_estadisticas_{backup_timestamp} AS
        SELECT * FROM vista_olap_estadisticas_pedidos;
        """
        
        pg_hook.run(backup_sql)
        
        # Limpiar backups antiguos (mantener solo los últimos 7 días)
        cleanup_old_backups_sql = """
        DO $$
        DECLARE
            table_name TEXT;
        BEGIN
            FOR table_name IN 
                SELECT tablename 
                FROM pg_tables 
                WHERE tablename LIKE 'backup_%' 
                AND tablename < 'backup_' || to_char(CURRENT_DATE - INTERVAL '7 days', 'YYYYMMDD')
            LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || table_name;
            END LOOP;
        END $$;
        """
        
        pg_hook.run(cleanup_old_backups_sql)
        
        logging.info(f"✅ Backup completado: backup_*_{backup_timestamp}")
        
        return {'status': 'success', 'backup_timestamp': backup_timestamp}
        
    except Exception as e:
        logging.error(f"❌ Error en backup: {e}")
        raise

def generate_daily_report():
    """Generar reporte diario del sistema"""
    logging.info("📊 Generando reporte diario...")
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_restaurant')
        
        # Métricas del día anterior
        daily_metrics_sql = """
        SELECT 
            CURRENT_DATE - INTERVAL '1 day' as fecha_reporte,
            COUNT(*) as pedidos_totales,
            COUNT(CASE WHEN estado = 'completado' THEN 1 END) as pedidos_completados,
            COUNT(CASE WHEN estado = 'cancelado' THEN 1 END) as pedidos_cancelados,
            SUM(CASE WHEN estado = 'completado' THEN total ELSE 0 END) as ingresos_dia,
            COUNT(DISTINCT cliente_id) as clientes_activos,
            AVG(CASE WHEN estado = 'completado' THEN total END) as ticket_promedio
        FROM pedidos 
        WHERE DATE(fecha_pedido) = CURRENT_DATE - INTERVAL '1 day';
        """
        
        daily_metrics = pg_hook.get_first(daily_metrics_sql)
        
        # Productos más vendidos del día
        top_products_sql = """
        SELECT 
            p.nombre,
            SUM(dp.cantidad) as cantidad_vendida,
            SUM(dp.subtotal) as ingresos_producto
        FROM detalle_pedidos dp
        JOIN productos p ON dp.producto_id = p.id
        JOIN pedidos pe ON dp.pedido_id = pe.id
        WHERE DATE(pe.fecha_pedido) = CURRENT_DATE - INTERVAL '1 day'
        AND pe.estado = 'completado'
        GROUP BY p.nombre
        ORDER BY cantidad_vendida DESC
        LIMIT 5;
        """
        
        top_products = pg_hook.get_records(top_products_sql)
        
        report = {
            'fecha': str(daily_metrics[0]) if daily_metrics[0] else 'N/A',
            'pedidos_totales': daily_metrics[1] or 0,
            'pedidos_completados': daily_metrics[2] or 0,
            'pedidos_cancelados': daily_metrics[3] or 0,
            'ingresos_dia': float(daily_metrics[4]) if daily_metrics[4] else 0,
            'clientes_activos': daily_metrics[5] or 0,
            'ticket_promedio': float(daily_metrics[6]) if daily_metrics[6] else 0,
            'productos_top': [{'producto': p[0], 'cantidad': p[1], 'ingresos': float(p[2])} for p in top_products]
        }
        
        logging.info(f"📈 Reporte diario generado: {report}")
        
        return report
        
    except Exception as e:
        logging.error(f"❌ Error generando reporte: {e}")
        raise

# ===============================================
# DEFINICIÓN DE TAREAS DEL DAG DE MANTENIMIENTO
# ===============================================

# Verificación de salud del sistema
health_check_task = PythonOperator(
    task_id='system_health_check',
    python_callable=system_health_check,
    dag=maintenance_dag
)

# Limpieza de datos antiguos
cleanup_task = PythonOperator(
    task_id='cleanup_old_data',
    python_callable=cleanup_old_logs,
    dag=maintenance_dag
)

# Optimización de base de datos
optimize_task = PythonOperator(
    task_id='optimize_database',
    python_callable=optimize_database,
    dag=maintenance_dag
)

# Backup de vistas críticas
backup_task = PythonOperator(
    task_id='backup_critical_views',
    python_callable=backup_critical_views,
    dag=maintenance_dag
)

# Refresco de vistas materializadas
refresh_views_task = PostgresOperator(
    task_id='refresh_materialized_views',
    postgres_conn_id='postgres_restaurant',
    sql="""
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_ingresos_categoria;
    """,
    dag=maintenance_dag
)

# Generación de reporte diario
report_task = PythonOperator(
    task_id='generate_daily_report',
    python_callable=generate_daily_report,
    dag=maintenance_dag
)

# Verificación de espacio en disco (simulada)
disk_check_task = BashOperator(
    task_id='check_disk_space',
    bash_command="""
    echo "🗂️ Verificando espacio en disco..."
    df -h
    echo "✅ Verificación de espacio completada"
    """,
    dag=maintenance_dag
)

# ===============================================
# DEPENDENCIAS DEL DAG DE MANTENIMIENTO
# ===============================================

# Verificación inicial
health_check_task >> [cleanup_task, optimize_task, backup_task]

# Optimización y limpieza en paralelo
[cleanup_task, optimize_task] >> refresh_views_task

# Backup y refresco de vistas antes del reporte
[backup_task, refresh_views_task] >> report_task

# Verificación final de disco
report_task >> disk_check_task