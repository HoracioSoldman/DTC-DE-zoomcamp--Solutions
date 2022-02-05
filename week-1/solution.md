## My Solution

1- select count(*) from yellow_taxi_data where date(tpep_pickup_datetime) = '2021-01-15'  


2- select date(tpep_pickup_datetime) as pickup_date,  max(tip_amount) as max_tip from yellow_taxi_data group by date(tpep_pickup_datetime) order by max_tip 
 desc limit 1;


3- select "DOLocationID", zones."Zone", count(*) as rides  
  from yellow_taxi_data  
  left outer join zones on yellow_taxi_data."DOLocationID" = zones."LocationID" 
  where tpep_dropoff_datetime::date = '2021-01-14' and "PULocationID" in (select "LocationID" from zones where "Zone" = 'Central Park')  
  group by "DOLocationID", zones."Zone"  
  order by rides desc  
  limit 1;


4- select concat("PULocationID" , ' / ' , "DOLocationID") as journey, avg(total_amount) as average_fare 
 from yellow_taxi_data  
 group by journey 
 order by average_fare desc 
 limit 1;
 --couldn't display the pickup and dropoff zones with the single query