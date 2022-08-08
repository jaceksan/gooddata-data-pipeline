from gooddata_sdk import GoodDataSdk
import os

# Comment to demonstrate the run of gooddata_staging and gooddata_production stages.

host = os.environ["GOODDATA_HOST"]
token = os.environ["GOODDATA_TOKEN"]
staging_workspace_id = os.environ["STAGING_WORKSPACE_ID"]

sdk = GoodDataSdk.create(host, token)

sdk.catalog_workspace_content.put_declarative_ldm(
    staging_workspace_id,
    sdk.catalog_workspace_content.load_declarative_ldm(staging_workspace_id)
)
sdk.catalog_workspace_content.put_declarative_analytics_model(
    staging_workspace_id,
    sdk.catalog_workspace_content.load_declarative_analytics_model(staging_workspace_id)
)

print("done")
