{{ config(
  schema=var('input_schema'),
  indexes=[
    {'columns': ['pull_request_id'], 'unique': true},
    {'columns': ['user_url'], 'unique': false}
  ]
) }}

with pull_requests_extracted as (
    select
      pull_requests.number,
      pull_requests.html_url,
      pull_requests.title,
      pull_requests.draft,
      pull_requests.state,
      pull_requests.repo_id,
      pull_requests.created_at,
      pull_requests.merged_at,
      pull_requests.closed_at,
      to_json("{{ get_db_entity_name('user') }}") as user_json
    from {{ var("input_schema") }}.pull_requests
),

final as (
    select
      repo_id || '/' || number as pull_request_id,
      number as pull_request_number,
      html_url as pull_request_url,
      title as pull_request_title,
      draft as pull_request_draft,
      created_at as created_at,
      merged_at as merged_at,
      closed_at as closed_at,
      CAST(json_extract_path_text(user_json, 'url') as TEXT) as user_url,
      repo_id
    from pull_requests_extracted
)

select * from final
