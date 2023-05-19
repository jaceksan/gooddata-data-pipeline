import os
from gooddata_sdk import GoodDataSdk, CatalogWorkspaceSetting
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        conflict_handler="resolve",
        description="Localization of GoodData workspaces",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-gh", "--gooddata-host",
                        help="Hostname(DNS) where GoodData is running",
                        default=os.getenv("GOODDATA_HOST", "http://localhost:3000"))
    parser.add_argument("-gt", "--gooddata-token",
                        help="GoodData API token for authentication",
                        default=os.getenv("GOODDATA_TOKEN", "YWRtaW46Ym9vdHN0cmFwOmFkbWluMTIz"))
    parser.add_argument("-gw", "--gooddata-workspace",
                        help="GoodData workspace ID",
                        default=os.getenv("GOODDATA_WORKSPACE", "faa_development"))
    return parser.parse_args()

args = parse_arguments()
mapbox_token = os.getenv("MAPBOX_ACCESS_TOKEN")
if not mapbox_token:
    raise Exception("You must set env variable MAPBOX_ACCESS_TOKEN with valid MAPBOX token!")
else:
    gooddata_host = "http://localhost:3000"
    gooddata_token = "YWRtaW46Ym9vdHN0cmFwOmFkbWluMTIz"
    workspace_id = args.gooddata_workspace
    workspace_setting_id = "mapboxToken"
    sdk = GoodDataSdk.create(host_=gooddata_host, token_=gooddata_token)
    # TODO - remove delete once the corresponding issue is solved in GoodData
    sdk.catalog_workspace.delete_workspace_setting(workspace_id, workspace_setting_id)
    sdk.catalog_workspace.create_or_update_workspace_setting(
        workspace_id,
        workspace_setting=CatalogWorkspaceSetting(id=workspace_setting_id, content={"value": mapbox_token})
    )
