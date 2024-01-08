with final as (
  select
    id,
    username,
    first_name,
    last_name,
    email,
    gender,
    country,
    CAST((CASE visits WHEN '' THEN NULL ELSE visits END) AS DECIMAL(15, 2)) as visits,
    CAST((CASE nps WHEN '' THEN NULL ELSE nps END) AS DECIMAL(15, 2)) as nps,
    CAST((CASE clv WHEN '' THEN NULL ELSE clv END) AS DECIMAL(15, 2)) as clv
  from {{ var("input_schema_data_science") }}.eshop_customers
)

select * from final
