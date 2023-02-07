{{ config(
  indexes=[
    {'columns': ['commit_id'], 'unique': true},
    {'columns': ['user_url'], 'unique': false}
  ],
  materialized='incremental',
  unique_key='commit_id',
  incremental_strategy='delete+insert'
) }}

with using_clause as (
  select
    *
  from {{ ref('commits_extract_json') }}
  {% if is_incremental() %}
    where created_at > ( select max(created_at) from {{ this }} )
  {% endif %}
),

updates as (
  select *
  from using_clause
  {% if is_incremental() %}
    where commit_id in ( select commit_id from {{ this }} )
  {% else %}
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

users as (
    select * from {{ ref('users') }}
),

final as (
    select
      c.commit_id,
      c.commit_url,
      c.comment_count,
      c.created_at,
      c.repo_id,
      c.user_url,
      users.user_id
    from (
      select * from inserts
      union all select * from updates
    ) c
    -- Filter out commits without responsible user (data cleansing)
    join users on c.user_url = users.user_url
)

select * from final
