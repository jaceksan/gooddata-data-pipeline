with aircraft_models as (
  select
    aircraft_model_code,
    manufacturer,
    cast(seats as int) as seats
  from {{ var("input_schema") }}.aircraft_models
)

select * from aircraft_models
