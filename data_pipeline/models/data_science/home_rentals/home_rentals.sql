with final as (
  select
    location,
    neighborhood,
    CAST(number_of_rooms AS DECIMAL(15, 2)) as number_of_rooms,
    CAST(number_of_bathrooms AS DECIMAL(15, 2)) as number_of_bathrooms,
    CAST(replace(sqft, ',', '.') AS DECIMAL(15, 2)) as square_feets,
    CAST(days_on_market AS DECIMAL(15, 2)) as days_on_market,
    CAST(initial_price AS DECIMAL(15, 2)) as initial_price,
    CAST(rental_price AS DECIMAL(15, 2)) as rental_price
  from {{ var("input_schema_data_science") }}.home_rentals
)

select * from final
