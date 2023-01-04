with pulls_repo_ids as (
    select distinct
      repo_id
    from {{ ref('pull_requests_extract_json') }}
),

repos as (
    select
      id as repo_id,
      html_url as repo_url,
      name as repo_name,
      stargazers_count,
      watchers_count,
      created_at at time zone '{{ var("timezone") }}' as created_at
    from {{ var("input_schema") }}.repositories
),

final as (
    select
      *
    from repos r
    -- Filter only repos, for which we collected at least one pull request
    where exists (
      select 1 from pulls_repo_ids p where p.repo_id = r.repo_id
    )
)

select * from final
