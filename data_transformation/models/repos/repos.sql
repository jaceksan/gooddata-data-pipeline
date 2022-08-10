{{ config(
  indexes=[
    {'columns': ['repo_id'], 'unique': true}
  ]
) }}

with repos as (
  select to_json("item") as item_json from cicd_input_stage.repos
),

pull_requests as (
    select to_json("item") as item_json from cicd_input_stage.pulls
),

pulls_extracted as (
    select
      CAST(json_extract_path_text(item_json, 'html_url') as TEXT) as pull_url
    from pull_requests
),
repos_extracted as (
    select
      CAST(json_extract_path_text(item_json, 'id') as INT) as repo_id,
      CAST(json_extract_path_text(item_json, 'html_url') as TEXT) as repo_url,
      CAST(json_extract_path_text(item_json, 'name') as TEXT) as repo_name
    from repos
),

final as (
    select
      repo_id, repo_url, repo_name
    from repos_extracted r
    -- Filter only repos, for which we collected at least one pull request
    where exists (
      select 1 from pulls_extracted p where p.pull_url like r.repo_url || '/%'
    )
)

select * from final
