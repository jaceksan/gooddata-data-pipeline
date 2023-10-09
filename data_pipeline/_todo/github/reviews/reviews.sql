{{ config(
  indexes=[
    {'columns': ['review_id'], 'unique': true},
    {'columns': ['pull_request_id'], 'unique': false}
  ],
  materialized='incremental',
  unique_key='review_id'
) }}

with using_clause as (
  select
    *
  from {{ ref('reviews_extract_json') }}
  {% if is_incremental() %}
    where created_at > ( select max(created_at) from {{ this }} )
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

pull_requests as (
  select * from {{ ref('pull_requests') }}
),

final as (
    select
      r.*,
      p.pull_request_id
    from (
      select * from inserts
      union all select * from updates
    ) r
    join pull_requests p on r.pull_request_url = p.pull_requests_api_url
)

select * from final
