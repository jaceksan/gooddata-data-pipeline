{{ config(
  indexes=[
    {'columns': ['user_id'], 'unique': true}
  ]
) }}

with collaborators as (
  select * from {{ var("input_schema") }}.collaborators
),

final as (
  -- We do not want to store users multiple times per repo where they collaborate (no analytics UC yet)
  select distinct
      collaborators.id as user_id,
      collaborators.html_url as user_html_url,
      collaborators.url as user_url,
      collaborators.login
  from collaborators
)

select * from final
