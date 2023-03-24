with carriers as (
  select
    code,
    name,
    nickname
  from {{ var("input_schema_faa") }}.carriers
)

select * from carriers
