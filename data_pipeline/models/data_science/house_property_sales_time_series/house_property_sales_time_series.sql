with final as (
  select
    saledate,
    type,
    bedrooms,
    CAST("MA" AS DECIMAL(15, 2)) as ma
  from {{ var("input_schema_data_science") }}.house_property_sales_time_series
)

select * from final
