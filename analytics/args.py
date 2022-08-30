import argparse


def parse_arguments():
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(
        conflict_handler="resolve",
        description="Extracts data from github",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-c', '--config', default='config.yaml',
                        help='Config file defining, what should be crawled')
    parser.add_argument('-w', '--workspace-id',
                        help='Workspace ID, where we want to load metadata')
    return parser.parse_args()
