{{ config(
  schema=var('input_schema_github'),
  indexes=[
    {'columns': ['commit_id'], 'unique': true},
    {'columns': ['user_id'], 'unique': false},
    {'columns': ['repo_id'], 'unique': false}
  ],
  materialized='incremental',
  unique_key='commit_id'
) }}

-- Helper step, materialize extracted JSON fields first and then JOIN it with other tables
-- Incremental mode

with using_clause as (
  select
    sha as commit_id,
    html_url as commit_url,
    {{ extract_json_value('commit', 'comment_count', 'comment_count', 'INT') }},
    commit_timestamp as created_at,
    {{ extract_json_value('author', 'id', 'user_id', 'INT') }},
    CAST(repo_id as INT) as repo_id
  from {{ var("input_schema_github") }}.commits
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