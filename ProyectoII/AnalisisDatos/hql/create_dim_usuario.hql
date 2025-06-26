CREATE EXTERNAL TABLE IF NOT EXISTS dim_usuario (
  id STRING,
  nombre STRING,
  email STRING,
  rol STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/AnalisisDatos/csv/dim_usuario';