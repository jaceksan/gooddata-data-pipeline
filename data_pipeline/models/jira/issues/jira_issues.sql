{{ config(
  indexes=[
    {'columns': ['jira_issue_id'], 'unique': true},
    {'columns': ['updated_at'], 'unique': false}
  ],
  materialized='incremental',
  unique_key='jira_issue_id'
) }}

with using_clause as (
  select *
  from {{ ref('jira_issues_extract_json') }}
  {% if is_incremental() %}
    where updated_at > ( select max(updated_at) from {{ this }} )
  {% endif %}
),

updates as (
  select *
  from using_clause
  {% if is_incremental() %}
    where jira_issue_id in ( select jira_issue_id from {{ this }} )
  {% else %}
    -- No updates when doing full load
    where 1 = 0
  {% endif %}
),

inserts as (
  select *
  from using_clause
  {% if is_incremental() %}
    where jira_issue_id not in ( select jira_issue_id from {{ this }} )
  {% endif %}
),

final as (
    select
      j.*,
      (
        -- closed_at or now(not yet closed)
        extract(epoch from coalesce(j.closed_at, {{ current_timestamp() }}))
          - extract(epoch from j.created_at)
      ) / 3600 / 24 as jira_days_to_solve,
      (
        -- if due_date_at is set, calculate if we met it
        case
          when j.due_date_at is not null then
            extract(epoch from coalesce(j.closed_at, {{ current_timestamp() }}))
              - extract(epoch from j.due_date_at)
          end
      ) / 3600 / 24 as jira_days_due_date_exceeded
    from (
      select * from inserts
      union all select * from updates
    ) j
)

select * from final
