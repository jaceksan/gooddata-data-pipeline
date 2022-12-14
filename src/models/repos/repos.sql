{{ config(
  indexes=[
    {'columns': ['repo_id'], 'unique': true}
  ]
) }}

with pulls_extracted as (
    select
      pull_request_url
    from {{ ref('pull_requests_extract_json') }}
),

repos_extracted as (
    select *
    from {{ ref('repos_extract_json') }}
),

final as (
    select
      *
    from repos_extracted r
    -- Filter only repos, for which we collected at least one pull request
    where exists (
      select 1 from pulls_extracted p where p.pull_request_url like r.repo_url || '/%'
    )
)

select * from final
