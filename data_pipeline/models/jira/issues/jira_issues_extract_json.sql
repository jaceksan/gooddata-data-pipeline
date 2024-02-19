{{ config(
  schema=var('input_schema_jira'),
  indexes=[
    {'columns': ['jira_issue_id'], 'unique': true},
    {'columns': ['updated_at'], 'unique': false}
  ],
  materialized='incremental',
  unique_key='jira_issue_id'
) }}

-- Helper step, materialize extracted JSON fields first and then JOIN it with other tables
-- Incremental mode

with using_clause as (
  select
    cast(id as INT) as jira_issue_id,
    key as jira_issue_number,
    self as jira_issue_url,
    fields__summary as summary,
    fields__labels as labels,
    -- TODO: substr may not be supported by all DBs. I did not find an official macro for this.
    --  Worst case scenario is that I will have to write a custom macro for this.
    cast(substr(fields__created, 1, 10) as date) as created_at,
    cast(fields__duedate as date) as due_date_at,
    cast(substr(fields__updated, 1, 10) as date) as updated_at,
    cast(substr(fields__resolutiondate, 1, 10) as date) as closed_at,
    -- TODO - expand the following attributes to a star schema
    {{ extract_json_value('fields__assignee', 'accountId', 'jira_assignee_id', 'TEXT') }},
    {{ extract_json_value('fields__assignee', 'displayName', 'jira_assignee_name', 'TEXT') }},
    {{ extract_json_value('fields__assignee', 'emailAddress', 'jira_assignee_email', 'TEXT') }},
    {{ extract_json_value('fields__creator', 'accountId', 'jira_creator_id', 'TEXT') }},
    {{ extract_json_value('fields__creator', 'displayName', 'jira_creator_name', 'TEXT') }},
    {{ extract_json_value('fields__creator', 'emailAddress', 'jira_creator_email', 'TEXT') }},
    {{ extract_json_value('fields__issuetype', 'id', 'jira_issue_type_id', 'INT') }},
    {{ extract_json_value('fields__issuetype', 'name', 'jira_issue_type_name', 'TEXT') }},
    {{ extract_json_value('fields__priority', 'id', 'jira_priority_id', 'INT') }},
    {{ extract_json_value('fields__priority', 'name', 'jira_priority_name', 'TEXT') }},
    {{ extract_json_value('fields__project', 'id', 'jira_project_id', 'INT') }},
    {{ extract_json_value('fields__project', 'name', 'jira_project_name', 'TEXT') }},
    {{ extract_json_value('fields__resolution', 'id', 'jira_resolution_id', 'INT') }},
    {{ extract_json_value('fields__resolution', 'name', 'jira_resolution_name', 'TEXT') }},
    {{ extract_json_value('fields__status', 'id', 'jira_status_id', 'INT') }},
    {{ extract_json_value('fields__status', 'name', 'jira_status_name', 'TEXT') }},
    {{ extract_json_value('fields__status', 'statusCategory.id', 'jira_status_category_id', 'INT') }},
    {{ extract_json_value('fields__status', 'statusCategory.key', 'jira_status_category_key', 'TEXT') }},
    {{ extract_json_value('fields__status', 'statusCategory.name', 'jira_status_category_name', 'TEXT') }}
  from {{ var("input_schema_jira") }}.issues
  {% if is_incremental() %}
    -- TODO - this may not performn well on large tables. I could materialize the STR column and compare strings instead.
    where cast(substr(fields__updated, 1, 10) as date) > ( select max(updated_at) from {{ this }} )
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
    select *
    from inserts
    union all select * from updates
)

select * from final
