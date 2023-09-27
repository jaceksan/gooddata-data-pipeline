{{ config(
  indexes=[
    {'columns': ['user_id'], 'unique': false}
  ],
  materialized='incremental',
  unique_key='user_id'
) }}

-- Incremental mode - insert/update users only from actual increment of commits

with using_clause as (
  select
    user_id,
    login,
    user_avatar_url,
    user_url,
    last_updated
  from (
    select
      user_id,
      login,
      user_avatar_url,
      user_url,
      created_at,
      max(created_at) over (partition by user_id) as last_updated,
      row_number() over (partition by user_id order by created_at desc) as rn
    from {{ var("input_schema_github") }}.commits_extract_json
    -- Remove records with empty user ID
    where user_id is not null
    {% if is_incremental() %}
      and created_at > ( select max(last_updated) from {{ this }} )
    {% endif %}
  ) x
  where x.created_at = x.last_updated and rn = 1
),

updates as (
  select *
  from using_clause
  {% if is_incremental() %}
    where user_id in ( select user_id from {{ this }} )
  {% else %}
    -- No updates when doing full load
    where 1 = 0
  {% endif %}
),

inserts as (
  select *
  from using_clause
  {% if is_incremental() %}
    where user_id not in ( select user_id from {{ this }} )
  {% endif %}
),

final as (
  select * from inserts
  union all select * from updates
)

select * from final
