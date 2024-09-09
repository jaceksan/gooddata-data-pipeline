{{ config(
  unique_key='CustomerID'
) }}
-- {'columns': ['Email'], 'unique': true}
-- Generator generates duplicate emails. Later on we can implement a logic removing such duplicates.
--   indexes=[
--     {'columns': ['CustomerID'], 'unique': true},
--   ],

with dim_customer as (
    select
        CustomerID,
        FirstName,
        LastName,
        Email,
        Phone,
        Address,
        City,
        State,
        ZipCode,
        Country,
        Age,
        Gender,
        (CASE WHEN MembershipStatus = 'Platimun' THEN 'Platinum' ELSE MembershipStatus END) as MembershipStatus
    from {{ var("input_schema") }}.dim_customer
)

select * from dim_customer
