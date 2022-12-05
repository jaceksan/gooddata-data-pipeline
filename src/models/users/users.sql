{{ config(
  indexes=[
    {'columns': ['user_id'], 'unique': true}
  ]
) }}

with users as (
  select to_json("item") as item_json from {{ var("input_schema") }}.users
),

final as (
  select
    CAST(json_extract_path_text(item_json, 'id') as INT) as user_id,
    CAST(json_extract_path_text(item_json, 'html_url') as TEXT) as user_url,
    CAST(json_extract_path_text(item_json, 'login') as TEXT) as login
  from users
)

select * from final
