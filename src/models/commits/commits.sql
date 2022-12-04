with commits as (
    select * from {{ ref('commits_extract_json') }}
),

users as (
    select * from {{ ref('users') }}
),

repos as (
    select * from {{ ref('repos') }}
),

final as (
    select
      commits.commit_id,
      commits.commit_url,
      commits.commit_title,
      commits.user_id,
      commits.created_at,
      repos.repo_id
    from commits
    -- Filter out commits without responsible user (data cleansing)
    join users on commits.user_id = users.user_id
    join repos on commits.commit_url like repos.repo_url || '/%'
)

select * from final
