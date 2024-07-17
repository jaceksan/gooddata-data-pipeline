# Real-time demo
Generate data, upload to Minio/S3, and load to DuckDB/Redshift.
Then deliver the corresponding LDM/ADM to GoodData.

## Prerequisites
Start Minio in root folder:
```bash
docker compose up -d minio minio-bootstrap
```

Install Python dependencies:
```bash
make dev
```

# Activate the virtual environment:
```bash
source .venv/bin/activate
```

## Quick start
Create a new .env file. You can use the template [env_example](env_example).
Set up the environment:
```bash
# For local env
source .env local
# For cloud env with Redshift
source .env cloud
# Local and cloud must be separated because some variables are in conflict (e.g. AWS_ACCESS_KEY_ID)
```

Then check the [Makefile](Makefile) for available commands.
You can execute atomic steps or the whole pipeline like this:
```bash
# Local with DuckDB
make elt_local
# Cloud with Redshift
make elt_cloud
make deploy_models
make deploy_and_test_analytics
```
