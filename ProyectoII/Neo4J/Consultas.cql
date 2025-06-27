// Pedidos por recomendacion

MATCH 
  (recomendador:Usuario)-[:Recomienda]->(restaurante:Restaurante),
  (seguidor:Usuario)-[:Siguiendo_A]->(recomendador),
  (seguidor)-[:Realiza]->(pedido:Pedido)-[:Pertenece_A]->(restaurante)
  
RETURN 
  recomendador.nombre AS Usuario_Que_Recomienda,
  seguidor.nombre AS Usuario_Que_Siguio,
  restaurante.nombre AS Restaurante_Recomendado,
  COUNT(pedido) AS Veces_Que_Siguio_La_Recomendacion
ORDER BY Usuario_Que_Recomienda ASC, Veces_Que_Siguio_La_Recomendacion DESC;

// Recomendaciones seguidas

MATCH 
  (recomendador:Usuario)-[:Recomienda]->(restaurante:Restaurante),
  (seguidor:Usuario)-[:Siguiendo_A]->(recomendador),
  (seguidor)-[:Realiza]->(:Pedido)-[:Pertenece_A]->(restaurante)
  
WITH recomendador, collect(DISTINCT seguidor) AS seguidores_que_siguieron

RETURN 
  recomendador.nombre AS Usuario_Que_Recomienda,
  size(seguidores_que_siguieron) AS Cantidad_De_Seguidores_Que_Siguieron_Recomendaciones
ORDER BY Cantidad_De_Seguidores_Que_Siguieron_Recomendaciones DESC;

// Ruta optima

// 🔁 Cambiá aquí el ID del repartidor
WITH 46 AS repartidorId

// Obtener ubicaciones de entrega y de origen desde restaurante
MATCH (r:Repartidor {id: repartidorId})-[:Reparte]->(p:Pedido)
MATCH (p)-[:Entregado_En]->(destino:Ubicacion)
MATCH (p)-[:Pertenece_A]->(:Restaurante)-[:Ubicado]->(origen:Ubicacion)
WITH DISTINCT origen, collect(DISTINCT destino) AS destinos

// Ejecutar Dijkstra desde ubicación del restaurante hacia cada destino
UNWIND destinos AS destino
CALL gds.shortestPath.dijkstra.stream('mapa_tiempo', {
  sourceNode: id(origen),
  targetNode: id(destino),
  relationshipWeightProperty: 'tiempo_min'
})
YIELD totalCost, nodeIds

RETURN 
  [nodeId IN nodeIds | gds.util.asNode(nodeId).nombre] AS Ruta,
  totalCost AS TiempoTotal
ORDER BY TiempoTotal ASC

// Productos mas comprados juntos

MATCH (p1:Producto)<-[:Contiene]-(pedido:Pedido)-[:Contiene]->(p2:Producto)
WHERE p1.id < p2.id
RETURN 
  p1.nombre AS Producto1, 
  p2.nombre AS Producto2, 
  COUNT(*) AS VecesCompradosJuntos
ORDER BY VecesCompradosJuntos DESC
LIMIT 5
Untitled Cypher

