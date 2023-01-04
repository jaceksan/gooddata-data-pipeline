{{ config(
  schema=var('input_schema'),
  indexes=[
    {'columns': ['commit_id'], 'unique': true},
    {'columns': ['user_url'], 'unique': false}
  ]
) }}

-- Helper step, materialize extracted JSON fields first and then JOIN it with other tables

with commits_extracted as (
    select
      commit_timestamp,
      sha,
      html_url,
      repo_id,
      to_json("author") as author_json,
      to_json("commit") as commit_json
    from {{ var("input_schema") }}.commits
),

final as (
    select
      sha as commit_id,
      html_url as commit_url,
      CAST(json_extract_path_text(commit_json, 'comment_count') as INT) as comment_count,
      commit_timestamp at time zone '{{ var("timezone") }}' as created_at,
      CAST(json_extract_path_text(author_json, 'url') as TEXT) as user_url,
      repo_id
    from commits_extracted
)

select * from final