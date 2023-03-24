import argparse
import os


def get_parser(description: str) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        conflict_handler="resolve",
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

def parse_arguments(description: str):
    parser = get_parser(description)
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Increase logging level to DEBUG')

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
    parser.add_argument("-gacc", "--gooddata-allow-clear-caches", action='store_true', default=False,
                        help="Allow button for clearing GoodData caches.")
    return parser.parse_args()
