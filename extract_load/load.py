#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

from databases.postgres import Postgres
from config import Config, CSV_FILE_PATH_TMPL
from libs.logger import get_logger


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

    def main(self):
        config = Config(self.args.config)
        for table in config.tables:
            self.logger.info(f'Load table {table.name}')
            # TODO - incremental load
            sql = f"DROP TABLE IF EXISTS {table.name} CASCADE"
            self.db.execute_query(sql)

            sql = f"CREATE TABLE {table.name}(item jsonb)"
            self.db.create_table_if_not_exists(sql, table.name)

            self.db.load_json_file(table.name, CSV_FILE_PATH_TMPL.format(table_name=table.name))


if __name__ == "__main__":
    Load().main()
