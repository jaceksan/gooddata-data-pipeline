with order_lines as (
  select
    order_line_id,
    order_id,
    order_status,
    date,
    -- Loaded by Meltano as VARCHAR, NULL values are loaded as empty strings. This would prevent creation of FK.
    (case campaign_id when '' then null else campaign_id end) as campaign_id,
    customer_id,
    product_id,
    cast(price as decimal(15, 2)) as price,
    cast(quantity as decimal(15, 2)) as quantity
  from {{ var("input_schema_demo") }}.order_lines
)

select * from order_lines
