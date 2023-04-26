import os
from gooddata_sdk import GoodDataSdk, CatalogWorkspaceSetting


mapbox_token = os.getenv("MAPBOX_ACCESS_TOKEN")
if not mapbox_token:
    raise Exception("You must set env variable MAPBOX_ACCESS_TOKEN with valid MAPBOX token!")
else:
    gooddata_host = "http://localhost:3000"
    gooddata_token = "YWRtaW46Ym9vdHN0cmFwOmFkbWluMTIz"
    sdk = GoodDataSdk.create(host_=gooddata_host, token_=gooddata_token)
    sdk.catalog_workspace.create_or_update_workspace_setting(
        "faa_development",
        workspace_setting=CatalogWorkspaceSetting(id="mapboxToken", content={"value": mapbox_token})
    )
