{{ config(
  indexes=[
    {'columns': ['user_id'], 'unique': true}
  ]
) }}

with contributors as (
  select * from {{ var("input_schema") }}.contributors
),

final as (
  -- We do not want to store users multiple times per repo where they contribute (no analytics UC yet)
  select distinct
    contributors.id as user_id,
    contributors.html_url as user_html_url,
    contributors.url as user_url,
    contributors.login
  from contributors
)

select * from final
