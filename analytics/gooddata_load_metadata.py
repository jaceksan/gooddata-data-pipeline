import os
from pathlib import Path

from gooddata_sdk import CatalogWorkspace, CatalogDeclarativeModel

from dbt.model import DbtTables
from args import parse_arguments_ws
from config import Config, GoodDataSdkWrapper

target_data_source_id = os.environ['GOODDATA_DATA_SOURCE_ID']
args = parse_arguments_ws("Load metadata into GoodData")
config = Config(args.config)
workspace = config.get_workspace(args.workspace_id)

sdk = GoodDataSdkWrapper().sdk

# Create workspaces, if they do not exist yet, otherwise update them
workspace = CatalogWorkspace(workspace_id=workspace.id, name=workspace.name)
sdk.catalog_workspace.create_or_update(workspace=workspace)

# Construct GoodData LDM from dbt models
dbt_tables = DbtTables()
declarative_datasets = dbt_tables.make_declarative_datasets(target_data_source_id)
ldm = CatalogDeclarativeModel.from_dict({"ldm": declarative_datasets}, camel_case=False)

# Load layouts from disk from the configured folder.
# Single folder serves all workspaces in this demo (dev->staging->prod)
adm = sdk.catalog_workspace_content.load_analytics_model_from_disk(Path("gooddata_layouts"))

# Deploy logical and analytics model into target workspace
sdk.catalog_workspace_content.put_declarative_ldm(workspace.id, ldm)
sdk.catalog_workspace_content.put_declarative_analytics_model(workspace.id, adm)

print("done")
