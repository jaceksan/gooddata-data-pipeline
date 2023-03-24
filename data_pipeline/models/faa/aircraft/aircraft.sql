with aircraft as (
  select
    tail_num,
    aircraft_model_code
  from {{ var("input_schema_faa") }}.aircraft
)

select * from aircraft
