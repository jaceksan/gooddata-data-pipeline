with flights as (
  select
    cancelled,
    diverted,
    flight_num,
    id2,
    cast(arr_delay as int) as arr_delay,
    cast(dep_delay as int) as dep_delay,
    cast(distance as int) as distance,
    cast(flight_time as int) as flight_time,
    cast(taxi_in as int) as taxi_in,
    cast(taxi_out as int) as taxi_out,
    carrier,
    destination,
    origin,
    dep_time,
    tail_num
  from {{ var("input_schema_faa") }}.flights
)

select * from flights
