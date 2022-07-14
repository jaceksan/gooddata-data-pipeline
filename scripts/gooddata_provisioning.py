from gooddata_sdk import GoodDataSdk, CatalogWorkspace
import os

host = os.environ["GOODDATA_HOST"]
token = os.environ["GOODDATA_TOKEN"]
staging_workspace_id = os.environ["STAGING_WORKSPACE_ID"]
production_workspace_id = os.environ["PRODUCTION_WORKSPACE_ID"]

sdk = GoodDataSdk.create(host, token)

sdk.catalog_workspace.create_or_update(CatalogWorkspace(production_workspace_id, production_workspace_id))

declarative_ldm = sdk.catalog_workspace_content.get_declarative_ldm(staging_workspace_id)
declarative_analytics_model = sdk.catalog_workspace_content.get_declarative_analytics_model(staging_workspace_id)

sdk.catalog_workspace_content.put_declarative_ldm(production_workspace_id, declarative_ldm)
sdk.catalog_workspace_content.put_declarative_analytics_model(production_workspace_id, declarative_analytics_model)

print("done")