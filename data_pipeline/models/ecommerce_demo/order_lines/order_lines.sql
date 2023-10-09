with order_lines as (
  select
    order_line_id,
    (case order__order_id when '' then null else order__order_id end) as order__order_id,
    (case product__product_id when '' then null else product__product_id end) as product__product_id,
    (case customer__customer_id when '' then null else customer__customer_id end) as customer__customer_id,
    CAST(order_unit_price AS DECIMAL(15, 2)) as order_unit_price,
    CAST(order_unit_quantity AS DECIMAL(15, 2)) as order_unit_quantity,
    CAST(order_unit_discount AS DECIMAL(15, 2)) as order_unit_discount,
    CAST(order_unit_cost AS DECIMAL(15, 2)) as order_unit_cost,
    date,
    order_date,
    customer_age,
    wdf__client_id
  from {{ var("input_schema_ecommerce_demo") }}.order_lines
)

select * from order_lines
