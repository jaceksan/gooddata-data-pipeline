import os
import sys
from gooddata_sdk import GoodDataSdk
from args import parse_arguments_ws
from config import Config

host = os.environ["GOODDATA_HOST"]
token = os.environ["GOODDATA_TOKEN"]
args = parse_arguments_ws("Test all insights in requested workspace")
config = Config(args.config)
workspace = config.get_workspace(args.workspace_id)

sdk = GoodDataSdk.create(host, token)

insights = sdk.insights.get_insights(workspace.id)

for insight in insights:
    try:
        sdk.tables.for_insight(workspace.id, insight)
    except RuntimeError:
        sys.exit()
