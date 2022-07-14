with users as (
    select * from cicd_input_stage.users 
),

final as (
    select 
    
    users.id as user_id, 
    users.url, 
    users.login 
    
    from users
)

select * from final