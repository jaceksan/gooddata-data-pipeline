import argparse

from config import Config


def set_shared_args(parser: argparse.ArgumentParser):
    parser.add_argument('-c', '--config', default='config.yaml',
                        help='Config file defining, what tables should be loaded')
    parser.add_argument('-r', '--repositories', nargs='+', default=[],
                        help='List of github repositories to be crawled/loaded. Full path - org/repo. '
                             'If empty, all from config.yaml are loaded.')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Increase logging level to DEBUG')


def validate_args_repos(config: Config, repos: list[str]) -> dict:
    invalid_repos = []
    valid_orgs = {}

    for full_repo in repos:
        found = False
        input_org, input_repo = full_repo.split("/")
        for conf_org in config.organizations:
            if conf_org.name == input_org:
                valid_repos = []
                for conf_repo in conf_org.repos:
                    if conf_repo == input_repo:
                        valid_repos.append(input_repo)
                        found = True
                valid_orgs[input_org] = valid_repos

        if not found:
            invalid_repos.append(full_repo)

    if invalid_repos:
        raise Exception(f"Following input repos are not in configuration.yaml: {', '.join(invalid_repos)}")
    else:
        return valid_orgs
