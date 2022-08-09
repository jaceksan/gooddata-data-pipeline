#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from pathlib import Path

from databases.postgres import Postgres
from config import Config, CSV_FILE_PATH_TMPL_REPO, CSV_FILE_PATH_TMPL_ORG, Table
from libs.logger import get_logger

# Comment to demonstrate the run of extract_load stage.


class Load:
    def __init__(self):
        self.args = self.parse_arguments()
        self.logger = get_logger(Load.__name__, self.args.debug)
        self.db = Postgres(self.logger)

    @staticmethod
    def parse_arguments():
        # noinspection PyTypeChecker
        parser = argparse.ArgumentParser(
            conflict_handler="resolve",
            description="Extracts data from github",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument('-c', '--config', default='config.yaml',
                            help='Config file defining, what should be crawled')
        parser.add_argument('--debug', action='store_true', default=False,
                            help='Increase logging level to DEBUG')
        return parser.parse_args()

    def recreate_table(self, table: Table):
        self.logger.info(f'Recreate table {table.name}')
        # TODO - incremental load
        sql = f"DROP TABLE IF EXISTS {table.name} CASCADE"
        self.db.execute_query(sql)

        sql = f"CREATE TABLE {table.name}(item jsonb)"
        self.db.create_table_if_not_exists(sql, table.name)

    def store_data(self, table: Table, file_name: str):
        self.logger.info(f'Load table {table.name} from file {file_name}')
        self.db.load_json_file(table.name, Path(file_name))

    def main(self):
        config = Config(self.args.config)
        for table in config.tables:
            self.recreate_table(table)
            for org in config.organizations:
                if table.org_level:
                    # Some endpoints are organization-level, e.g. users exist in organization, not in each repo
                    file_name = CSV_FILE_PATH_TMPL_ORG.format(table_name=table.name, org_name=org.name)
                    self.store_data(table, file_name)
                else:
                    for repo in org.repos:
                        file_name = CSV_FILE_PATH_TMPL_REPO.format(
                            table_name=table.name, org_name=org.name, repo_name=repo
                        )
                        self.store_data(table, file_name)


if __name__ == "__main__":
    Load().main()
