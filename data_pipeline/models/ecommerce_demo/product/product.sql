with product as (
  select
    product_id,
    ls__product_id__product_name,
    ls__product_id__product_id_image_web,
    product_brand,
    product_category,
    product_image,
    ls__product_image__product_image_web,
    CAST(rating AS DECIMAL(15, 2)) as rating,
    product_rating,
    wdf__product_category
  from {{ var("input_schema_ecommerce_demo") }}.product
)

select * from product
