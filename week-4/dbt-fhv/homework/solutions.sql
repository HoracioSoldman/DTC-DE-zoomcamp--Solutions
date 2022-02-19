-- What is the count of records in the model fact_trips after running all models with the test run variable disabled 
-- and filtering for 2019 and 2020 data only (pickup datetime).

SELECT count(*) FROM `dtc-de-340319.dbt_hrc.fact_trips` where pickup_datetime between '2019-01-01' and '2021-12-31';
--> 61635083  / 61634866

-- The distribution between service_types:
-- 10.1% for green_taxi and 89.9% for the yellow_taxi

SELECT count(*) FROM `dtc-de-340319.dbt_fhv.stg_fhv_data` where DATE(pickup_datetime) between '2019-01-01' and '2019-12-31';
--> 42084899

SELECT count(*) FROM `dtc-de-340319.dbt_fhv.fact_trips` where date(pickup_datetime) between '2019-01-01' and '2019-12-31'; 
--> 22676253

--> January 2019