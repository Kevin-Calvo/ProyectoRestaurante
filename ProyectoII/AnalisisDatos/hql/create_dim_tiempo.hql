CREATE EXTERNAL TABLE IF NOT EXISTS dim_tiempo (
  fecha STRING,
  dia INT,
  mes STRING,
  trimestre INT,
  year INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/AnalisisDatos/csv/dim_tiempo';



