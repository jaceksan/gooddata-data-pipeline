with commits as (
    select to_json("item") as item_json from cicd_input_stage.commits
),

users as (
    select * from {{ ref('users') }}
),

extract_from_commits as (
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
),

final as (
    select
      extract_from_commits.commit_id,
      extract_from_commits.commit_url,
      extract_from_commits.commit_title,
      extract_from_commits.user_id,
      extract_from_commits.created_at
    from extract_from_commits
    -- Filter out commits without responsible user (data cleansing)
    join users on extract_from_commits.user_id = users.user_id
    where extract_from_commits.user_id is not null and users.login is not null
)

select * from final