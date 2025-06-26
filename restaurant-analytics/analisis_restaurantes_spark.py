from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import pandas as pd
from datetime import datetime, timedelta
import psycopg2
import time
from psycopg2 import OperationalError

# ===============================================
# CONFIGURACIÓN INICIAL DE SPARK
# ===============================================

spark = SparkSession.builder \
    .appName("RestaurantOLAPAnalysis") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("🚀 INICIANDO ANÁLISIS OLAP CON APACHE SPARK")
print("=" * 80)

# ===============================================
# FUNCIÓN PARA ESPERAR POSTGRESQL
# ===============================================

def wait_for_postgres():
    max_attempts = 12
    attempt = 0
    while attempt < max_attempts:
        try:
            conn = psycopg2.connect(
                dbname="restaurant_db",
                user="restaurant_user",
                password="restaurant_pass",
                host="postgres",
                port="5432"
            )
            cursor = conn.cursor()
            
            # Verificar si las tablas críticas existen
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('categorias', 'productos', 'clientes', 'pedidos', 'detalle_pedidos', 'reservas')
            """)
            table_count = cursor.fetchone()[0]
            
            if table_count == 6:
                print("✅ PostgreSQL está completamente inicializado con todas las tablas")
                cursor.close()
                conn.close()
                return True
            
            cursor.close()
            conn.close()
        except OperationalError as e:
            print(f"⚠️  Intento {attempt+1}/{max_attempts}: {e}")
        
        print(f"⏳ Esperando PostgreSQL... intento {attempt+1}/{max_attempts}")
        attempt += 1
        time.sleep(10)
    
    return False

# Esperar a que PostgreSQL esté listo
if not wait_for_postgres():
    print("❌ Error crítico: PostgreSQL no está disponible")
    spark.stop()
    exit(1)

# ===============================================
# CONEXIÓN Y LECTURA DE DATOS
# ===============================================

jdbc_url = "jdbc:postgresql://postgres:5432/restaurant_db"
properties = {
    "user": "restaurant_user",
    "password": "restaurant_pass",
    "driver": "org.postgresql.Driver",
    "fetchsize": "1000"
}

print("📊 Conectando y leyendo datos desde PostgreSQL...")

try:
    # Leer todas las tablas
    df_categorias = spark.read.jdbc(url=jdbc_url, table="categorias", properties=properties)
    df_productos = spark.read.jdbc(url=jdbc_url, table="productos", properties=properties)
    df_clientes = spark.read.jdbc(url=jdbc_url, table="clientes", properties=properties)
    df_pedidos = spark.read.jdbc(url=jdbc_url, table="pedidos", properties=properties)
    df_detalle_pedidos = spark.read.jdbc(url=jdbc_url, table="detalle_pedidos", properties=properties)
    df_reservas = spark.read.jdbc(url=jdbc_url, table="reservas", properties=properties)
    
    # Cachear para mejor rendimiento
    df_categorias.cache()
    df_productos.cache()
    df_clientes.cache()
    df_pedidos.cache()
    df_detalle_pedidos.cache()
    df_reservas.cache()
    
    print("✅ Datos leídos exitosamente:")
    print(f"   - Categorías: {df_categorias.count()} registros")
    print(f"   - Productos: {df_productos.count()} registros")
    print(f"   - Clientes: {df_clientes.count()} registros")
    print(f"   - Pedidos: {df_pedidos.count()} registros")
    print(f"   - Detalle pedidos: {df_detalle_pedidos.count()} registros")
    print(f"   - Reservas: {df_reservas.count()} registros")
    
except Exception as e:
    print(f"❌ Error al conectar con PostgreSQL: {e}")
    spark.stop()
    exit(1)

# ===============================================
# CREACIÓN DEL ESQUEMA ESTRELLA (DATA WAREHOUSE)
# ===============================================

print("\n🏗️  CREANDO ESQUEMA ESTRELLA PARA OLAP")
print("=" * 60)

# TABLA DE HECHOS (FACT TABLE) - Ventas
fact_ventas = df_detalle_pedidos \
    .join(df_pedidos, df_detalle_pedidos.pedido_id == df_pedidos.id, "inner") \
    .join(df_productos, df_detalle_pedidos.producto_id == df_productos.id, "inner") \
    .join(df_categorias, df_productos.categoria_id == df_categorias.id, "inner") \
    .join(df_clientes, df_pedidos.cliente_id == df_clientes.id, "inner") \
    .select(
        col("pedido_id").alias("pedido_key"),
        col("producto_id").alias("producto_key"),
        df_pedidos["cliente_id"].alias("cliente_key"),
        df_categorias["id"].alias("categoria_key"),
        to_date(df_pedidos["fecha_pedido"]).alias("fecha_key"),
        col("cantidad"),
        col("precio_unitario"),
        col("subtotal"),
        df_pedidos["total"].alias("total_pedido"),
        df_pedidos["estado"],
        df_pedidos["zona_entrega"]
    ) \
    .filter(col("estado") == "completado")

# DIMENSIÓN TIEMPO
dim_tiempo = df_pedidos \
    .select(
        to_date(col("fecha_pedido")).alias("fecha_key"),
        year(col("fecha_pedido")).alias("anio"),
        month(col("fecha_pedido")).alias("mes"),
        dayofmonth(col("fecha_pedido")).alias("dia"),
        dayofweek(col("fecha_pedido")).alias("dia_semana"),
        quarter(col("fecha_pedido")).alias("trimestre"),
        hour(col("fecha_pedido")).alias("hora"),
        when(col("mes").between(1, 3), "Q1")
        .when(col("mes").between(4, 6), "Q2")
        .when(col("mes").between(7, 9), "Q3")
        .otherwise("Q4").alias("trimestre_nombre"),
        when(col("mes") == 1, "Enero")
        .when(col("mes") == 2, "Febrero")
        .when(col("mes") == 3, "Marzo")
        .when(col("mes") == 4, "Abril")
        .when(col("mes") == 5, "Mayo")
        .when(col("mes") == 6, "Junio")
        .otherwise("Otro").alias("mes_nombre"),
        when(dayofweek(col("fecha_pedido")).isin([1, 7]), "Fin de Semana")
        .otherwise("Día Laboral").alias("tipo_dia")
    ) \
    .distinct()

# DIMENSIÓN PRODUCTO
dim_producto = df_productos \
    .join(df_categorias, df_productos.categoria_id == df_categorias.id, "inner") \
    .select(
        df_productos["id"].alias("producto_key"),
        df_productos["nombre"].alias("producto_nombre"),
        df_productos["precio"].alias("producto_precio"),
        df_productos["descripcion"].alias("producto_descripcion"),
        df_categorias["id"].alias("categoria_key"),
        df_categorias["nombre"].alias("categoria_nombre"),
        df_categorias["descripcion"].alias("categoria_descripcion")
    )

# DIMENSIÓN CLIENTE
dim_cliente = df_clientes.select(
    col("id").alias("cliente_key"),
    col("nombre").alias("cliente_nombre"),
    col("email").alias("cliente_email"),
    col("zona_geografica").alias("cliente_zona"),
    col("fecha_registro").alias("cliente_fecha_registro")
)

# DIMENSIÓN GEOGRAFÍA
dim_geografia = df_clientes \
    .select("zona_geografica") \
    .distinct() \
    .withColumn("zona_key", monotonically_increasing_id()) \
    .select(
        col("zona_key"),
        col("zona_geografica").alias("zona_nombre"),
        col("zona_geografica").alias("region")
    )

# Registrar tablas temporales
fact_ventas.createOrReplaceTempView("fact_ventas")
dim_tiempo.createOrReplaceTempView("dim_tiempo")
dim_producto.createOrReplaceTempView("dim_producto")
dim_cliente.createOrReplaceTempView("dim_cliente")
dim_geografia.createOrReplaceTempView("dim_geografia")

print("✅ Esquema estrella creado exitosamente")
print(f"   - Fact Ventas: {fact_ventas.count()} registros")
print(f"   - Dim Tiempo: {dim_tiempo.count()} registros")
print(f"   - Dim Producto: {dim_producto.count()} registros")
print(f"   - Dim Cliente: {dim_cliente.count()} registros")
print(f"   - Dim Geografía: {dim_geografia.count()} registros")

# ===============================================
# ANÁLISIS OLAP 1: TENDENCIAS DE CONSUMO
# ===============================================

print("\n📈 ANÁLISIS OLAP 1: TENDENCIAS DE CONSUMO POR CATEGORÍA")
print("=" * 60)

# Cubo OLAP: Tendencias por Tiempo, Categoría y Zona
cubo_tendencias = spark.sql("""
    SELECT 
        dt.anio,
        dt.mes,
        dt.mes_nombre,
        dt.trimestre_nombre,
        dp.categoria_nombre,
        dc.cliente_zona,
        COUNT(DISTINCT fv.pedido_key) as num_pedidos,
        SUM(fv.cantidad) as cantidad_productos,
        SUM(fv.subtotal) as ingresos_totales,
        AVG(fv.subtotal) as ticket_promedio,
        COUNT(DISTINCT fv.cliente_key) as clientes_unicos,
        SUM(fv.subtotal) / SUM(fv.cantidad) as precio_promedio_unitario
    FROM fact_ventas fv
    JOIN dim_tiempo dt ON fv.fecha_key = dt.fecha_key
    JOIN dim_producto dp ON fv.producto_key = dp.producto_key
    JOIN dim_cliente dc ON fv.cliente_key = dc.cliente_key
    GROUP BY dt.anio, dt.mes, dt.mes_nombre, dt.trimestre_nombre, 
             dp.categoria_nombre, dc.cliente_zona
    ORDER BY dt.anio, dt.mes, ingresos_totales DESC
""")

print("📊 Cubo OLAP - Tendencias de Consumo:")
cubo_tendencias.show(50, truncate=False)

# Vista agregada por categoría y tiempo
tendencias_categoria_tiempo = spark.sql("""
    SELECT 
        dt.anio,
        dt.mes_nombre,
        dp.categoria_nombre,
        SUM(fv.subtotal) as ingresos_categoria,
        SUM(fv.cantidad) as productos_vendidos,
        COUNT(DISTINCT fv.pedido_key) as pedidos_categoria,
        ROUND(
            SUM(fv.subtotal) * 100.0 / SUM(SUM(fv.subtotal)) OVER (PARTITION BY dt.anio, dt.mes), 2
        ) as participacion_mensual_pct
    FROM fact_ventas fv
    JOIN dim_tiempo dt ON fv.fecha_key = dt.fecha_key
    JOIN dim_producto dp ON fv.producto_key = dp.producto_key
    GROUP BY dt.anio, dt.mes_nombre, dt.mes, dp.categoria_nombre
    ORDER BY dt.anio, dt.mes, ingresos_categoria DESC
""")

print("📊 Tendencias por Categoría y Tiempo:")
tendencias_categoria_tiempo.show(30, truncate=False)

# ===============================================
# ANÁLISIS OLAP 2: HORARIOS PICO
# ===============================================

print("\n⏰ ANÁLISIS OLAP 2: HORARIOS PICO Y PATRONES TEMPORALES")
print("=" * 60)

# Análisis de horarios pico con datos transformados
horarios_pico = df_pedidos \
    .filter(col("estado") == "completado") \
    .withColumn("hora", hour(col("fecha_pedido"))) \
    .withColumn("dia_semana", dayofweek(col("fecha_pedido"))) \
    .withColumn("periodo_dia", 
        when(col("hora").between(6, 11), "Desayuno")
        .when(col("hora").between(12, 16), "Almuerzo")
        .when(col("hora").between(17, 22), "Cena")
        .otherwise("Madrugada")
    ) \
    .withColumn("es_fin_semana", 
        when(col("dia_semana").isin([1, 7]), True).otherwise(False)
    )

# Registrar vista temporal
horarios_pico.createOrReplaceTempView("pedidos_horarios")

# Cubo OLAP: Horarios por período, día y zona
cubo_horarios = spark.sql("""
    SELECT 
        periodo_dia,
        es_fin_semana,
        zona_entrega,
        COUNT(*) as num_pedidos,
        AVG(total) as ticket_promedio,
        SUM(total) as ingresos_periodo,
        COUNT(DISTINCT cliente_id) as clientes_unicos,
        MIN(total) as ticket_minimo,
        MAX(total) as ticket_maximo
    FROM pedidos_horarios 
    GROUP BY periodo_dia, es_fin_semana, zona_entrega
    ORDER BY ingresos_periodo DESC
""")

print("📊 Cubo OLAP - Horarios Pico:")
cubo_horarios.show(50, truncate=False)

# Análisis detallado por hora
distribucion_horaria = spark.sql("""
    SELECT 
        hora,
        periodo_dia,
        COUNT(*) as pedidos_hora,
        AVG(total) as ticket_promedio_hora,
        SUM(total) as ingresos_hora,
        ROUND(
            COUNT(*) * 100.0 / (SELECT COUNT(*) FROM pedidos_horarios), 2
        ) as participacion_pct
    FROM pedidos_horarios 
    GROUP BY hora, periodo_dia
    ORDER BY hora
""")

print("📊 Distribución Horaria Detallada:")
distribucion_horaria.show(24, truncate=False)

# ===============================================
# ANÁLISIS OLAP 3: CRECIMIENTO MENSUAL
# ===============================================

print("\n📊 ANÁLISIS OLAP 3: CRECIMIENTO MENSUAL Y ESTACIONALIDAD")
print("=" * 60)

# Cubo OLAP: Crecimiento por tiempo, zona y categoría
cubo_crecimiento = spark.sql("""
    SELECT 
        dt.anio,
        dt.mes,
        dt.mes_nombre,
        dt.trimestre_nombre,
        dc.cliente_zona,
        dp.categoria_nombre,
        COUNT(DISTINCT fv.pedido_key) as pedidos_completados,
        SUM(fv.subtotal) as ingresos_totales,
        AVG(fv.subtotal) as ticket_promedio,
        COUNT(DISTINCT fv.cliente_key) as clientes_activos,
        SUM(fv.cantidad) as productos_vendidos
    FROM fact_ventas fv
    JOIN dim_tiempo dt ON fv.fecha_key = dt.fecha_key
    JOIN dim_cliente dc ON fv.cliente_key = dc.cliente_key
    JOIN dim_producto dp ON fv.producto_key = dp.producto_key
    GROUP BY dt.anio, dt.mes, dt.mes_nombre, dt.trimestre_nombre, 
             dc.cliente_zona, dp.categoria_nombre
    ORDER BY dt.anio, dt.mes, ingresos_totales DESC
""")

print("📊 Cubo OLAP - Crecimiento Mensual:")
cubo_crecimiento.show(50, truncate=False)

# Análisis de crecimiento mensual agregado
crecimiento_mensual = spark.sql("""
    SELECT 
        dt.anio,
        dt.mes,
        dt.mes_nombre,
        COUNT(DISTINCT fv.pedido_key) as total_pedidos,
        SUM(fv.subtotal) as ingresos_totales,
        AVG(fv.subtotal) as ticket_promedio,
        COUNT(DISTINCT fv.cliente_key) as clientes_unicos,
        SUM(fv.cantidad) as productos_vendidos
    FROM fact_ventas fv
    JOIN dim_tiempo dt ON fv.fecha_key = dt.fecha_key
    GROUP BY dt.anio, dt.mes, dt.mes_nombre
    ORDER BY dt.anio, dt.mes
""")

# Calcular crecimiento porcentual
window_spec = Window.orderBy("anio", "mes")
crecimiento_con_variacion = crecimiento_mensual \
    .withColumn("ingresos_mes_anterior", lag("ingresos_totales", 1).over(window_spec)) \
    .withColumn("crecimiento_pct",
        when(col("ingresos_mes_anterior").isNotNull() & (col("ingresos_mes_anterior") > 0),
             round(((col("ingresos_totales") - col("ingresos_mes_anterior")) / 
                   col("ingresos_mes_anterior") * 100), 2))
        .otherwise(None))

print("📈 Crecimiento Mensual con Variaciones:")
crecimiento_con_variacion.show(12, truncate=False)

# ===============================================
# CREAR VISTAS OLAP PARA METABASE
# ===============================================

print("\n🔄 CREANDO VISTAS OLAP PARA METABASE")
print("=" * 60)

try:
    # Guardar resultados en PostgreSQL para que Metabase los pueda leer
    
    # Vista 1: Ingresos por mes y categoría
    vista_ingresos_mes_categoria = spark.sql("""
        SELECT 
            dt.anio,
            dt.mes,
            dt.mes_nombre,
            dp.categoria_nombre,
            SUM(fv.subtotal) as ingresos_categoria,
            COUNT(DISTINCT fv.pedido_key) as pedidos_categoria,
            SUM(fv.cantidad) as productos_vendidos,
            COUNT(DISTINCT fv.cliente_key) as clientes_categoria
        FROM fact_ventas fv
        JOIN dim_tiempo dt ON fv.fecha_key = dt.fecha_key
        JOIN dim_producto dp ON fv.producto_key = dp.producto_key
        GROUP BY dt.anio, dt.mes, dt.mes_nombre, dp.categoria_nombre
        ORDER BY dt.anio, dt.mes, ingresos_categoria DESC
    """)
    
    # Vista 2: Actividad por zona geográfica
    vista_actividad_zona = spark.sql("""
        SELECT 
            dc.cliente_zona,
            COUNT(DISTINCT fv.pedido_key) as total_pedidos,
            SUM(fv.subtotal) as ingresos_zona,
            AVG(fv.subtotal) as ticket_promedio,
            COUNT(DISTINCT fv.cliente_key) as clientes_unicos,
            SUM(fv.cantidad) as productos_vendidos
        FROM fact_ventas fv
        JOIN dim_cliente dc ON fv.cliente_key = dc.cliente_key
        GROUP BY dc.cliente_zona
        ORDER BY ingresos_zona DESC
    """)
    
    # Vista 3: Estadísticas de pedidos por estado
    vista_estadisticas_pedidos = spark.sql("""
        SELECT 
            dt.anio,
            dt.mes,
            dt.mes_nombre,
            COUNT(DISTINCT fv.pedido_key) as pedidos_completados,
            SUM(fv.subtotal) as ingresos_completados,
            AVG(fv.subtotal) as ticket_promedio,
            COUNT(DISTINCT fv.cliente_key) as clientes_activos
        FROM fact_ventas fv
        JOIN dim_tiempo dt ON fv.fecha_key = dt.fecha_key
        GROUP BY dt.anio, dt.mes, dt.mes_nombre
        ORDER BY dt.anio, dt.mes
    """)
    
    # Escribir vistas de vuelta a PostgreSQL
    vista_ingresos_mes_categoria.write \
        .jdbc(url=jdbc_url, table="vista_olap_ingresos_categoria", 
              mode="overwrite", properties=properties)
    
    vista_actividad_zona.write \
        .jdbc(url=jdbc_url, table="vista_olap_actividad_zona", 
              mode="overwrite", properties=properties)
    
    vista_estadisticas_pedidos.write \
        .jdbc(url=jdbc_url, table="vista_olap_estadisticas_pedidos", 
              mode="overwrite", properties=properties)
    
    print("✅ Vistas OLAP creadas en PostgreSQL para Metabase:")
    print("   - vista_olap_ingresos_categoria")
    print("   - vista_olap_actividad_zona") 
    print("   - vista_olap_estadisticas_pedidos")
    
except Exception as e:
    print(f"⚠️  Error al crear vistas en PostgreSQL: {e}")

# ===============================================
# RESUMEN FINAL
# ===============================================

print("\n🎯 RESUMEN DEL ANÁLISIS OLAP")
print("=" * 60)

# Métricas clave del negocio
metricas_generales = spark.sql("""
    SELECT 
        COUNT(DISTINCT pedido_key) as total_pedidos_completados,
        SUM(subtotal) as ingresos_totales,
        AVG(subtotal) as ticket_promedio_global,
        COUNT(DISTINCT cliente_key) as clientes_activos,
        COUNT(DISTINCT producto_key) as productos_vendidos,
        SUM(cantidad) as items_vendidos
    FROM fact_ventas
""")

print("📊 Métricas Generales del Negocio:")
metricas_generales.show(truncate=False)

# Top categorías por ingresos
top_categorias = spark.sql("""
    SELECT 
        dp.categoria_nombre,
        SUM(fv.subtotal) as ingresos_categoria,
        COUNT(DISTINCT fv.pedido_key) as pedidos_categoria,
        ROUND(
            SUM(fv.subtotal) * 100.0 / (SELECT SUM(subtotal) FROM fact_ventas), 2
        ) as participacion_pct
    FROM fact_ventas fv
    JOIN dim_producto dp ON fv.producto_key = dp.producto_key
    GROUP BY dp.categoria_nombre
    ORDER BY ingresos_categoria DESC
""")

print("🏆 Top Categorías por Ingresos:")
top_categorias.show(truncate=False)

# Mejor mes del año
mejor_mes = spark.sql("""
    SELECT 
        dt.mes_nombre,
        SUM(fv.subtotal) as ingresos_mes,
        COUNT(DISTINCT fv.pedido_key) as pedidos_mes
    FROM fact_ventas fv
    JOIN dim_tiempo dt ON fv.fecha_key = dt.fecha_key
    GROUP BY dt.mes, dt.mes_nombre
    ORDER BY ingresos_mes DESC
    LIMIT 1
""")

print("🎉 Mejor Mes del Año:")
mejor_mes.show(truncate=False)

print("\n🎉 ANÁLISIS OLAP COMPLETADO EXITOSAMENTE!")
print("📊 Datos procesados y vistas creadas para Metabase")
print("🔗 Conéctate a Metabase en http://localhost:3000")
print("💾 Usa las vistas OLAP creadas para tus dashboards")

# Limpiar recursos
spark.stop()