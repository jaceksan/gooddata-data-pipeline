with final as (
  select
    timestamp,
    country,
    CAST((CASE population WHEN '' THEN NULL ELSE population END) AS DECIMAL(15, 2)) as population
  from {{ var("input_schema_data_science") }}.census_by_country
)

select * from final
