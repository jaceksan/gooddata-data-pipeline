with campaigns as (
  select
    campaign_id,
    campaign_name
  from {{ var("input_schema_demo") }}.campaigns
)

select * from campaigns
