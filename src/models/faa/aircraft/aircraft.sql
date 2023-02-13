with aircraft as (
  select
    tail_num,
    aircraft_model_code
  from {{ var("input_schema") }}.aircraft
)

select * from aircraft
