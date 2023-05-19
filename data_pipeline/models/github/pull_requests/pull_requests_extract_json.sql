{{ config(
  schema=var('input_schema_github'),
  indexes=[
    {'columns': ['pull_request_number', 'repo_id'], 'unique': true},
    {'columns': ['user_id'], 'unique': false},
    {'columns': ['created_at'], 'unique': false}
  ],
  materialized='incremental',
  unique_key=['pull_request_number', 'repo_id']
) }}

-- Helper step, materialize extracted JSON fields first and then JOIN it with other tables
-- Incremental mode

with using_clause as (
  select
    number as pull_request_number,
    html_url as pull_request_url,
    title as pull_request_title,
    draft as pull_request_draft,
    state,
    CAST(repo_id as INT) as repo_id,
    created_at,
    merged_at,
    closed_at,
    {{ extract_json_value('user', 'id', 'user_id', 'INT') }}
    --CAST(json_extract_path_text(to_json("{{ get_db_entity_name('user') }}"), 'id') as INT) as user_id
  from {{ var("input_schema_github") }}.pull_requests
  {% if is_incremental() %}
    where created_at > ( select max(created_at) from {{ this }} )
  {% endif %}
),

updates as (
  select *
  from using_clause
  {% if is_incremental() %}
    where (pull_request_number, repo_id) in ( select pull_request_number, repo_id from {{ this }} )
  {% else %}
    -- No updates when doing full load
    where 1 = 0
  {% endif %}
),

inserts as (
  select *
  from using_clause
  {% if is_incremental() %}
    where (pull_request_number, repo_id) not in ( select pull_request_number, repo_id from {{ this }} )
  {% endif %}
),

final as (
    select *
    from inserts
    union all select * from updates
)

select * from final
