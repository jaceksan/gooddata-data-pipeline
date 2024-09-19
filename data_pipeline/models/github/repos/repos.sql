with commits_repo_ids as (
    select distinct
      repo_id
    from {{ ref('commits_extract_json') }}
),

repos as (
    select
      CAST(id as bigint) as repo_id,
      html_url as repo_url,
      name as repo_name,
      cast(stargazers_count as bigint) as stargazers_count,
      cast(watchers_count as bigint) as watchers_count,
      -- Use a dedicated name (repo prefix) to do not confuse analytics
      -- From business perspective this is different created_at than in the case of commits/pull_requests
      created_at as repo_created_at,
      {{ extract_org_name("html_url") }} AS org_name
    from {{ var("input_schema_github") }}.repositories
),

final as (
    select
      *
    from repos r
    -- Filter only repos, for which we collected at least one pull request
    where exists (
      select 1 from commits_repo_ids p where p.repo_id = r.repo_id
    )
)

select * from final
