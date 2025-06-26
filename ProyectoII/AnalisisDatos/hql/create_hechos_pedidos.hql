CREATE EXTERNAL TABLE IF NOT EXISTS hechos_pedidos (
  id STRING,
  id_usuario STRING,
  id_restaurante STRING,
  fecha STRING,
  estado STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/AnalisisDatos/csv/hechos_pedidos';
