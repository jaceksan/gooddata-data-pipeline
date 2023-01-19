with commits_extracted as (
    select * from {{ ref('commits_extract_json') }}
),

users as (
    select * from {{ ref('users') }}
),

final as (
    select
      commits_extracted.commit_id,
      commits_extracted.commit_url,
      commits_extracted.comment_count,
      commits_extracted.created_at,
      commits_extracted.repo_id,
      users.user_id
    from commits_extracted
    -- Filter out commits without responsible user (data cleansing)
    join users on commits_extracted.user_url = users.user_url
)

select * from final
