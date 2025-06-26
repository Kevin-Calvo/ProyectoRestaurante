"""
Script de configuración inicial para Apache Airflow
===================================================

Este script configura las conexiones necesarias y variables
para el funcionamiento del DAG de orquestación.

Ejecutar después de que Airflow esté funcionando.
"""

import os
import time
from airflow.models import Connection, Variable
from airflow import settings
from sqlalchemy.orm import sessionmaker

def setup_airflow_connections():
    """Configurar conexiones de Airflow"""
    
    # Crear sesión de base de datos
    session = settings.Session()
    
    try:
        # Conexión a PostgreSQL del restaurante
        postgres_conn = Connection(
            conn_id='postgres_restaurant',
            conn_type='postgres',
            host='postgres',
            login='restaurant_user',
            password='restaurant_pass',
            schema='restaurant_db',
            port=5432
        )
        
        # Verificar si la conexión ya existe
        existing_conn = session.query(Connection).filter(
            Connection.conn_id == 'postgres_restaurant'
        ).first()
        
        if existing_conn:
            session.delete(existing_conn)
            
        session.add(postgres_conn)
        session.commit()
        print("✅ Conexión PostgreSQL configurada")
        
        # Conexión a ElasticSearch
        es_conn = Connection(
            conn_id='elasticsearch_default',
            conn_type='elasticsearch',
            host='elasticsearch',
            port=9200
        )
        
        existing_es = session.query(Connection).filter(
            Connection.conn_id == 'elasticsearch_default'
        ).first()
        
        if existing_es:
            session.delete(existing_es)
            
        session.add(es_conn)
        session.commit()
        print("✅ Conexión ElasticSearch configurada")
        
    except Exception as e:
        print(f"❌ Error configurando conexiones: {e}")
        session.rollback()
    finally:
        session.close()

def setup_airflow_variables():
    """Configurar variables de Airflow"""
    
    try:
        # Variables de configuración del pipeline
        variables = {
            'restaurant_pipeline_config': {
                'spark_image': 'spark_analytics:latest',
                'processing_batch_size': 1000,
                'elasticsearch_index': 'restaurant_products',
                'data_retention_days': 365,
                'notification_email': 'admin@restaurant.com'
            },
            'olap_refresh_schedule': {
                'materialized_views': ['mv_dashboard_ingresos_categoria'],
                'analyze_tables': ['pedidos', 'detalle_pedidos', 'productos', 'clientes'],
                'vacuum_tables': ['dwh_fact_ventas', 'dwh_dim_tiempo']
            },
            'data_quality_thresholds': {
                'min_orders_per_day': 1,
                'max_processing_time_minutes': 30,
                'required_categories': 6,
                'min_products_active': 10
            }
        }
        
        for var_name, var_value in variables.items():
            Variable.set(var_name, var_value, serialize_json=True)
            print(f"✅ Variable '{var_name}' configurada")
            
    except Exception as e:
        print(f"❌ Error configurando variables: {e}")

if __name__ == "__main__":
    print("🚀 Configurando Airflow para el pipeline del restaurante...")
    
    # Esperar a que Airflow esté completamente inicializado
    time.sleep(10)
    
    setup_airflow_connections()
    setup_airflow_variables()
    
    print("🎉 Configuración de Airflow completada!")
    print("📊 DAG disponible: restaurant_etl_pipeline")
    print("🔗 Acceder a Airflow UI: http://localhost:8080")
    print("👤 Usuario: admin | Contraseña: admin123")