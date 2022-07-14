with pull_requests as (
    select * from cicd_input_stage.pull_requests 
),

users as (
    select * from {{ ref('users') }}
),

extract_from_pull_requests as (
    select id as pull_request_id, CAST(json_extract_path_text(to_json("user"), 'id') as INT) as user_id, created_at, merged_at from pull_requests
),

final as (
    select 
    
    extract_from_pull_requests.pull_request_id, 
    extract_from_pull_requests.user_id, 
    users.login, 
    extract_from_pull_requests.created_at, 
    extract_from_pull_requests.merged_at 

    from extract_from_pull_requests
 
    left join users on extract_from_pull_requests.user_id = users.user_id

    where extract_from_pull_requests.user_id is not null and users.login is not null and extract_from_pull_requests.merged_at is not null
)

select * from final
