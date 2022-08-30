import os
from gooddata_sdk import GoodDataSdk, CatalogWorkspace
from args import parse_arguments
from config import Config


host = os.environ["GOODDATA_HOST"]
token = os.environ["GOODDATA_TOKEN"]
args = parse_arguments()
config = Config(args.config)
workspace = config.get_workspace(args.workspace_id)

sdk = GoodDataSdk.create(host, token)

# Create workspaces, if they do not exist yet, otherwise update them
sdk.catalog_workspace.create_or_update(
    CatalogWorkspace(workspace_id=workspace.id, name=workspace.name)
)

# Deploy logical and analytics model into staging workspace
ldm = sdk.catalog_workspace_content.load_declarative_ldm(workspace.id)
adm = sdk.catalog_workspace_content.load_declarative_analytics_model(workspace.id)

sdk.catalog_workspace_content.put_declarative_ldm(workspace.id, ldm)
sdk.catalog_workspace_content.put_declarative_analytics_model(workspace.id, adm)

print("done")
