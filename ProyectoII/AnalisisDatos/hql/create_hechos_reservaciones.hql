CREATE EXTERNAL TABLE IF NOT EXISTS hechos_reservaciones (
  id STRING,
  id_usuario STRING,
  id_restaurante STRING,
  fecha STRING,
  invitados INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/AnalisisDatos/csv/hechos_reservaciones';
