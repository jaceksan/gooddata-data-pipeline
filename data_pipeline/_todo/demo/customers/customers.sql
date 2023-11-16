with customers as (
  select
    customer_id,
    customer_name,
    g.usa_state as state,
    g.usa_state_latitude as state_latitude,
    g.usa_state_longitude as state_longitude,
    region
  from {{ var("input_schema_demo") }}.customers c
  left join {{ var("input_schema_demo") }}.countries_geo_coordinates g
    on lower(c.state) = lower(g.usa_state_code)
)

select * from customers
