{{ config(
  schema=var('input_schema'),
  indexes=[
    {'columns': ['commit_id'], 'unique': true},
    {'columns': ['user_id'], 'unique': false}
  ]
) }}

-- Helper step, materialize extracted JSON fields first and then JOIN it with other tables

with commits as (
    select to_json("item") as item_json from {{ var("input_schema") }}.commits
),

final as (
    select
      CAST(json_extract_path_text(item_json, 'sha') as TEXT) as commit_id,
      CAST(json_extract_path_text(item_json, 'html_url') as TEXT) as commit_url,
      CAST(json_extract_path_text(item_json, 'title') as TEXT) as commit_title,
      CAST(json_extract_path_text(item_json, 'author', 'id') as INT) as user_id,
      to_timestamp(
        CAST(json_extract_path_text(item_json, 'commit', 'committer', 'date') as TEXT),
        '{{ var("github_date_format") }}'
      ) at time zone '{{ var("timezone") }}' as created_at
    from commits
)

select * from final