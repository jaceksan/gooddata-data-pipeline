with orders as (
  select
    order_id,
    order_status,
    wdf__client_id
  from {{ var("input_schema_ecommerce_demo") }}.orders c
)

select * from orders
