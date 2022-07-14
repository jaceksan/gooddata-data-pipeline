with commits as (
    select * from cicd_input_stage.commits 
),

users as (
    select * from {{ ref('users') }}
),

extract_from_commits as (
    select sha as commit_id, CAST(json_extract_path_text(to_json(author), 'id') as INT) as user_id, created_at from commits
),

final as (
    select 
    
    extract_from_commits.commit_id, 
    extract_from_commits.user_id, 
    users.login, 
    extract_from_commits.created_at 

    from extract_from_commits
 
    left join users on extract_from_commits.user_id = users.user_id

    where extract_from_commits.user_id is not null and users.login is not null
)

select * from final