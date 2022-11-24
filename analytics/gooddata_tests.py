import sys

from args import parse_arguments_ws
from config import Config, GoodDataSdkWrapper

args = parse_arguments_ws("Test all insights in requested workspace")
config = Config(args.config)
workspace = config.get_workspace(args.workspace_id)

sdk = GoodDataSdkWrapper().sdk

insights = sdk.insights.get_insights(workspace.id)

for insight in insights:
    try:
        sdk.tables.for_insight(workspace.id, insight)
    except RuntimeError:
        sys.exit()
