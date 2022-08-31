import argparse


def get_parser(description: str) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        conflict_handler="resolve",
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )


def set_config_arg(parser):
    parser.add_argument('-c', '--config', default='config.yaml',
                        help='Config file defining, what should be crawled')


def set_workspace_arg(parser):
    parser.add_argument('-c', '--config', default='config.yaml',
                        help='Config file defining, what should be crawled')
    parser.add_argument('-w', '--workspace-id',
                        help='Workspace ID, where we want to load metadata')


def parse_arguments_ws(description: str):
    parser = get_parser(description)
    set_config_arg(parser)
    set_workspace_arg(parser)
    return parser.parse_args()


def parse_arguments(description: str):
    parser = get_parser(description)
    set_config_arg(parser)
    return parser.parse_args()
