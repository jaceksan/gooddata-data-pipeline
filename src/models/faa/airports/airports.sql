with airports as (
  select
    code,
    faa_region,
    fac_type,
    state,
    cast(elevation as int) as elevation,
    code || '-' || full_name as name
  from {{ var("input_schema") }}.airports
)

select * from airports
