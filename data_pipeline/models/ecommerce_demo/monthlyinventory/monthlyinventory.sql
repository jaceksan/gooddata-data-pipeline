with monthlyinventory as (
  select
    monthly_inventory_id,
    (case product__product_id when '' then null else product__product_id end) as product__product_id,
    CAST(monthly_quantity_eom AS DECIMAL(15, 2)) as monthly_quantity_eom,
    CAST(monthly_quantity_bom AS DECIMAL(15, 2)) as monthly_quantity_bom,
    inventory_month,
    date,
    wdf__client_id
  from {{ var("input_schema_ecommerce_demo") }}.monthlyinventory
)

select * from monthlyinventory
