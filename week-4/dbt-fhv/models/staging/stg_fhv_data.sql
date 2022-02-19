{{ config(materialized='view') }}


with tripdata as 
(
  select *
  from {{ source('staging','fhv2019_external_table_partitoned_clustered') }}
  where dispatching_base_num is not null 
)

select
    -- identifiers
    
    dispatching_base_num,
    cast(PULocationid as integer) as  PULocationid,
    cast(DOLocationid as integer) as DOLocationid,
    
    -- timestamps
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropoff_datetime as timestamp) as dropoff_datetime,
    
    -- trip info
    cast(SR_Flag as integer) as SR_Flag

from tripdata

--dbt build --if <model.sql> --var 'is_test_run: false'
{% if var('is_test_run', default=false) %}
    limit 100
{% endif %}