import sys

from logger import get_logger
from args import parse_arguments_ws
from sdk_wrapper import GoodDataSdkWrapper

args = parse_arguments_ws("Test all insights in requested workspace")
logger = get_logger("gooddata_store_metadata", args.debug)
logger.info("Start")

sdk = GoodDataSdkWrapper(args, logger).sdk

insights = sdk.insights.get_insights(args.gooddata_workspace_id)

for insight in insights:
    try:
        logger.info(f"Executing insight {insight.title} ...")
        sdk.tables.for_insight(args.gooddata_workspace_id, insight)
    except RuntimeError:
        sys.exit()

logger.info("Done")
