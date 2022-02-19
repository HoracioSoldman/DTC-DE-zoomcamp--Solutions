{{ config(materialized='table') }}

with trips_data as (
    select *
    from {{ ref('stg_fhv_data') }}
), 

dim_zones as (
    select * from {{ ref('dim_zones') }}
    where borough != 'Unknown'
)
select 
    trips_data.dispatching_base_num, 
    trips_data.PULocationid,
    pickup_zone.zone as pickup_zone, 
    trips_data.DOLocationid,
    dropoff_zone.zone as dropoff_zone,
    trips_data.pickup_datetime, 
    trips_data.dropoff_datetime, 
    trips_data.SR_Flag
from trips_data
inner join dim_zones as pickup_zone
on trips_data.PULocationid = pickup_zone.locationid
inner join dim_zones as dropoff_zone
on trips_data.DOLocationid = dropoff_zone.locationid
where pickup_zone is not null and dropoff_zone is not null