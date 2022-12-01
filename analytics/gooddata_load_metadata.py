from pathlib import Path

from logger import get_logger
from args import parse_arguments_ws
from sdk_wrapper import GoodDataSdkWrapper

args = parse_arguments_ws("Load analytics metadata into GoodData")
logger = get_logger("gooddata_load_metadata", args.debug)
logger.info("Start")

sdk = GoodDataSdkWrapper(args, logger).sdk

# Load analytics layouts from disk from the configured folder.
# Single folder serves all workspaces in this demo (dev->staging->prod)
logger.info("Read analytics model from disk")
adm = sdk.catalog_workspace_content.load_analytics_model_from_disk(Path("gooddata_layouts"))

# Deploy analytics model into target workspace
logger.info("Load analytics model into GoodData")
sdk.catalog_workspace_content.put_declarative_analytics_model(args.gooddata_workspace_id, adm)

logger.info("Done")
