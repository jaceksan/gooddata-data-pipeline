with final as (
  select
    timestamp,
    continent,
    CAST(population AS DECIMAL(15, 2)) as population
  from {{ var("input_schema_data_science") }}.census
)

select * from final
