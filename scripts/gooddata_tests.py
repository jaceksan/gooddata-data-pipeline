from gooddata_sdk import GoodDataSdk
import os
import sys

host = os.environ["GOODDATA_HOST"]
token = os.environ["GOODDATA_TOKEN"]
staging_workspace_id = os.environ["STAGING_WORKSPACE_ID"]

sdk = GoodDataSdk.create(host, token)

insights = sdk.insights.get_insights(staging_workspace_id)

for insight in insights:
    try:
        sdk.tables.for_insight(staging_workspace_id, insight)
    except RuntimeError:
        sys.exit()