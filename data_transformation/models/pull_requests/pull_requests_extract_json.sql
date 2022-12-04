{{ config(
  schema=var('input_schema'),
  indexes=[
    {'columns': ['pull_request_id'], 'unique': true},
    {'columns': ['user_id'], 'unique': false}
  ]
) }}

with pull_requests as (
    select to_json("item") as item_json from {{ var("input_schema") }}.pulls
),

final as (
    select
      CAST(json_extract_path_text(item_json, 'id') as INT) as pull_request_id,
      CAST(json_extract_path_text(item_json, 'html_url') as TEXT) as pull_request_url,
      CAST(json_extract_path_text(item_json, 'title') as TEXT) as pull_request_title,
      CAST(json_extract_path_text(item_json, 'draft') as BOOLEAN) as pull_request_draft,
      CAST(json_extract_path_text(item_json, 'user', 'id') as INT) as user_id,
      to_timestamp(
        CAST(json_extract_path_text(item_json, 'created_at') as TEXT),
        '{{ var("github_date_format") }}'
      ) at time zone '{{ var("timezone") }}' as created_at,
      to_timestamp(
        CAST(json_extract_path_text(item_json, 'merged_at') as TEXT),
        '{{ var("github_date_format") }}'
      ) at time zone '{{ var("timezone") }}' as merged_at,
      to_timestamp(
        CAST(json_extract_path_text(item_json, 'closed_at') as TEXT),
        '{{ var("github_date_format") }}'
      ) at time zone '{{ var("timezone") }}' as closed_at
    from pull_requests
)

select * from final
