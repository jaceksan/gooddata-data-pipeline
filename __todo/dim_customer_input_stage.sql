{{ config(
  schema=var('input_schema'),
  indexes=[
    {'columns': ['CustomerID'], 'unique': true}
  ],
  unique_key='CustomerID'
) }}
with dim_customer as (
    select
        *
    from read_parquet('s3://real-time-data/dim_customer.parquet')
)

select * from dim_customer
