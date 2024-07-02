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
from datetime import datetime, timezone

DUCKDB_DB_FILE = os.getenv("DUCKDB_DB_FILE")
PATH_GENERATED_DATA = Path(os.getenv("PATH_GENERATED_DATA"))
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION")
REDSHIFT_HOST = os.getenv("REDSHIFT_HOST")
REDSHIFT_USER = os.getenv("REDSHIFT_USER")
REDSHIFT_PASSWORD = os.getenv("REDSHIFT_PASSWORD")
REDSHIFT_DB_NAME = os.getenv("REDSHIFT_DB_NAME")
MOTHERDUCK_DB_NAME = os.getenv("MOTHERDUCK_DB_NAME")
DB_INPUT_SCHEMA = os.getenv("DB_INPUT_SCHEMA")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MyLogger')


def duration(start_time):
    return int((time() - start_time) * 1000)


def connect_to_s3(db_type) -> boto3.client:
    if db_type == "redshift":
        # Create a session using explicit credentials
        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
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


def connect_to_duckdb(is_motherduck: bool):
    if is_motherduck:
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


def read_status_file(db_type: str) -> datetime:
    file_path = PATH_GENERATED_DATA / f"load_{db_type}.status"
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            return datetime.strptime(f.read(), "%Y_%m_%d_%H_%M_%S").replace(tzinfo=timezone.utc)
    else:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)


def write_status_file(start_time, db_type: str):
    with open(PATH_GENERATED_DATA / f"load_{db_type}.status", "w") as f:
        f.write(datetime.strftime(start_time, "%Y_%m_%d_%H_%M_%S"))


def get_files(db_type: str):
    last_load_time = read_status_file(db_type)
    logging.info(f"Last load time for {db_type}: {last_load_time}")
    s3_client = connect_to_s3(db_type)
    s3_objects = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
    return [
        f for f in s3_objects['Contents']
        if last_load_time < f['LastModified'] and f['Key'].startswith('real_time/tables')
    ]


def load_from_minio_to_duckdb(files, is_motherduck: bool):
    con = connect_to_duckdb(is_motherduck)
    for s3_file in files:
        start_file = time()
        file_path = s3_file['Key']
        logging.info(f"Loading file {file_path} into DuckDB")
        table_name = file_path.split('/')[-2]
        logging.info(f"Loading file {file_path} into DuckDB table {table_name}")
        sql_statement = f"""
        CREATE OR REPLACE TABLE {DB_INPUT_SCHEMA}.{table_name} AS
        SELECT * FROM read_parquet('s3://{S3_BUCKET_NAME}/{file_path}');
        """
        logging.debug(f"SQL statement: \n{sql_statement}")
        con.execute(sql_statement)
        logging.info(f"Loaded file {file_path} into DuckDB table {table_name} duration={duration(start_file)}ms")


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


def load_from_s3_to_redshift(files):
    cur = connect_to_redshift()
    redshift_ddl(cur)
    iam_role = os.getenv('REDSHIFT_IAM_ROLE')
    for s3_file in files:
        start_file = time()
        file_path = s3_file['Key']
        table_name = file_path.split('/')[-2]
        logging.info(f"Loading file {file_path} into Redshift table {table_name}")
        sql_statement = f"""
        COPY {table_name} 
        FROM 's3://{S3_BUCKET_NAME}/{file_path}'
        FORMAT AS PARQUET
        IAM_ROLE '{iam_role}'
        """
        logging.debug(f"SQL statement: \n{sql_statement}")
        cur.execute(sql_statement)
        logging.info(f"Loaded Redshift table {table_name} duration={duration(start_file)}ms")


def load_to_duckdb(is_motherduck: bool):
    start_load = time()
    logging.info("Loading to DuckDB...")
    files = get_files("duckdb")
    if len(files) == 0:
        logging.info("No new files to load")
    else:
        load_from_minio_to_duckdb(files, is_motherduck)
        write_status_file(datetime.now(tz=timezone.utc), "duckdb")
    logging.info(f"Load to DuckDB finished duration={duration(start_load)}ms")


def load_to_redshift():
    start_load = time()
    logging.info("Loading to Redshift...")
    files = get_files("redshift")
    if len(files) == 0:
        logging.info("No new files to load")
    else:
        load_from_s3_to_redshift(files)
        write_status_file(datetime.now(tz=timezone.utc), "redshift")
    logging.info(f"Load to Redshift finished duration={duration(start_load)}ms")


def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--duckdb", action="store_true", default=False, help="Load to DuckDB")
    parser.add_argument("--motherduck", action="store_true", default=False, help="Load to MotherDuck")
    parser.add_argument("--redshift", action="store_true", default=False, help="Load to Redshift")
    parser.add_argument(
        "-pd",
        "--profiles-dir",
        help="Directory where dbt profiles.yml is stored",
        default=os.getenv("DBT_PROFILES_DIR", "~/.dbt"),
    )
    return parser.parse_args()


logging.info(f"Load started")
args = parse_args()
if not args.duckdb and not args.redshift:
    logging.warning("No database selected, doing nothing")
else:
    start = time()
    if args.duckdb:
        load_to_duckdb(False)
    if args.motherduck:
        load_to_duckdb(True)
    if args.redshift:
        load_to_redshift()

    logging.info(f"Load complete. duration={duration(start)}ms")
