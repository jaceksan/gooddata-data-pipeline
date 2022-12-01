from gooddata_sdk import (
    GoodDataSdk,
    BasicCredentials, CatalogDataSourcePostgres, PostgresAttributes, CatalogDeclarativeTables,
    CatalogWorkspace, CatalogDeclarativeModel
)

from dbt_gooddata.dbt.models import DbtModelTables
from dbt_gooddata.dbt.profiles import DbtProfiles, DbtOutput
from dbt_gooddata.args import parse_arguments
from dbt_gooddata.logger import get_logger
from dbt_gooddata.sdk_wrapper import GoodDataSdkWrapper

# TODO
#   Tests, ...
#   + try to use python-github lib.
#       Sort by date desc and stop when getting to last downloaded (store timestamp in a control table)


def register_data_source(sdk: GoodDataSdk, data_source_id: str, dbt_target: DbtOutput, schema_name: str) -> None:
    sdk.catalog_data_source.create_or_update_data_source(
        CatalogDataSourcePostgres(
            # TODO - add support for all database types
            id=data_source_id,
            name=dbt_target.title,
            db_specific_attributes=PostgresAttributes(
                host=dbt_target.host,
                db_name=dbt_target.dbname
            ),
            # Schema name is collected from dbt manifest from relevant tables
            schema=schema_name,
            credentials=BasicCredentials(
                username=dbt_target.user,
                password=dbt_target.password,
            ),
        )
    )


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


def deploy_models(args, logger, sdk: GoodDataSdk, data_source_id: str, dbt_target: DbtOutput):
    logger.info("Deploy models")
    dbt_tables = DbtModelTables(args.gooddata_model_id)
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


def upload_notification(logger, sdk: GoodDataSdk, data_source_id: str):
    logger.info(f"Upload notification {data_source_id=}")
    sdk.catalog_data_source.register_upload_notification(data_source_id)


def main():
    args = parse_arguments("dbt-gooddata plugin for models management and invalidating caches(upload notification)")
    logger = get_logger("dbt-gooddata", args.debug)
    logger.info("Start")
    dbt_target = DbtProfiles(args).target
    data_source_id = dbt_target.name
    sdk = GoodDataSdkWrapper(args, logger).sdk

    if args.method == "deploy_models":
        deploy_models(args, logger, sdk, data_source_id, dbt_target)
    elif args.method == "upload_notification":
        upload_notification(logger, sdk, data_source_id)
    else:
        raise Exception(f"Unsupported method requested in args: {args.method}")

    logger.info("End")
