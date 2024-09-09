{{ config(
  materialized='incremental',
  unique_key='InventoryID'
) }}
--   indexes=[
--     {'columns': ['InventoryID'], 'unique': true},
--   ],

with using_clause as (
  select *
  from {{ var("input_schema") }}.fact_inventory
  {% if is_incremental() %}
    where TransactionDate > ( select max(TransactionDate) from {{ this }} )
  {% endif %}
),

updates as (
  select *
  from using_clause
  {% if is_incremental() %}
    where InventoryID in ( select InventoryID from {{ this }} )
  {% else %}
    -- No updates when doing full load
    where 1 = 0
  {% endif %}
),

inserts as (
  select *
  from using_clause
  {% if is_incremental() %}
    where InventoryID not in ( select InventoryID from {{ this }} )
  {% endif %}
),

fact_inventory as (
    select
      iu.*
    from (
      select * from inserts
      union all select * from updates
    ) iu
    -- JOIN dims to filter out bad data
    join {{ ref('dim_product') }} on iu.ProductID = dim_product.ProductID
)

select * from fact_inventory
