import sys
from pathlib import Path
from time import time

from gooddata_sdk import (
    GoodDataSdk,
    CatalogDeclarativeTables, CatalogWorkspace, CatalogDeclarativeModel
)

from dbt_gooddata.dbt.metrics import DbtModelMetrics
from dbt_gooddata.dbt.tables import DbtModelTables
from dbt_gooddata.dbt.profiles import DbtProfiles, DbtOutput
from dbt_gooddata.args import parse_arguments
from dbt_gooddata.logger import get_logger
from dbt_gooddata.sdk_wrapper import GoodDataSdkWrapper


GOODDATA_LAYOUTS_DIR = Path("gooddata_layouts")

# TODO
#   add support for other database types (Snowflake first)
#   Tests, ...


def register_data_source(sdk: GoodDataSdk, data_source_id: str, dbt_target: DbtOutput, schema_name: str) -> None:
    data_source = dbt_target.to_gooddata(data_source_id, schema_name)
    sdk.catalog_data_source.create_or_update_data_source(data_source)


def generate_and_put_pdm(sdk: GoodDataSdk, data_source_id: str, dbt_tables: DbtModelTables) -> None:
    # Construct GoodData PDM from dbt models and put it to the server
    # GoodData caches the metadata to reduce querying them (costly) in runtime.
    pdm = dbt_tables.make_pdm()
    declarative_tables = CatalogDeclarativeTables.from_dict(pdm, camel_case=False)
    sdk.catalog_data_source.put_declarative_pdm(data_source_id, declarative_tables)


def create_workspace(sdk: GoodDataSdk, workspace_id: str, workspace_title: str) -> None:
    # Create workspaces, if they do not exist yet, otherwise update them
    workspace = CatalogWorkspace(workspace_id=workspace_id, name=workspace_title)
    sdk.catalog_workspace.create_or_update(workspace=workspace)


def generate_and_put_ldm(sdk: GoodDataSdk, data_source_id: str, workspace_id: str, dbt_tables: DbtModelTables) -> None:
    # Construct GoodData LDM from dbt models
    declarative_datasets = dbt_tables.make_declarative_datasets(data_source_id)
    ldm = CatalogDeclarativeModel.from_dict({"ldm": declarative_datasets}, camel_case=False)

    # Deploy logical into target workspace
    sdk.catalog_workspace_content.put_declarative_ldm(workspace_id, ldm)


def deploy_models(args, logger, sdk: GoodDataSdk, data_source_id: str, dbt_target: DbtOutput) -> None:
    logger.info("Deploy models")
    dbt_tables = DbtModelTables(args.gooddata_model_id, args.gooddata_upper_case)
    workspace_id = args.gooddata_workspace_id
    workspace_title = args.gooddata_workspace_title

    logger.info(f"Register data source {data_source_id=} schema={dbt_tables.schema_name}")
    register_data_source(sdk, data_source_id, dbt_target, dbt_tables.schema_name)
    logger.info(f"Generate and put PDM")
    generate_and_put_pdm(sdk, data_source_id, dbt_tables)
    logger.info(f"Create workspace {workspace_id=}")
    create_workspace(sdk, workspace_id, workspace_title)
    logger.info(f"Generate and put LDM")
    generate_and_put_ldm(sdk, data_source_id, workspace_id, dbt_tables)


def upload_notification(logger, sdk: GoodDataSdk, data_source_id: str) -> None:
    logger.info(f"Upload notification {data_source_id=}")
    sdk.catalog_data_source.register_upload_notification(data_source_id)


def deploy_analytics(args, logger, sdk: GoodDataSdk) -> None:
    logger.info("Read analytics model from disk")
    adm = sdk.catalog_workspace_content.load_analytics_model_from_disk(Path("gooddata_layouts"))

    logger.info("Append dbt metrics to GoodData metrics")
    dbt_gooddata_metrics = DbtModelMetrics(args.gooddata_model_id, args.gooddata_upper_case).make_gooddata_metrics()
    adm.analytics.metrics = adm.analytics.metrics + dbt_gooddata_metrics

    # Deploy analytics model into target workspace
    logger.info("Load analytics model into GoodData")
    sdk.catalog_workspace_content.put_declarative_analytics_model(args.gooddata_workspace_id, adm)


def store_analytics(args, logger, sdk: GoodDataSdk) -> None:
    logger.info("Store analytics model to disk")
    sdk.catalog_workspace_content.store_analytics_model_to_disk(args.gooddata_workspace_id, GOODDATA_LAYOUTS_DIR)

    # TODO - this is hack. Add corresponding functionality into Python SDK
    logger.info("Exclude dbt metrics from stored analytics model, they are already defined in dbt models")
    dbt_gooddata_metrics = DbtModelMetrics(args.gooddata_model_id, args.gooddata_upper_case).make_gooddata_metrics()
    for metric in dbt_gooddata_metrics:
        metric_path = GOODDATA_LAYOUTS_DIR / "analytics_model" / "metrics" / f"{metric.id}.yaml"
        metric_path.unlink()


def test_insights(args, logger, sdk: GoodDataSdk) -> None:
    logger.info("Test insights")
    insights = sdk.insights.get_insights(args.gooddata_workspace_id)

    for insight in insights:
        try:
            start = time()
            sdk.tables.for_insight(args.gooddata_workspace_id, insight)
            duration = int((time() - start) * 1000)
            logger.info(f"Test successful insight=\"{insight.title}\" duration={duration}(ms) ...")
        except RuntimeError:
            sys.exit()


def main():
    args = parse_arguments("dbt-gooddata plugin for models management and invalidating caches(upload notification)")
    logger = get_logger("dbt-gooddata", args.debug)
    logger.info("Start")
    sdk = GoodDataSdkWrapper(args, logger).sdk

    if args.method == "store_analytics":
        store_analytics(args, logger, sdk)
    elif args.method == "deploy_analytics":
        deploy_analytics(args, logger, sdk)
    elif args.method == "test_insights":
        test_insights(args, logger, sdk)
    else:
        dbt_target = DbtProfiles(args).target
        data_source_id = dbt_target.name
        if args.method == "deploy_models":
            deploy_models(args, logger, sdk, data_source_id, dbt_target)
        elif args.method == "upload_notification":
            upload_notification(logger, sdk, data_source_id)
        else:
            raise Exception(f"Unsupported method requested in args: {args.method}")

    logger.info("End")
