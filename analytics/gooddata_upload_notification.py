import os

from config import GoodDataSdkWrapper

host = os.environ["GOODDATA_HOST"]
token = os.environ["GOODDATA_TOKEN"]
data_source_id = os.environ["GOODDATA_DATA_SOURCE_ID"]

sdk = GoodDataSdkWrapper.sdk

sdk.catalog_data_source.register_upload_notification(data_source_id)

print("done")
