from gooddata_sdk import GoodDataSdk
import os

host = os.environ["GOODDATA_HOST"]
token = os.environ["GOODDATA_TOKEN"]
data_source_id = os.environ["GOODDATA_DATA_SOURCE_ID"]

sdk = GoodDataSdk.create(host, token)

sdk.catalog_data_source.register_upload_notification(data_source_id)