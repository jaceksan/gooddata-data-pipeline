import os
from gooddata_sdk import GoodDataSdk, CatalogWorkspace
from args import parse_arguments_ws
from config import Config


host = os.environ["GOODDATA_HOST"]
token = os.environ["GOODDATA_TOKEN"]
target_data_source_id = os.environ['GOODDATA_DATA_SOURCE_ID']
args = parse_arguments_ws("Load metadata into GoodData")
config = Config(args.config)
workspace = config.get_workspace(args.workspace_id)

sdk = GoodDataSdk.create(host, token)

# Create workspaces, if they do not exist yet, otherwise update them
sdk.catalog_workspace.create_or_update(
    CatalogWorkspace(workspace_id=workspace.id, name=workspace.name)
)

# Load layouts from disk from the configured folder.
# Single folder serves all workspaces in this demo (dev->staging->prod)
ldm = sdk.catalog_workspace_content.load_declarative_ldm(config.layout_workspace_folder_name)
adm = sdk.catalog_workspace_content.load_declarative_analytics_model(config.layout_workspace_folder_name)

# Stored layouts(LDM) contain a data source ID
# Target workspace can be connected to different workspace
# We have to modify data source ID in LDM in this case
if config.layout_data_source_id != target_data_source_id:
    data_source_mapping = {config.layout_data_source_id: target_data_source_id}
    ldm.modify_mapped_data_source(data_source_mapping)

# Deploy logical and analytics model into target workspace
sdk.catalog_workspace_content.put_declarative_ldm(workspace.id, ldm)
sdk.catalog_workspace_content.put_declarative_analytics_model(workspace.id, adm)

print("done")
