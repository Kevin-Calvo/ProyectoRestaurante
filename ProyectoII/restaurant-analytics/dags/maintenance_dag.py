"""
DAG de Mantenimiento para el Sistema de Restaurante - VERSIÓN CORREGIDA
======================================================================

Esta versión NO requiere configurar conexiones en Airflow.
Se conecta directamente a PostgreSQL usando psycopg2.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import requests
import logging

default_args = {
    'owner': 'restaurant-admin',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10)
}

maintenance_dag = DAG(
    'restaurant_maintenance',
    default_args=default_args,
    description='Tareas de mantenimiento del sistema',
    schedule_interval='0 2 * * *',  # Diario a las 2:00 AM
    tags=['maintenance', 'cleanup'],
    catchup=False
)

def system_health_check():
    """Verificar salud del sistema"""
    logging.info("🏥 Verificando salud del sistema...")
    
    health_report = {
        'timestamp': datetime.now().isoformat(),
        'postgres': 'unknown',
        'elasticsearch': 'unknown',
        'data_freshness': 'unknown'
    }
    
    try:
        import psycopg2
        
        # Conexión directa a PostgreSQL
        conn = psycopg2.connect(
            host="postgres",
            database="restaurant_db",
            user="restaurant_user",
            password="restaurant_pass",
            port=5432
        )
        
        cursor = conn.cursor()
        
        # Verificar última actividad
        cursor.execute("""
            SELECT 
                MAX(fecha_pedido) as ultimo_pedido,
                COUNT(*) as pedidos_hoy
            FROM pedidos 
            WHERE fecha_pedido >= CURRENT_DATE
        """)
        
        activity = cursor.fetchone()
        if activity:
            health_report['postgres'] = 'healthy'
            health_report['data_freshness'] = f"Último pedido: {activity[0]}, Pedidos hoy: {activity[1]}"
            logging.info(f"📊 Actividad hoy: {activity[1]} pedidos")
            logging.info(f"📅 Último pedido: {activity[0]}")
        
        # Verificar estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_pedidos,
                COUNT(CASE WHEN estado = 'completado' THEN 1 END) as completados,
                COUNT(CASE WHEN estado = 'cancelado' THEN 1 END) as cancelados,
                COUNT(DISTINCT cliente_id) as clientes_unicos
            FROM pedidos
        """)
        
        stats = cursor.fetchone()
        logging.info(f"📈 Estadísticas generales:")
        logging.info(f"   Total pedidos: {stats[0]}")
        logging.info(f"   Completados: {stats[1]}")
        logging.info(f"   Cancelados: {stats[2]}")
        logging.info(f"   Clientes únicos: {stats[3]}")
        
        cursor.close()
        conn.close()
        
        # Verificar ElasticSearch
        try:
            es_response = requests.get('http://elasticsearch:9200/_cluster/health', timeout=10)
            if es_response.status_code == 200:
                es_health = es_response.json()
                health_report['elasticsearch'] = es_health.get('status', 'unknown')
                logging.info(f"🔍 ElasticSearch: {health_report['elasticsearch']}")
            else:
                health_report['elasticsearch'] = 'unhealthy'
                logging.warning(f"⚠️ ElasticSearch unhealthy: {es_response.status_code}")
        except Exception as es_error:
            health_report['elasticsearch'] = 'unreachable'
            logging.warning(f"⚠️ ElasticSearch unreachable: {es_error}")
        
        logging.info(f"✅ Reporte de salud completo: {health_report}")
        return health_report
        
    except Exception as e:
        logging.error(f"❌ Error en verificación de salud: {e}")
        health_report['postgres'] = 'error'
        health_report['error'] = str(e)
        return health_report

def cleanup_old_data():
    """Limpiar datos antiguos del sistema"""
    logging.info("🧹 Limpiando datos antiguos...")
    
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
        
        # Archivar pedidos cancelados muy antiguos
        cursor.execute("""
            UPDATE pedidos 
            SET estado = 'archivado' 
            WHERE fecha_pedido < CURRENT_DATE - INTERVAL '6 months' 
            AND estado = 'cancelado'
        """)
        
        archived_orders = cursor.rowcount
        logging.info(f"📦 Pedidos archivados: {archived_orders}")
        
        # Limpiar logs simulados (en un sistema real sería más complejo)
        cleanup_simulation = {
            'logs_cleaned': 0,
            'temp_files_removed': 0,
            'archived_orders': archived_orders
        }
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logging.info("✅ Limpieza de datos completada")
        logging.info(f"   Pedidos archivados: {archived_orders}")
        
        return {'status': 'success', 'cleanup_stats': cleanup_simulation}
        
    except Exception as e:
        logging.error(f"❌ Error en limpieza: {e}")
        return {'status': 'error', 'message': str(e)}

def optimize_database():
    """Optimizar índices y estadísticas de la base de datos"""
    logging.info("⚡ Optimizando base de datos...")
    
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
        
        # Actualizar estadísticas de todas las tablas principales
        tables_to_analyze = [
            'pedidos', 'detalle_pedidos', 'productos', 
            'clientes', 'reservas', 'categorias'
        ]
        
        for table in tables_to_analyze:
            cursor.execute(f"ANALYZE {table};")
            logging.info(f"   📊 Analizando tabla: {table}")
        
        # Obtener estadísticas de tamaño de tablas
        cursor.execute("""
            SELECT 
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """)
        
        table_sizes = cursor.fetchall()
        logging.info("📊 Tamaños de tablas:")
        for table_name, size in table_sizes:
            logging.info(f"   {table_name}: {size}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logging.info("✅ Optimización de base de datos completada")
        
        return {
            'status': 'success', 
            'tables_analyzed': len(tables_to_analyze),
            'table_sizes': table_sizes
        }
        
    except Exception as e:
        logging.error(f"❌ Error en optimización: {e}")
        return {'status': 'error', 'message': str(e)}

def backup_critical_views():
    """Backup de vistas críticas del sistema"""
    logging.info("💾 Realizando backup de vistas críticas...")
    
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
        
        # Crear tabla de backup con timestamp
        backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup de vistas principales
        views_to_backup = [
            'vista_ingresos_mes_categoria',
            'vista_actividad_clientes_zona',
            'vista_estadisticas_pedidos'
        ]
        
        backed_up_views = []
        
        for view_name in views_to_backup:
            try:
                backup_table_name = f"backup_{view_name}_{backup_timestamp}"
                
                # Verificar si la vista existe
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.views 
                    WHERE table_name = %s AND table_schema = 'public'
                """, (view_name,))
                
                if cursor.fetchone()[0] > 0:
                    # Crear backup
                    cursor.execute(f"""
                        CREATE TABLE {backup_table_name} AS 
                        SELECT * FROM {view_name}
                    """)
                    
                    # Obtener cantidad de registros
                    cursor.execute(f"SELECT COUNT(*) FROM {backup_table_name}")
                    record_count = cursor.fetchone()[0]
                    
                    backed_up_views.append({
                        'view': view_name,
                        'backup_table': backup_table_name,
                        'records': record_count
                    })
                    
                    logging.info(f"   💾 {view_name} → {backup_table_name} ({record_count} registros)")
                else:
                    logging.warning(f"   ⚠️ Vista {view_name} no encontrada")
                    
            except Exception as view_error:
                logging.error(f"   ❌ Error backing up {view_name}: {view_error}")
        
        # Limpiar backups antiguos (mantener solo los últimos 7 días)
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE tablename LIKE 'backup_%' 
            AND tablename < 'backup_' || to_char(CURRENT_DATE - INTERVAL '7 days', 'YYYYMMDD')
            AND schemaname = 'public'
        """)
        
        old_backups = cursor.fetchall()
        
        for (old_backup,) in old_backups:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {old_backup}")
                logging.info(f"   🗑️ Backup antiguo eliminado: {old_backup}")
            except Exception as drop_error:
                logging.warning(f"   ⚠️ Error eliminando {old_backup}: {drop_error}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logging.info(f"✅ Backup completado: {len(backed_up_views)} vistas respaldadas")
        
        return {
            'status': 'success', 
            'backup_timestamp': backup_timestamp,
            'backed_up_views': backed_up_views,
            'old_backups_cleaned': len(old_backups)
        }
        
    except Exception as e:
        logging.error(f"❌ Error en backup: {e}")
        return {'status': 'error', 'message': str(e)}

def generate_daily_report():
    """Generar reporte diario del sistema"""
    logging.info("📊 Generando reporte diario...")
    
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
        
        # Métricas del día anterior
        cursor.execute("""
            SELECT 
                CURRENT_DATE - INTERVAL '1 day' as fecha_reporte,
                COUNT(*) as pedidos_totales,
                COUNT(CASE WHEN estado = 'completado' THEN 1 END) as pedidos_completados,
                COUNT(CASE WHEN estado = 'cancelado' THEN 1 END) as pedidos_cancelados,
                SUM(CASE WHEN estado = 'completado' THEN total ELSE 0 END) as ingresos_dia,
                COUNT(DISTINCT cliente_id) as clientes_activos,
                AVG(CASE WHEN estado = 'completado' THEN total END) as ticket_promedio
            FROM pedidos 
            WHERE DATE(fecha_pedido) = CURRENT_DATE - INTERVAL '1 day'
        """)
        
        daily_metrics = cursor.fetchone()
        
        # Productos más vendidos del día anterior
        cursor.execute("""
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
            LIMIT 5
        """)
        
        top_products = cursor.fetchall()
        
        # Actividad por zona del día anterior
        cursor.execute("""
            SELECT 
                c.zona_geografica,
                COUNT(p.id) as pedidos_zona,
                SUM(CASE WHEN p.estado = 'completado' THEN p.total ELSE 0 END) as ingresos_zona
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            WHERE DATE(p.fecha_pedido) = CURRENT_DATE - INTERVAL '1 day'
            GROUP BY c.zona_geografica
            ORDER BY pedidos_zona DESC
        """)
        
        zone_activity = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Construir reporte
        report = {
            'fecha': str(daily_metrics[0]) if daily_metrics[0] else 'N/A',
            'pedidos_totales': daily_metrics[1] or 0,
            'pedidos_completados': daily_metrics[2] or 0,
            'pedidos_cancelados': daily_metrics[3] or 0,
            'ingresos_dia': float(daily_metrics[4]) if daily_metrics[4] else 0,
            'clientes_activos': daily_metrics[5] or 0,
            'ticket_promedio': float(daily_metrics[6]) if daily_metrics[6] else 0,
            'productos_top': [
                {'producto': p[0], 'cantidad': p[1], 'ingresos': float(p[2])} 
                for p in top_products
            ],
            'actividad_por_zona': [
                {'zona': z[0], 'pedidos': z[1], 'ingresos': float(z[2])} 
                for z in zone_activity
            ]
        }
        
        # Log del reporte
        logging.info("📈 REPORTE DIARIO GENERADO")
        logging.info("=" * 50)
        logging.info(f"📅 Fecha: {report['fecha']}")
        logging.info(f"📊 Pedidos totales: {report['pedidos_totales']}")
        logging.info(f"✅ Pedidos completados: {report['pedidos_completados']}")
        logging.info(f"❌ Pedidos cancelados: {report['pedidos_cancelados']}")
        logging.info(f"💰 Ingresos del día: ${report['ingresos_dia']:.2f}")
        logging.info(f"👥 Clientes activos: {report['clientes_activos']}")
        logging.info(f"🎫 Ticket promedio: ${report['ticket_promedio']:.2f}")
        
        if report['productos_top']:
            logging.info("🏆 Top productos:")
            for i, product in enumerate(report['productos_top'], 1):
                logging.info(f"   {i}. {product['producto']}: {product['cantidad']} unidades")
        
        if report['actividad_por_zona']:
            logging.info("🗺️ Actividad por zona:")
            for zone in report['actividad_por_zona']:
                logging.info(f"   {zone['zona']}: {zone['pedidos']} pedidos, ${zone['ingresos']:.2f}")
        
        logging.info("=" * 50)
        
        return report
        
    except Exception as e:
        logging.error(f"❌ Error generando reporte: {e}")
        return {'status': 'error', 'message': str(e)}

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
    python_callable=cleanup_old_data,
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
    echo "📊 Uso de memoria:"
    free -h
    echo "✅ Verificación de recursos completada"
    """,
    dag=maintenance_dag
)

# ===============================================
# DEPENDENCIAS DEL DAG DE MANTENIMIENTO
# ===============================================

# Verificación inicial
health_check_task >> [cleanup_task, optimize_task, backup_task]

# Optimización y limpieza en paralelo, luego reporte
[cleanup_task, optimize_task, backup_task] >> report_task

# Verificación final de recursos
report_task >> disk_check_task