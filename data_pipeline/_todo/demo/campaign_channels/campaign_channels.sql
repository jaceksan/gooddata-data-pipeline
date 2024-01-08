with campaign_channels as (
  select
    campaign_channel_id,
    category,
    type,
    cast(budget as decimal(15,2)) as budget,
    cast(spend as decimal(15,2)) as spend,
    campaign_id
  from {{ var("input_schema_demo") }}.campaign_channels
)

select * from campaign_channels
