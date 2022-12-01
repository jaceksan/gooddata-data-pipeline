from pathlib import Path
from logger import get_logger
from args import parse_arguments_ws
from sdk_wrapper import GoodDataSdkWrapper

args = parse_arguments_ws("Get metadata from GoodData and store them to disk")
logger = get_logger("gooddata_store_metadata", args.debug)
logger.info("Start")

sdk = GoodDataSdkWrapper(args, logger).sdk

sdk.catalog_workspace_content.store_analytics_model_to_disk(args.gooddata_workspace_id, Path("gooddata_layouts"))

logger.info("Done")
