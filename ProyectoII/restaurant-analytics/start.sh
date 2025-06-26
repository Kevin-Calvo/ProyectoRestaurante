#!/bin/bash

echo "🚀 INICIANDO PROYECTO DE ANÁLISIS OLAP PARA RESTAURANTE"
echo "=" * 60

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi

echo "✅ Docker está corriendo"

# Limpiar contenedores anteriores si existen
echo "🧹 Limpiando contenedores anteriores..."
docker-compose down -v

# Construir e iniciar servicios
echo "🏗️  Construyendo e iniciando servicios..."
docker-compose up --build -d

echo "⏳ Esperando a que los servicios se inicialicen..."
echo "   PostgreSQL tardará unos 30 segundos en inicializar los datos..."
echo "   Metabase tardará unos 2-3 minutos en estar listo..."

# Esperar a que PostgreSQL esté listo
echo "📊 Verificando PostgreSQL..."
timeout=60
counter=0
until docker exec restaurant_postgres pg_isready -U restaurant_user -d restaurant_db > /dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        echo "❌ PostgreSQL no se pudo inicializar en $timeout segundos"
        exit 1
    fi
    echo "⏳ Esperando PostgreSQL... ($counter/$timeout)"
    sleep 5
    counter=$((counter + 5))
done

echo "✅ PostgreSQL está listo"

# Ejecutar análisis con Spark
echo "⚡ Ejecutando análisis OLAP con Spark..."
docker-compose logs -f spark

echo ""
echo "🎉 ¡PROYECTO INICIADO EXITOSAMENTE!"
echo "=" * 60
echo "📊 Servicios disponibles:"
echo "   - PostgreSQL: localhost:5432"
echo "     - Usuario: restaurant_user"
echo "     - Contraseña: restaurant_pass"
echo "     - Base de datos: restaurant_db"
echo ""
echo "   - Metabase: http://localhost:3000"
echo "     - Usuario inicial: admin@admin.com"
echo "     - Contraseña inicial: admin123"
echo ""
echo "📈 Para conectar Metabase a PostgreSQL:"
echo "   - Host: postgres"
echo "   - Puerto: 5432"
echo "   - Database: restaurant_db"
echo "   - Username: restaurant_user"
echo "   - Password: restaurant_pass"
echo ""
echo "🔍 Vistas OLAP disponibles para dashboards:"
echo "   - vista_olap_ingresos_categoria"
echo "   - vista_olap_actividad_zona"
echo "   - vista_olap_estadisticas_pedidos"
echo "   - vista_ingresos_mes_categoria (vista nativa)"
echo "   - vista_actividad_clientes_zona (vista nativa)"
echo ""
echo "⚙️  Para ver logs de un servicio específico:"
echo "   docker-compose logs -f [servicio]"
echo ""
echo "🛑 Para detener todo:"
echo "   docker-compose down"