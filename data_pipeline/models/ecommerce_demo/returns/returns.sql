with returns as (
  select
    return_id,
    (case order__order_id when '' then null else order__order_id end) as order__order_id,
    (case product__product_id when '' then null else product__product_id end) as product__product_id,
    (case customer__customer_id when '' then null else customer__customer_id end) as customer__customer_id,
    CAST(return_unit_cost AS DECIMAL(15, 2)) as return_unit_cost,
    CAST(return_unit_quantity AS DECIMAL(15, 2)) as return_unit_quantity,
    CAST(return_unit_paid_amount AS DECIMAL(15, 2)) as return_unit_paid_amount,
    date,
    return_date,
    wdf__client_id
  from {{ var("input_schema_ecommerce_demo") }}.returns
)

select * from returns
