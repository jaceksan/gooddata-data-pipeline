with final as (
  select
    "{{ get_db_entity_name('CustomerID') }}" as customerid,
    "{{ get_db_entity_name('Gender') }}" as gender,
    CAST("{{ get_db_entity_name('Age') }}" AS DECIMAL(15, 2)) as age,
    CAST("{{ get_db_entity_name('Annual Income (k$)') }}" AS DECIMAL(15, 2)) as annualincome,
    CAST("{{ get_db_entity_name('Spending Score (1-100)') }}" AS DECIMAL(15, 2)) as spendingscore
  from {{ var("input_schema_data_science") }}.mall_customers
)

select * from final
