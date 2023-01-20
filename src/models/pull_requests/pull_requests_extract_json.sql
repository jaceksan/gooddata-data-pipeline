{{ config(
  schema=var('input_schema'),
  indexes=[
    {'columns': ['pull_request_number', 'repo_id'], 'unique': true},
    {'columns': ['user_url'], 'unique': false},
    {'columns': ['created_at'], 'unique': false}
  ],
  materialized='incremental',
  unique_key=['pull_request_number', 'repo_id'],
  incremental_strategy='delete+insert'
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
    repo_id,
    created_at,
    merged_at,
    closed_at,
    CAST(json_extract_path_text(to_json("{{ get_db_entity_name('user') }}"), 'url') as TEXT) as user_url
  from {{ var("input_schema") }}.pull_requests
  {% if is_incremental() %}
    where created_at > ( select max(created_at) from {{ this }} )
  {% endif %}
),

updates as (
  select *
  from using_clause
  {% if is_incremental() %}
    where (pull_request_number, repo_id) in ( select pull_request_number, repo_id from {{ this }} )
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
