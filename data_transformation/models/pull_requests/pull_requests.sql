with pull_requests as (
    select * from {{ ref('pull_requests_extract_json') }}
),

users as (
    select * from {{ ref('users') }}
),

repos as (
    select * from {{ ref('repos') }}
),

final as (
    select
      pull_requests.pull_request_id,
      pull_requests.pull_request_url,
      pull_requests.pull_request_title,
      pull_requests.user_id,
      pull_requests.created_at,
      pull_requests.merged_at,
      pull_requests.closed_at,
      repos.repo_id,
      (
        -- Either merged_at, or closed_at(closed without merged) or now(not yet merged or closed)
        extract(epoch from coalesce(pull_requests.merged_at, pull_requests.closed_at, now()))
          - extract(epoch from pull_requests.created_at)
      ) / 3600 / 24 as days_to_solve
    from pull_requests
    -- Filter out commits without responsible user (data cleansing)
    join users on pull_requests.user_id = users.user_id
    join repos on pull_requests.pull_request_url like repos.repo_url || '/%'
)

select * from final
