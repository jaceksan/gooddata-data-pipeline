{{ config(
  schema=var('input_schema'),
  indexes=[
    {'columns': ['commit_id'], 'unique': true},
    {'columns': ['user_url'], 'unique': false}
  ],
  materialized='incremental',
  unique_key='commit_id',
  incremental_strategy='delete+insert'
) }}

-- Helper step, materialize extracted JSON fields first and then JOIN it with other tables
-- Incremental mode

with using_clause as (
  select
    sha as commit_id,
    html_url as commit_url,
    CAST(json_extract_path_text(to_json(commit), 'comment_count') as INT) as comment_count,
    commit_timestamp as created_at,
    CAST(json_extract_path_text(to_json(author), 'url') as TEXT) as user_url,
    repo_id
  from {{ var("input_schema") }}.commits
  {% if is_incremental() %}
    where commit_timestamp > ( select max(created_at) from {{ this }} )
  {% endif %}
),

updates as (
  select *
  from using_clause
  {% if is_incremental() %}
    where commit_id in ( select commit_id from {{ this }} )
  {% else %}
    -- No updates when doing full load
    where 1 = 0
  {% endif %}
),

inserts as (
  select *
  from using_clause
  {% if is_incremental() %}
    where commit_id not in ( select commit_id from {{ this }} )
  {% endif %}
),

final as (
  select * from inserts
  union all select * from updates
)

select * from final