{{ config(
  unique_key='ProductID'
) }}
--   indexes=[
--     {'columns': ['ProductID'], 'unique': true},
--   ],
with dim_product as (
    select
        ProductID,
        ProductName,
        (CASE WHEN ProductCategory = 'Gardem' THEN 'Garden' ELSE ProductCategory END) AS ProductCategory,
        ProductSubcategory,
        Manufacturer,
        SupplierID,
        UnitPrice,
        Cost,
        ProductDescription,
        Size,
        Weight,
        Color
    from {{ var("input_schema") }}.dim_product
)

select * from dim_product
