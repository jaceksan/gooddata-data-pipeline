with carriers as (
  select
    code,
    name,
    nickname
  from {{ var("input_schema") }}.carriers
)

select * from carriers
