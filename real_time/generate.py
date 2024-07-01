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
PATH_TO_WRITE = Path('generated_data') / 'tables'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MyLogger')
TABLES = ['dim_customer', 'dim_product', 'fact_sales', 'fact_inventory']


@attr.s(auto_attribs=True, kw_only=False)
class FactParams:
    fact_records: int
    customer_ids: np.ndarray
    product_ids: np.ndarray
    small_quantity: np.ndarray
    big_quantity: np.ndarray
    amount: list[float]
    discount: list[float]
    seconds: np.ndarray
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
                  'MembershipStatus': random.choice(['Silver', 'Gold', 'Platinum', 'Platimun'])}
                 for i in range(num_entries)]
    return pd.DataFrame(customers)


async def generate_dim_product(num_entries: int) -> pd.DataFrame:
    products = [{'ProductID': i,
                 'ProductName': text.word(),
                 'ProductCategory': random.choice(['Electronics', 'Clothing', 'Home', 'Garden', 'Gardem']),
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
    records = [{
        'SalesID': i,
        'CustomerID': fact_params.customer_ids[i],
        'ProductID': fact_params.product_ids[i],
        'TransactionDate': fact_params.start_time + timedelta(seconds=int(fact_params.seconds[i])),
        'Quantity': fact_params.small_quantity[i],
        'SalesAmount': fact_params.amount[i],
        'Discount': fact_params.discount[i],
        'SalesChannel': random.choice(['Online', 'In-store'])
     } for i in range(1, fact_params.fact_records)]
    return pd.DataFrame(records)


async def generate_fact_inventory(fact_params: FactParams) -> pd.DataFrame:
    records = [{
        'InventoryID': i,
        'ProductID': fact_params.product_ids[i],
        'TransactionDate': fact_params.start_time + timedelta(seconds=int(fact_params.seconds[i])),
        'MovementType': random.choice(['Incoming', 'Outgoing']),
        'Quantity': fact_params.big_quantity[i],
        'Location': random.choice(['Warehouse', 'Store'])
    } for i in range(1, fact_params.fact_records)]
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
    start_time: datetime,
):
    for table in TABLES:
        os.makedirs(PATH_TO_WRITE / table, exist_ok=True)
    # No need to parallelize saving to Parquet as it is already fast
    dim_customer_df.to_parquet(PATH_TO_WRITE / 'dim_customer' / 'dim_customer.parquet', engine='pyarrow')
    dim_product_df.to_parquet(PATH_TO_WRITE / 'dim_product' / 'dim_product.parquet', engine='pyarrow')
    # TODO - include start_time into generated files
    start_time_str = start_time.strftime('%Y_%m_%d_%H_%M_%S')
    fact_sales_df.to_parquet(PATH_TO_WRITE / 'fact_sales' / f'fact_sales_{start_time_str}.parquet', engine='pyarrow')
    fact_inventory_df.to_parquet(
        PATH_TO_WRITE / 'fact_inventory' / f'fact_inventory_{start_time_str}.parquet', engine='pyarrow'
    )


def get_dim_ids(dim_df: pd.DataFrame, id_column: str, fact_values: int) -> np.ndarray:
    return np.random.choice(dim_df[id_column], size=fact_values, replace=True)


def get_random_integers(list_size: int, low: int, high: int) -> np.ndarray:
    return np.random.randint(low, high, list_size)


def get_random_floats(list_size: int, low: float, high: float, precision: int) -> list[float]:
    return [round(x, precision) for x in np.random.uniform(low, high, list_size)]


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
        customer_ids=get_dim_ids(dim_customer_df, "CustomerID", fact_records),
        product_ids=get_dim_ids(dim_product_df, "ProductID", fact_records),
        small_quantity=get_random_integers(fact_records, 1, 10),
        big_quantity=get_random_integers(fact_records, 10, 100),
        amount=get_random_floats(fact_records, 100, 1000, 2),
        discount=get_random_floats(fact_records, 0, 0.3, 2),
        start_time=start_time,
        seconds=get_random_integers(fact_records, 0, 120),
    )
    logger.info("Generating fact tables...")
    fact_sales_df, fact_inventory_df = await asyncio.gather(
        generate_fact_sales(fact_params),
        generate_fact_inventory(fact_params)
    )

    await asyncio.gather(preview_data(dim_customer_df, dim_product_df, fact_sales_df, fact_inventory_df))
    await asyncio.gather(
        write_data_to_parquet(dim_customer_df, dim_product_df, fact_sales_df, fact_inventory_df, start_time)
    )

# Run the main function
start = time()
logger.info("Starting data generation...")
asyncio.run(main())
logger.info('\n' + ('-' * 80) + '\n')
logger.info(f"Data generation completed in {time() - start:.2f} seconds.")
