import asyncio
from pathlib import Path

import pandas as pd
from mimesis import Person
from mimesis import Address
from mimesis.providers.text import Text
from mimesis.providers.finance import Finance
from mimesis.random import Random
import random
from datetime import datetime, timedelta
from time import time
import os
import numpy as np
import attr
import argparse
import logging


person = Person()
address = Address()
text = Text()
finance = Finance()
m_random = Random()
BATCH_SIZE = 10_000
FACT_TO_DIM_RATIO = 100
DIM_RECORDS_PER_MB = 370  # 1MB of parquet data
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MyLogger')


@attr.s(auto_attribs=True, kw_only=False)
class FactParams:
    fact_records: int
    customer_ids: np.ndarray
    product_ids: np.ndarray
    small_quantity: np.ndarray
    big_quantity: np.ndarray
    amount: list[float]
    discount: list[float]
    seconds: list[int]
    start_time: datetime


def parse_args():
    # Create the ArgumentParser object
    parser = argparse.ArgumentParser(description="Generate synthetic data.")

    # Add the scale-factor argument
    # The `type=int` ensures that the input is validated as an integer
    parser.add_argument('-sf', '--scale-factor', type=int, required=True,
                        help='Scale factor - Megabytes of data to generate.')

    # Parse the arguments
    args = parser.parse_args()

    return args


# Function to generate dimension and fact tables
async def generate_dim_customer(num_entries: int) -> pd.DataFrame:
    customers = [{'CustomerID': i,
                  'FirstName': person.first_name(),
                  'LastName': person.last_name(),
                  'Email': person.email(),
                  'Phone': person.phone_number(),
                  'Address': address.address(),
                  'City': address.city(),
                  'State': address.state(),
                  'ZipCode': address.zip_code(),
                  'Country': address.country(),
                  'Age': random.randint(18, 70),
                  'Gender': random.choice(['Male', 'Female', 'Other']),
                  'MembershipStatus': random.choice(['Silver', 'Gold', 'Platinum'])}
                 for i in range(num_entries)]
    return pd.DataFrame(customers)


async def generate_dim_product(num_entries: int) -> pd.DataFrame:
    products = [{'ProductID': i,
                 'ProductName': text.word(),
                 'ProductCategory': random.choice(['Electronics', 'Clothing', 'Home', 'Garden']),
                 'ProductSubcategory': text.word(),
                 'Manufacturer': finance.company(),
                 'SupplierID': m_random.randint(a=1, b=100),
                 'UnitPrice': round(random.uniform(10, 500), 2),
                 'Cost': round(random.uniform(5, 200), 2),
                 'ProductDescription': text.text(),
                 'Size': random.choice(['Small', 'Medium', 'Large']),
                 'Weight': round(random.uniform(1.0, 5.0), 2),
                 'Color': random.choice(['Red', 'Blue', 'Green', 'Yellow'])}
                for i in range(num_entries)]
    return pd.DataFrame(products)


async def generate_fact_sales(fact_params: FactParams) -> pd.DataFrame:
    records = []
    for i in range(0, fact_params.fact_records, BATCH_SIZE):
        batch = [
            {
                'SalesID': j,
                'CustomerID': fact_params.customer_ids[j % len(fact_params.customer_ids)],
                'ProductID': fact_params.product_ids[j % len(fact_params.product_ids)],
                'TransactionDate': fact_params.start_time + timedelta(seconds=fact_params.seconds[j]),
                'Quantity': fact_params.small_quantity[j % len(fact_params.small_quantity)],
                'SalesAmount': fact_params.amount[j % len(fact_params.amount)],
                'Discount': fact_params.discount[j % len(fact_params.discount)],
                'SalesChannel': random.choice(['Online', 'In-store'])
             } for j in range(i, min(i + BATCH_SIZE, fact_params.fact_records))
        ]
        records.extend(batch)
        await asyncio.sleep(0)  # Yield control to allow other tasks
    return pd.DataFrame(records)


async def generate_fact_inventory(fact_params: FactParams) -> pd.DataFrame:
    records = []
    for i in range(0, fact_params.fact_records, BATCH_SIZE):
        batch = [
            {
                'InventoryID': j,
                'ProductID': fact_params.product_ids[j % len(fact_params.product_ids)],
                'TransactionDate': fact_params.start_time + timedelta(seconds=fact_params.seconds[j]),
                'MovementType': random.choice(['Incoming', 'Outgoing']),
                'Quantity': fact_params.big_quantity[j % len(fact_params.big_quantity)],
                'Location': random.choice(['Warehouse', 'Store'])
            } for j in range(i, min(i + BATCH_SIZE, fact_params.fact_records))
        ]
        records.extend(batch)
        await asyncio.sleep(0)  # Yield control to allow other tasks
    return pd.DataFrame(records)


async def preview_data(
    dim_customer_df: pd.DataFrame,
    dim_product_df: pd.DataFrame,
    fact_sales_df: pd.DataFrame,
    fact_inventory_df: pd.DataFrame,
):
    # Example of data
    logger.info("Dimension Customer Sample:")
    logger.info(dim_customer_df.head())
    logger.info("Dimension Product Sample:")
    logger.info(dim_product_df.head())
    logger.info("Fact Sales Sample:")
    logger.info(fact_sales_df.head())
    logger.info("Fact Inventory Sample:")
    logger.info(fact_inventory_df.head())


async def write_data_to_parquet(
    dim_customer_df: pd.DataFrame,
    dim_product_df: pd.DataFrame,
    fact_sales_df: pd.DataFrame,
    fact_inventory_df: pd.DataFrame,
):
    # Save DataFrames to Parquet files
    target_folder = Path('/tmp') / 'generated_data'
    os.makedirs(target_folder, exist_ok=True)
    # No need to parallelize saving to Parquet as it is already fast
    dim_customer_df.to_parquet(target_folder / 'dim_customer.parquet', engine='pyarrow')
    dim_product_df.to_parquet(target_folder / 'dim_product.parquet', engine='pyarrow')
    fact_sales_df.to_parquet(target_folder / 'fact_sales.parquet', engine='pyarrow')
    fact_inventory_df.to_parquet(target_folder / 'fact_inventory.parquet', engine='pyarrow')


async def main():
    args = parse_args()
    dim_records = DIM_RECORDS_PER_MB * args.scale_factor
    fact_records = dim_records * FACT_TO_DIM_RATIO
    # Using asyncio.gather to run tasks concurrently
    logger.info("Generating dimension tables...")
    dim_customer_df, dim_product_df = await asyncio.gather(
        generate_dim_customer(dim_records),
        generate_dim_product(dim_records)
    )
    # After dimension tables are ready, generate fact tables
    logger.info("Generating random numbers...")
    start_time = datetime.now()
    fact_params = FactParams(
        fact_records=fact_records,
        customer_ids=np.random.randint(1, dim_customer_df.size + 1, dim_customer_df.size),
        product_ids=np.random.randint(1, dim_product_df.size + 1, dim_product_df.size),
        small_quantity=np.random.randint(1, 10, fact_records),
        big_quantity=np.random.randint(10, 100, fact_records),
        amount=[round(x, 2) for x in np.random.uniform(100, 1000, fact_records)],
        discount=[round(x, 2) for x in np.random.uniform(0, 0.3, fact_records)],
        start_time=start_time,
        seconds=[np.random.randint(0, 120) for _ in range(fact_records)]
    )
    logger.info("Generating fact tables...")
    fact_sales_df, fact_inventory_df = await asyncio.gather(
        generate_fact_sales(fact_params),
        generate_fact_inventory(fact_params)
    )

    await asyncio.gather(preview_data(dim_customer_df, dim_product_df, fact_sales_df, fact_inventory_df))
    await asyncio.gather(write_data_to_parquet(dim_customer_df, dim_product_df, fact_sales_df, fact_inventory_df))

# Run the main function
start = time()
logger.info("Starting data generation...")
asyncio.run(main())
logger.info('\n' + ('-' * 80) + '\n')
logger.info(f"Data generation completed in {time() - start:.2f} seconds.")
