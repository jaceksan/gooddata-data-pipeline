import logging
import os.path
from pathlib import Path
from time import time
import boto3
from botocore.client import Config
import duckdb
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import re
import os
from datetime import datetime
import attr
import argparse

DUCKDB_DB_FILE = os.getenv("DUCKDB_DB_FILE")
PATH_IN_BUCKET = os.getenv("PATH_IN_BUCKET")
PATH_GENERATED_DATA = Path(os.getenv("PATH_GENERATED_DATA"))
PATH_TO_TABLES = Path(os.getenv("PATH_TO_TABLES"))
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION")
REDSHIFT_HOST = os.getenv("REDSHIFT_HOST")
REDSHIFT_USER = os.getenv("REDSHIFT_USER")
REDSHIFT_PASSWORD = os.getenv("REDSHIFT_PASSWORD")
REDSHIFT_DB_NAME = os.getenv("REDSHIFT_DB_NAME")
REDSHIFT_IAM_ROLE = os.getenv('REDSHIFT_IAM_ROLE')
MOTHERDUCK_DB_NAME = os.getenv("MOTHERDUCK_DB_NAME")
DB_INPUT_SCHEMA = os.getenv("DB_INPUT_SCHEMA")
DATE_FORMAT = os.getenv("DATE_FORMAT")
DATETIME_FORMAT = os.getenv("DATETIME_FORMAT")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LoadLogger')


@attr.s(auto_attribs=True, kw_only=True)
class FileToLoad:
    file_path: str
    file_datetime: str
    incremental: bool


@attr.s(auto_attribs=True, kw_only=True)
class TableToLoad:
    table_name: str
    files: list[FileToLoad]
    incremental: bool = False


@attr.s(auto_attribs=True, kw_only=True)
class TablesToLoad:
    tables: list[TableToLoad]
    max_file_datetime: str


def duration(start_time):
    return int((time() - start_time) * 1000)


def connect_to_s3(db_type) -> boto3.client:
    if db_type == "redshift":
        # Create a session using explicit credentials
        if os.getenv('AWS_ACCESS_KEY_ID'):
            session = boto3.Session(
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
                region_name=S3_REGION
            )
        else:
            session = boto3.Session(
                region_name=S3_REGION
            )
        return session.client(
            's3',
            config=Config(signature_version='s3v4'),
        )
    else:
        return boto3.client(
            's3',
            endpoint_url=f"http://{MINIO_ENDPOINT}",
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name=S3_REGION
        )


def connect_to_duckdb(database: str):
    if database == "motherduck":
        con = duckdb.connect(f"md:{MOTHERDUCK_DB_NAME}")
    else:
        con = duckdb.connect(DUCKDB_DB_FILE)
        con.execute('INSTALL httpfs;')
        con.execute('LOAD httpfs;')
        sql_s3_set = f"""
        SET s3_region='us-east-1';
        SET s3_url_style='path';
        SET s3_endpoint='{MINIO_ENDPOINT}';
        SET s3_access_key_id='{MINIO_ACCESS_KEY}';
        SET s3_secret_access_key='{MINIO_SECRET_KEY}';
        SET s3_use_ssl='false';
        """
        con.execute(sql_s3_set)

    con.execute(f"CREATE SCHEMA IF NOT EXISTS {DB_INPUT_SCHEMA};")
    return con


def connect_to_redshift():
    # Initialize DuckDB connection
    con = psycopg2.connect(
        user=REDSHIFT_USER,
        password=REDSHIFT_PASSWORD,
        host=REDSHIFT_HOST,
        port=5439,
        database=REDSHIFT_DB_NAME,
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {DB_INPUT_SCHEMA};")
    cur.execute(f"SET search_path TO {DB_INPUT_SCHEMA}, public;")
    return cur


def connect_to_database(database: str):
    if database == "redshift":
        return connect_to_redshift()
    else:
        return connect_to_duckdb(database)


def read_status_file(db_type: str) -> str:
    file_path = PATH_GENERATED_DATA / f"load_{db_type}.status"
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            return f.read()
    else:
        return "19700101-000000000"


def write_status_file(start_time: str, db_type: str):
    with open(PATH_GENERATED_DATA / f"load_{db_type}.status", "w") as f:
        f.write(start_time)


def exists_table(tables: TablesToLoad, table_name: str) -> bool:
    for table in tables.tables:
        if table.table_name == table_name:
            return True
    return False


def get_files_to_load(args) -> TablesToLoad:
    db_type = args.database
    re_file_time = re.compile(r'^(\d{8}-\d{9,12})\.parquet$')
    last_max_file_datetime = read_status_file(db_type)
    tables_to_load = TablesToLoad(tables=[], max_file_datetime=last_max_file_datetime)
    logging.info(f"Last load time for {db_type}: {last_max_file_datetime}")
    s3_client = connect_to_s3(db_type)
    s3_objects = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
    for s3_object in s3_objects['Contents']:
        file_path = s3_object['Key']
        parts = file_path.split('/')
        if len(parts) > 2:
            table_name = str(parts[2])
            file_name = parts[-1]
            match = re_file_time.match(file_name)
            if match:
                file_datetime = match.group(1)
                if file_datetime > last_max_file_datetime or args.full_refresh:
                    if file_datetime > tables_to_load.max_file_datetime:
                        tables_to_load.max_file_datetime = file_datetime
                    incremental = False
                    if len(parts) == 5:
                        incremental = True
                    file_to_upload = FileToLoad(
                        file_path=file_path,
                        file_datetime=file_datetime,
                        incremental=incremental
                    )
                    if exists_table(tables_to_load, table_name):
                        for table in tables_to_load.tables:
                            if table.table_name == table_name:
                                table.files.append(file_to_upload)
                                if incremental:
                                    # There are incremental files for this table,
                                    # so the table can be loaded incrementally
                                    # Still --full-refresh can override it
                                    table.incremental = True
                    else:
                        tables_to_load.tables.append(
                            TableToLoad(table_name=table_name, files=[file_to_upload], incremental=incremental)
                        )
            else:
                logging.warning(f"File {file_name} does not match the pattern")
    return tables_to_load


def redshift_ddl(cur):
    with open("ddl/redshift_ddl.sql") as fp:
        ddl = fp.read()
        re_split = re.compile(r'^;$', re.M)
        re_sql_comments = re.compile(r'^\s*--.*\n', re.M)
        re_empty_lines = re.compile(r'^\s*\n', re.M)
        queries = re_split.split(ddl)
        for query in queries:
            if re.search(r'[a-zA-Z]', re_sql_comments.sub('', query)):
                stmt = re_empty_lines.sub('', query)
                stmt = re_sql_comments.sub('', stmt)
                first_line = stmt.split("\n").pop(0)
                logging.info(f"Executing DDL query: {first_line}")
                cur.execute(query)


def load_file_from_minio_to_duckdb(con, table_name: str, file_to_load: FileToLoad):
    sql_statement = f"""
    CREATE OR REPLACE TABLE {DB_INPUT_SCHEMA}.{table_name} AS
    SELECT * FROM read_parquet('s3://{S3_BUCKET_NAME}/{file_to_load.file_path}');
    """
    logging.debug(f"SQL statement: \n{sql_statement}")
    con.execute(sql_statement)


def load_file_from_s3_to_redshift(cur, table_name: str, file_to_upload: FileToLoad):
    sql_statement = f"""
    COPY {table_name} 
    FROM 's3://{S3_BUCKET_NAME}/{file_to_upload.file_path}'
    FORMAT AS PARQUET
    IAM_ROLE '{REDSHIFT_IAM_ROLE}'
    """
    logging.debug(f"SQL statement: \n{sql_statement}")
    cur.execute(sql_statement)


def find_newest_file(files: list[FileToLoad]) -> FileToLoad:
    newest_file = files[0]
    for file in files:
        if file.file_datetime > newest_file.file_datetime:
            newest_file = file
    return newest_file


def load_files(con, table_name: str, files_to_upload: list[FileToLoad], database: str) -> None:
    for file_to_load in files_to_upload:
        start_file = time()
        file_path = file_to_load.file_path
        logging.info(f"Loading file {file_path} into {database} table {table_name}")

        if database == "redshift":
            load_file_from_s3_to_redshift(con, table_name, file_to_load)
        else:
            load_file_from_minio_to_duckdb(con, table_name, file_to_load)

        logging.info(f"Loaded file {file_path} into {database} table {table_name} duration={duration(start_file)}ms")


def prepare_tables(con, tables_to_load: TablesToLoad, args):
    # Drop tables if full refresh is requested
    if args.full_refresh:
        for table_to_load in tables_to_load.tables:
            con.execute(f"DROP TABLE IF EXISTS {table_to_load.table_name} CASCADE;")

    # Init tables. Some database can derive from PARQUET, some need static DDL.
    if args.database == "redshift":
        # Redshift cannot derive DDL from PARQUET
        redshift_ddl(con)
    elif args.database in ["duckdb", "motherduck"]:
        for table_to_load in tables_to_load.tables:
            # DuckDB can derive DDL from PARQUET
            first_file = table_to_load.files[0]
            sql_statement = f"""
                CREATE TABLE IF NOT EXISTS {DB_INPUT_SCHEMA}.{table_to_load.table_name} AS
                SELECT * FROM read_parquet('s3://{S3_BUCKET_NAME}/{first_file.file_path}') WHERE 1=0;
                """
            logging.debug(f"SQL statement: \n{sql_statement}")
            con.execute(sql_statement)
    else:
        raise ValueError(f"Unsupported database: {args.database}")


def load_tables(tables_to_load: TablesToLoad, args):
    database = args.database
    con = connect_to_database(database)
    prepare_tables(con, tables_to_load, args)

    for table_to_load in tables_to_load.tables:
        table_name = table_to_load.table_name
        # There can be more files for non-incremental tables
        # Always load only the last one
        if not table_to_load.incremental:
            files_to_upload = [find_newest_file(table_to_load.files)]
        else:
            if args.full_refresh:
                files_to_upload = [f for f in table_to_load.files if not f.incremental]
            else:
                files_to_upload = [f for f in table_to_load.files if f.incremental]

        load_files(con, table_name, files_to_upload, database)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--database", choices=["duckdb", "motherduck", "redshift"], default="duckdb",
        help="Database to load to"
    )
    default_profile_dir = os.getenv("DBT_PROFILES_DIR", "~/.dbt")
    parser.add_argument(
        "-pd",
        "--profiles-dir",
        help=f"Directory where dbt profiles.yml is stored. Default={default_profile_dir}",
        default=default_profile_dir,
    )
    parser.add_argument("-f", "--full-refresh", action="store_true", default=False, help="Full refresh")
    return parser.parse_args()


def main():
    start = time()
    args = parse_args()
    logging.info(f"Load to {args.database} started")
    tables_to_load = get_files_to_load(args)
    if len(tables_to_load.tables) == 0:
        logging.info("No new files to load")
    else:
        load_tables(tables_to_load, args)
        write_status_file(tables_to_load.max_file_datetime, "duckdb")
    logging.info(f"Load to {args.database} completed. duration={duration(start)}ms")


if __name__ == "__main__":
    main()
