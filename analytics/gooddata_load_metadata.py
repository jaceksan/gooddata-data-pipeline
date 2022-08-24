from gooddata_sdk import GoodDataSdk, CatalogWorkspace
import os

# Comment to demonstrate the run of gooddata_staging and gooddata_production stages.

host = os.environ["GOODDATA_HOST"]
token = os.environ["GOODDATA_TOKEN"]
staging_workspace_id = os.environ["STAGING_WORKSPACE_ID"]
production_workspace_id = os.environ["PRODUCTION_WORKSPACE_ID"]

sdk = GoodDataSdk.create(host, token)

# Create workspaces, if they do not exist yet, otherwise update them
sdk.catalog_workspace.create_or_update(
    CatalogWorkspace(workspace_id=staging_workspace_id, name="Staging")
)

sdk.catalog_workspace.create_or_update(
    CatalogWorkspace(workspace_id=production_workspace_id, name="Production")
)

# Deploy logical and analytics model into staging workspace
sdk.catalog_workspace_content.put_declarative_ldm(
    staging_workspace_id,
    sdk.catalog_workspace_content.load_declarative_ldm(staging_workspace_id)
)
sdk.catalog_workspace_content.put_declarative_analytics_model(
    staging_workspace_id,
    sdk.catalog_workspace_content.load_declarative_analytics_model(staging_workspace_id)
)

print("done")
