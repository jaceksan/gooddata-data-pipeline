with final as (
  select
    timestamp,
    CAST(temperature AS DECIMAL(15, 2)) as temperature
  from {{ var("input_schema_data_science") }}.ambient_temperature
)

select * from final
