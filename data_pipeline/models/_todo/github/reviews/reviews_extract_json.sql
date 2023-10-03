{{ config(
  schema=var('input_schema'),
  indexes=[
    {'columns': ['review_id'], 'unique': true},
    {'columns': ['pull_request_url'], 'unique': false}
  ],
  materialized='incremental',
  unique_key='review_id'
) }}

-- Helper step, materialize extracted JSON fields first and then JOIN it with other tables
-- Incremental mode

with using_clause as (
  select
    id as review_id,
    submitted_at as created_at, -- The name equals to other timestamps in the model (shared GoodData date dimension)
    pull_request_url,
    state as review_state
  from {{ var("input_schema") }}.reviews
  {% if is_incremental() %}
    where submitted_at > ( select max(created_at) from {{ this }} )
  {% endif %}
),

updates as (
  select *
  from using_clause
  {% if is_incremental() %}
    where review_id in ( select review_id from {{ this }} )
  {% else %}
    -- No updates when doing full load
    where 1 = 0
  {% endif %}
),

inserts as (
  select *
  from using_clause
  {% if is_incremental() %}
    where review_id not in ( select review_id from {{ this }} )
  {% endif %}
),

final as (
  select * from inserts
  union all select * from updates
)

select * from final