from args import parse_arguments_ws
from config import Config, GoodDataSdkWrapper

args = parse_arguments_ws("Get metadata from GoodData and store them to disk")
config = Config(args.config)
workspace = config.get_workspace(args.workspace_id)

sdk = GoodDataSdkWrapper().sdk

sdk.catalog_workspace_content.store_declarative_ldm(workspace.id)
sdk.catalog_workspace_content.store_declarative_analytics_model(workspace.id)

print("done")
