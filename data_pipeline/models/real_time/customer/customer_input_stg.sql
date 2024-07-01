with dim_customer as (
    select
        *
    from read_parquet('s3://real-time-data/dim_customer.parquet')
)

select * from dim_customer
