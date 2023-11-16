{{ config(
  indexes=[
    {'columns': ['created_at'], 'unique': true}
  ],
  materialized='incremental',
  unique_key='created_at'
) }}

with using_clause as (
  select
    *
  from {{ var("input_schema_exchangeratehost") }}.exchange_rate
    {% if is_incremental() %}
  where "{{ get_db_entity_name('date') }}" > ( select max(created_at) from {{ this }} )
      {% endif %}
),

updates as (
  select *
  from using_clause
  {% if is_incremental() %}
    where "{{ get_db_entity_name('date') }}" in ( select created_at from {{ this }} )
  {% else %}
    -- No updates when doing full load
    where 1 = 0
  {% endif %}
),

inserts as (
  select *
  from using_clause
  {% if is_incremental() %}
    where "{{ get_db_entity_name('date') }}" not in ( select created_at from {{ this }} )
  {% endif %}
),

final as (
    select
      "{{ get_db_entity_name('date') }}" as created_at,
      usd,
      czk,
      btc
    from (
      select * from inserts
      union all select * from updates
    ) c
)

select * from final
