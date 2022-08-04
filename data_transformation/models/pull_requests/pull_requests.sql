with pull_requests as (
    select to_json("item") as item_json from cicd_input_stage.pulls
),

users as (
    select * from {{ ref('users') }}
),

extract_pulls as (
    select
      CAST(json_extract_path_text(item_json, 'id') as INT) as pull_request_id,
      CAST(json_extract_path_text(item_json, 'html_url') as TEXT) as pull_request_url,
      CAST(json_extract_path_text(item_json, 'user', 'id') as INT) as user_id,
      to_timestamp(
        CAST(json_extract_path_text(item_json, 'created_at') as TEXT),
        '{{ var("github_date_format") }}'
      ) at time zone '{{ var("timezone") }}' as created_at,
      to_timestamp(
        CAST(json_extract_path_text(item_json, 'merged_at') as TEXT),
        '{{ var("github_date_format") }}'
      ) at time zone '{{ var("timezone") }}' as merged_at
    from pull_requests
),

final as (
    select
      extract_pulls.pull_request_id,
      extract_pulls.pull_request_url,
      extract_pulls.user_id,
      extract_pulls.created_at,
      extract_pulls.merged_at,
      (extract(epoch from extract_pulls.merged_at) - extract(epoch from extract_pulls.created_at)) / 3600 as hours_to_solve
    from extract_pulls
    -- Filter out commits without responsible user (data cleansing)
    join users on extract_pulls.user_id = users.user_id
    where extract_pulls.user_id is not null and users.login is not null and extract_pulls.merged_at is not null
)

select * from final
