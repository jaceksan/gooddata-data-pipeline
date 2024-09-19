{{ config(
  indexes=[
    {'columns': ['workflow_run_id'], 'unique': true},
    {'columns': ['repo_id'], 'unique': false}
  ],
  materialized='incremental',
  unique_key='workflow_run_id'
) }}

with using_clause as (
  select
    cast(id as bigint) as workflow_run_id,
    html_url as workflow_run_url,
    event as workflow_run_event,
    status as workflow_run_status,
    created_at,
    updated_at,
    {{ extract_org_name('html_url') }} as run_org_name,
    cast(repo_id as bigint) as repo_id,
    (
      -- If updated_at is empty, use current timestamp (workflow is still running)
        extract(epoch from coalesce(updated_at, {{ current_timestamp() }}))
        - extract(epoch from created_at)
    ) as workflow_run_duration
  from {{ var("input_schema_github") }}.workflow_runs
  {% if is_incremental() %}
    where created_at > ( select max(created_at) from {{ this }} )
  {% endif %}
),

updates as (
  select *
  from using_clause
  {% if is_incremental() %}
    where workflow_run_id in ( select workflow_run_id from {{ this }} )
  {% else %}
    -- No updates when doing full load
    where 1 = 0
  {% endif %}
),

inserts as (
  select *
  from using_clause
  {% if is_incremental() %}
    where workflow_run_id not in ( select workflow_run_id from {{ this }} )
  {% endif %}
),

repos as (
    select * from {{ ref('repos') }}
),

final as (
    select w.*
    from (
      select * from inserts
      union all select * from updates
    ) w
    -- Filter out workflow_runs without link to repository
    join repos r on w.repo_id = r.repo_id
)

select * from final
