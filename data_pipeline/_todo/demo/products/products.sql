with products as (
  select
    product_id,
    product_name,
    category
  from {{ var("input_schema_demo") }}.products
)

select * from products
