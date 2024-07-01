{{ config(
  materialized='incremental',
  unique_key='SalesID'
) }}
--   indexes=[
--     {'columns': ['SalesID'], 'unique': true},
--   ],

with using_clause as (
  select *
  from {{ var("input_schema") }}.fact_sales
  {% if is_incremental() %}
    where TransactionDate > ( select max(TransactionDate) from {{ this }} )
  {% endif %}
),

updates as (
  select *
  from using_clause
  {% if is_incremental() %}
    where SalesID in ( select SalesID from {{ this }} )
  {% else %}
    -- No updates when doing full load
    where 1 = 0
  {% endif %}
),

inserts as (
  select *
  from using_clause
  {% if is_incremental() %}
    where SalesID not in ( select SalesID from {{ this }} )
  {% endif %}
),

fact_sales as (
    select
      iu.*
    from (
      select * from inserts
      union all select * from updates
    ) iu
    -- JOIN dims to filter out bad data
    join {{ ref('dim_product') }} on iu.ProductID = dim_product.ProductID
    join {{ ref('dim_customer') }} on iu.CustomerID = dim_customer.CustomerID
)

select * from fact_sales
