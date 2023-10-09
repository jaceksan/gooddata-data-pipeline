with customer as (
  select
    customer_id,
    ls__customer_id__customer_name,
    customer_city,
    geo__customer_city__city_pushpin_longitude,
    geo__customer_city__city_pushpin_latitude,
    customer_country,
    customer_email,
    customer_state,
    customer_created_date,
    wdf__client_id
  from {{ var("input_schema_ecommerce_demo") }}.customer c
)

select * from customer
