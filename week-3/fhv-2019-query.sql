-- Creating external table for the FHV dataset referring to gcs path
CREATE OR REPLACE EXTERNAL TABLE `dtc-de-340319.fhv2019.fhv2019_external_table`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://dtc_data_lake_dtc-de-340319/raw/fhv/*.parquet']
);

--1. What is count for fhv vehicles data for year 2019
SELECT count(*) FROM `dtc-de-340319.fhv2019.fhv2019_external_table`;

--2. How many distinct dispatching_base_num we have in fhv for 2019
SELECT count(distinct(dispatching_base_num)) FROM `dtc-de-340319.fhv2019.fhv2019_external_table`;

--4. What is the count, estimated and actual data processed for query which counts trip 
--   between 2019/01/01 and 2019/03/31 for dispatching_base_num B00987, B02060, B02279


CREATE OR REPLACE TABLE `dtc-de-340319.fhv2019.fhv2019_external_table_partitoned_clustered`
PARTITION BY DATE(pickup_datetime)
CLUSTER BY dispatching_base_num AS
SELECT * FROM `dtc-de-340319.fhv2019.fhv2019_external_table`;


select count(*) from `dtc-de-340319.fhv2019.fhv2019_external_table_partitoned_clustered`
where date(pickup_datetime) between date('2019-01-01') and date('2019-03-31')
and dispatching_base_num in ('B00987', 'B02060', 'B02279');




