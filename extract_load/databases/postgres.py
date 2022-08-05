from __future__ import annotations

from logging import Logger
from typing import Any
from pathlib import Path
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import errors, errorcodes


class Postgres:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.port = os.getenv('POSTGRES_PORT', 5432)
        self.user = os.getenv('POSTGRES_USER', 'postgres')
        self.password = os.getenv('POSTGRES_PASS')
        self.name = os.getenv('POSTGRES_DBNAME')
        self.schema = os.getenv('POSTGRES_INPUT_SCHEMA', 'public')
        self._conn = self.get_connection()
        self._cur = self._conn.cursor()
        self.execute_query(f'SET SEARCH_PATH TO {self.schema}')

    def close_connections(self) -> None:
        if self._conn:
            self._conn.close()

    def get_connection(self) -> Any:
        conn = psycopg2.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn

    def execute_query(self, query: str) -> None:
        self._cur.execute(query)

    def execute_query_fetch_results(self, query: str, include_header: bool = False) -> list[Any]:
        self.execute_query(query)
        data = self._cur.fetchall()
        if include_header:
            data.insert(0, [x.name for x in self._cur.description])
        return data

    def create_table_if_not_exists(self, sql_stmt: str, table_name: str) -> bool:
        table_created = False
        try:
            self.execute_query(sql_stmt)
            table_created = True
        except errors.lookup(errorcodes.DUPLICATE_TABLE):
            self.logger.info(f'skip creating table {table_name}, it has already been created')

        return table_created

    def load_json_file(self, table_name: str, file: Path) -> None:
        stmt = f"""
            COPY {table_name} FROM STDIN CSV QUOTE e'\\x01' DELIMITER e'\\x02'
        """
        with open(file) as fp:
            self._cur.copy_expert(stmt, fp)
