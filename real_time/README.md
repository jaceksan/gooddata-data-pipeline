# Real-time demo
Generate data, upload to Minio/S3, and load to DuckDB/Redshift.
Then deliver the corresponding LDM/ADM to GoodData.

## Prerequisites

Install Python dependencies:
```shell
make dev
```

Activate the virtual environment:
```shell
source .venv/bin/activate
```

Create a new .env file. You can use the template [env_example](env_example).
Set up the environment:
```shell
### For local env
source .env local

### For cloud env with Redshift
# Local and cloud must be separated because some variables are in conflict (e.g. AWS_ACCESS_KEY_ID)
# Use "temp" parameter if you have to use AWS credentials.
# Otherwise, use SSO login

# SSO version:
aws sso login
source .env cloud

# AWS credentials version:
source .env cloud temp
```

Start Minio in root folder if you want to test it locally with DucKDB:
```shell
docker compose up -d minio minio-bootstrap
```

## Quick start

Data are generated and stored in folders based on if the related table is loaded incrementally or not.
Incremental:
`$PATH_IN_BUCKET/$PATH_TO_TABLES/<table_name>/<date string, e.g. 20240101>/<datetime string, e.g. 20240101-00000000000>`
Non-incremental:
`$PATH_IN_BUCKET/$PATH_TO_TABLES/<table_name>/<datetime string, e.g. 20240101-00000000000>`

Moreover, if you trigger commands with --full-refresh flag, the data will be stored in the non-incremental way.
Then, if trigger the load with --full-refresh, even the incremental tables will be loaded in the non-incremental way.

Check the [Makefile](Makefile) for available commands.
You can execute atomic steps or the whole pipeline like this:
```shell
# Full-refresh can be triggered like this:
# export FR="--full-refresh"

# Local with DuckDB
make elt_local
# Cloud with Redshift
make elt_cloud
make deploy_models
make deploy_and_test_analytics
```
