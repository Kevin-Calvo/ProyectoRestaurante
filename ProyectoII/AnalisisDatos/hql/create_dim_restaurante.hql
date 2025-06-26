CREATE EXTERNAL TABLE IF NOT EXISTS dim_restaurante (
  id STRING,
  nombre STRING,
  direccion STRING,
  owner_id STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/AnalisisDatos/csv/dim_restaurante';

