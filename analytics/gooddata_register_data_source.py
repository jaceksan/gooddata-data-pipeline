from gooddata_sdk import GoodDataSdk, CatalogDataSourcePostgres, PostgresAttributes, BasicCredentials
import os

host = os.environ["GOODDATA_HOST"]
token = os.environ["GOODDATA_TOKEN"]
data_source_id = os.getenv('GOODDATA_DATA_SOURCE_ID')

sdk = GoodDataSdk.create(host, token)

sdk.catalog_data_source.create_or_update_data_source(
    CatalogDataSourcePostgres(
        id=data_source_id,
        name="CI/CD",
        db_specific_attributes=PostgresAttributes(
            host=os.getenv('POSTGRES_HOST'),
            db_name=os.getenv('POSTGRES_DBNAME')
        ),
        schema=os.getenv('POSTGRES_OUTPUT_SCHEMA'),
        credentials=BasicCredentials(
            username=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASS'),
        ),
    )
)

# Scan data source for tables and store the metadata into GoodData
# GoodData caches the metadata to reduce querying them (costly) in runtime
sdk.catalog_data_source.scan_and_put_pdm(data_source_id)

print("done")
