{{ config(
  schema=var('input_schema'),
  indexes=[
    {'columns': ['repo_id'], 'unique': true}
  ]
) }}

with repos as (
  select to_json("item") as item_json from {{ var("input_schema") }}.repos
),

final as (
    select
      CAST(json_extract_path_text(item_json, 'id') as INT) as repo_id,
      CAST(json_extract_path_text(item_json, 'html_url') as TEXT) as repo_url,
      CAST(json_extract_path_text(item_json, 'name') as TEXT) as repo_name
    from repos
)

select * from final
