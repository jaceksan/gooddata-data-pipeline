#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import os

from config import (CSV_FILE_PATH_TMPL_ORG, CSV_FILE_PATH_TMPL_REPO,
                    DEFAULT_DATE_FROM, Config, Table)
from libs.logger import get_logger
from libs.rest_api import RestApi


class Extract:
    def __init__(self):
        self.args = self.parse_arguments()
        self.logger = get_logger(Extract.__name__, self.args.debug)

        self.api_token = os.getenv('GITHUB_TOKEN')
        self.headers = {
            "Accept": "application/vnd.github+json",
            "charset": "utf-8"
        }
        self.rest_api = RestApi(
            self.logger,
            f'{self.args.endpoint}',
            self.headers,
            wait_api_time=10,
            api_token=self.api_token,
            token_name='token'
        )
        self.per_page = 100

    @staticmethod
    def parse_arguments():
        # noinspection PyTypeChecker
        parser = argparse.ArgumentParser(
            conflict_handler="resolve",
            description="Extracts data from github",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument('-e', '--endpoint', default='https://api.github.com',
                            help='Github endpoint URL')
        parser.add_argument('-c', '--config', default='config.yaml',
                            help='Config file defining, what should be crawled')
        parser.add_argument('--debug', action='store_true', default=False,
                            help='Increase logging level to DEBUG')
        return parser.parse_args()

    @staticmethod
    def write_json(file_name: str, data):
        with open(file_name, 'w') as fp:
            for row in data:
                fp.write(json.dumps(row) + '\n')

    @staticmethod
    def get_endpoint(table: Table, org: str, repo: str):
        return table.endpoint.format(org=org, repo=repo)

    def get_params(self, page: int, table: Table):
        params = {'per_page': self.per_page, 'page': page}
        if table.date_col:
            params['sort'] = table.date_col
            params['direction'] = 'asc'
            params['q'] = f'{table.date_col}:%3E={DEFAULT_DATE_FROM}'
        if table.custom_params:
            params = params | table.custom_params
        return params

    def get_pages(self, table: Table, org: str, repo: str = None):
        endpoint = self.get_endpoint(table, org, repo)
        self.logger.info(f'get_pages endpoint={endpoint}')
        page = 1
        params = self.get_params(page, table)
        result = []
        batch = self.rest_api.get(endpoint, params=params).json()
        result.extend(batch)
        while batch:
            self.logger.info(f'get_pages endpoint={endpoint} done={len(result)}')
            page += 1
            params = self.get_params(page, table)
            batch = self.rest_api.get(endpoint, params=params).json()
            result.extend(batch)
        return result

    def main(self):
        config = Config(self.args.config)
        for org in config.organizations:
            for table in config.tables:
                if table.org_level:
                    # Some endpoints are organization-level, e.g. users exist in organization, not in each repo
                    data = self.get_pages(table, org.name)
                    file_name = CSV_FILE_PATH_TMPL_ORG.format(table_name=table.name, org_name=org.name)
                    self.write_json(file_name, data)
                else:
                    for repo in org.repos:
                        data = self.get_pages(table, org.name, repo)
                        file_name = CSV_FILE_PATH_TMPL_REPO.format(
                            table_name=table.name, org_name=org.name, repo_name=repo
                        )
                        self.write_json(file_name, data)


if __name__ == "__main__":
    Extract().main()
