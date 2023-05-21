{{ config(
  indexes=[
    {'columns': ['pull_request_number', 'repo_id'], 'unique': true},
    {'columns': ['pull_request_id'], 'unique': true},
    {'columns': ['user_id'], 'unique': false},
    {'columns': ['repo_id'], 'unique': false},
    {'columns': ['created_at'], 'unique': false}
  ],
  materialized='incremental',
  unique_key=['pull_request_number', 'repo_id']
) }}

with using_clause as (
  select *
  from {{ ref('pull_requests_extract_json') }}
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

users as (
    select * from {{ ref('users') }}
),

repos as (
    select * from {{ ref('repos') }}
),

final as (
    select
      repos.repo_name || '/' || p.pull_request_number as pull_request_id,
      p.pull_request_number,
      p.pull_request_url,
      p.pull_request_title,
      p.pull_request_draft,
      p.created_at,
      p.merged_at,
      p.closed_at,
      p.repo_id,
      p.user_id,
      (
        -- Either merged_at, or closed_at(closed without merged) or now(not yet merged or closed)
        extract(epoch from coalesce(p.merged_at, p.closed_at, {{ current_timestamp() }}))
          - extract(epoch from p.created_at)
      ) / 3600 / 24 as days_to_solve
    from (
      select * from inserts
      union all select * from updates
    ) p
    -- Filter out commits without responsible user (data cleansing)
    join users on p.user_id = users.user_id
    join repos on p.repo_id = repos.repo_id
)

select * from final
