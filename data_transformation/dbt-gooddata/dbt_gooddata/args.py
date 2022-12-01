import argparse
import os


def get_parser(description: str) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        conflict_handler="resolve",
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )


def set_gooddata_endpoint_args(parser):
    parser.add_argument("-gh", "--gooddata-host",
                        help="Hostname(DNS) where GoodData is running",
                        default=os.getenv("GOODDATA_HOST", "http://localhost:3000"))
    parser.add_argument("-gt", "--gooddata-token",
                        help="GoodData API token for authentication",
                        default=os.getenv("GOODDATA_TOKEN", "YWRtaW46Ym9vdHN0cmFwOmFkbWluMTIz"))
    parser.add_argument("-go", "--gooddata-override-host",
                        help="Override hostname, if necessary. "
                             "When you connect to different hostname than where GoodData is running(proxies)",
                        default=os.getenv("GOODDATA_OVERRIDE_HOST"))


def set_gooddata_deploy_models_args(parser: argparse.ArgumentParser):
    parser.add_argument("-gw", "--gooddata-workspace-id",
                        help="Workspace ID, where we want to load metadata",
                        default=os.getenv("GOODDATA_WORKSPACE_ID"))
    parser.add_argument("-gwt", "--gooddata-workspace-title",
                        help="Workspace title",
                        default=os.getenv("GOODDATA_WORKSPACE_TITLE"))
    parser.add_argument("-gm", "--gooddata-model-id",
                        help="Model ID specified in meta of dbt models. Models(tables) to be included into GoodData.",
                        default=os.getenv("GOODDATA_MODEL_ID"))


def set_dbt_args(parser: argparse.ArgumentParser):
    parser.add_argument("-pd", "--profile-dir",
                        help="Directory where dbt profiles.yml is stored",
                        default="~/.dbt")
    parser.add_argument("-p", "--profile",
                        help="Name of profile from profiles.yml",
                        default="default")
    parser.add_argument("-t", "--target",
                        help="dbt target/output. DB where dbt deploys. GoodData registers it as data source.",
                        default="dev_local")


def parse_arguments(description: str):
    parser = get_parser(description)
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Increase logging level to DEBUG')
    subparsers = parser.add_subparsers(help='actions')
    deploy_models = subparsers.add_parser("deploy_models")
    upload_notification = subparsers.add_parser("upload_notification")
    set_gooddata_endpoint_args(parser)
    set_dbt_args(parser)
    set_gooddata_deploy_models_args(deploy_models)
    deploy_models.set_defaults(method='deploy_models')
    upload_notification.set_defaults(method='upload_notification')
    return parser.parse_args()


def parse_dbt_arguments(description: str):
    parser = get_parser(description)
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Increase logging level to DEBUG')
    set_dbt_args(parser)
    return parser.parse_args()
