# GoodData Data Pipeline

The document describes some basics of the project of the GoodData data pipeline.

Authors of the project are:

- [Jan Soubusta](https://twitter.com/jaceksan).
- [Patrik Braborec](https://twitter.com/patrikbraborec).

The following articles are based on this project:
- [How To Build a Modern Data Pipeline](https://medium.com/gooddata-developers/how-to-build-a-modern-data-pipeline-cfdd9d14fbea)
- TODO - new article about dbt metrics

# Getting Started

The following paragraphs describe the setting for local development.

## Start GoodData
There are two options:
- Community edition running on your laptop
- GoodData cloud trial

### Community edition
The following command start the single container deployment of GoodData on your machine:
```bash
docker-compose up -d
```

### GoodData trial
Go to [GoodData trial](https://www.gooddata.com/trial/) page, enter your e-mail,
and in few tens of seconds you get your own GoodData instance running in our cloud, managed by us.

## Setup virtual environment
The tutorial on how to set up a virtual environment follows:

```bash
# Create virtual env
virtualenv venv
# Activate virtual env
source venv/bin/activate
#You should see a `(venv)` appear at the beginning of your terminal prompt indicating that you are working inside the `virtualenv`.
# Deactivate virtual env once you are done
deactivate
```

## Environment variables

You will also need to set up `env variables` in the virtual environment.
The following setup is valid for local (docker-compose) deployment.
Modify `DBT_TARGET`, `GOODDATA_HOST` and `GOODDATA_TOKEN` values to run scripts against different environments.

dbt [profiles.yaml](src/profile/profiles.yml) contains database properties for all targets (DB host, ...).
Change them to redirect this demo to your database.

**shared for all data pipeline phases**:
```bash
export DBT_PROFILE_DIR="profile" # default is ~/.dbt
export DBT_PROFILE="default"
export GOODDATA_MODEL_ID="github"
export DBT_TARGET="dev_local"
export POSTGRES_PASS=cicd123
```

**Extract/load data from Github**:
```bash
export GITHUB_TOKEN=<github-token>
# If you want to extract/load only subset of repositories
export REPOSITORIES="--repositories gooddata/gooddata-python-sdk"
```

**Data transformation**:
```bash
# GoodData properties must be set to enable generation and deployment of GoodData semantic model from dbt models
# These variables correspond to GoodData Community Edition (single container deployment)
export GOODDATA_HOST="http://localhost:3000"
export GOODDATA_TOKEN="YWRtaW46Ym9vdHN0cmFwOmFkbWluMTIz"
export GOODDATA_WORKSPACE_ID="development"
export GOODDATA_WORKSPACE_TITLE="Development"
```

**Analytics**:
```bash
export GOODDATA_HOST="http://localhost:3000"
export GOODDATA_TOKEN="YWRtaW46Ym9vdHN0cmFwOmFkbWluMTIz"
export GOODDATA_WORKSPACE_ID="development"
```

## Install dependencies 

If you want to run scripts locally, please install the following dependencies:

```bash
pip install -r src/extract_load/requirements.txt
pip install -r src/requirements.txt
# TODO - create a pip package for dbt-gooddata module
cd src/dbt-gooddata
python setup.py install
```

# Extract and Load

The folder `src/extract_load` contains scripts ([extract.py](extract_load/extract.py), [load.py](extract_load/load.py)) to extract data from [GitHub REST API](https://docs.github.com/en/rest) and load data to [PostgreSQL](https://www.postgresql.org/) database.

The output of this stage is `cicd_input_stage` schema in the database.

During implementation, we discovered that we always do a complete refresh of data and do not do incremental loading that would be more suitable for long-term use. It is possible to solve it programmatically and extend scripts, for example, to create a new table where you keep the state of your data or use other tools such as [Airbyte](https://airbyte.com/) that would solve these problems with data extracting for us.

You can run it locally as well (do not forget to set up env variables!):
```bash
cd src
# dbt-gooddata module helps with reading dbt profiles (single source of truth for database properties)
cd dbt-gooddata && python setup.py install && cd ..
cd extract_load
./extract.py $REPOSITORIES
./load.py --profile-dir ../$DBT_PROFILE_DIR --target $DBT_TARGET $REPOSITORIES
```

# Data transformation

The folder `src/models` contains [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) to transform data from `cicd_input_stage` to `cicd_output_stage` that is used for analytics of data.

As described in the *Extract and Load* section, we do full refresh of tables but dbt allows you to do so-called [incremental models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/configuring-incremental-models) that would allow you transforms only the rows in your source data (in our case `cicd_input_stage`) that you tell dbt to filter for, inserting them into the target table/schema (in our case `cicd_output_stage`).

You can run it locally as well (do not forget to set up env variables!):
```bash
cd src
pip install -r requirements.txt
dbt deps
dbt run --profiles-dir $DBT_PROFILE_DIR --target $DBT_TARGET
dbt test --profiles-dir $DBT_PROFILE_DIR --target $DBT_TARGET
```

## Generate GoodData semantic model from dbt models
Folder [dbt-gooddata](src/dbt-gooddata) contains a PoC of dbt plugin providing generators of GoodData semantic model objects.
Specifically, it allows you to generate so called PDM (Physical Data Model), LDM(Logical Data Model, mapped to PDM), and metrics from dbt models.
It is based on [GoodData Python SDK](https://github.com/gooddata/gooddata-python-sdk).

You can run it locally as well (do not forget to set up env variables!):
```bash
cd src
cd dbt-gooddata && python setup.py install && cd ..
# Run data transformation first, or at least run `dbt compile` command. dbt-gooddata relies on dbt manifest.json.
# Generate PDM/LDM/metrics, deploy them to GoodData
dbt-gooddata deploy_models
# Tool for invalidating caches. Must be executed anytime data in cicd_output_stage schema are changed 
dbt-gooddata upload_notification
```

## Constraints
We wanted to define database constraints. Why? [GoodData](https://www.gooddata.com/) will join automatically between tables if you have tables that have foreign keys. This is a huge benefit that saves time, and also you can avoid mistakes thanks to that. 

We used package [Snowflake-Labs/dbt_constraints](https://github.com/Snowflake-Labs/dbt_constraints) for defining constrains.

## Schema names
The dbt autogenerates the schema name but you can easily change it by custom macro - see our [approach how we dealt with schema names](data_transformation/macros/generate_schema_name.sql).

## Generate all columns into schema.yml files
This can help you to bootstrap schema.yaml files programmatically. Then, you can extend them by additional properties.

Example:
```bash
dbt --profiles-dir ./profile \
  run-operation generate_source \
  --args "{\"schema_name\": \"$POSTGRES_OUTPUT_SCHEMA\", \"generate_columns\": true, \"include_descriptions\": true}"
```

# Analytics
Folder [dbt-gooddata](src/dbt-gooddata) contains a PoC of dbt plugin providing tools for loading/storing GoodData analytics model (metrics, insights, dashboards).
It is based on [GoodData Python SDK](https://github.com/gooddata/gooddata-python-sdk).

## Load analytics model to GoodData
Analytics model is stored in [gooddata_layouts](src/gooddata_layouts) folder.
The following command reads the layout, and load it into the GooData instance (based on environment variables):

```bash
dbt-gooddata deploy_analytics
```

It not only loads the stored layout, but it also reads metrics from dbt models and loads them too.

## Store analytics model
Anytime you can fetch analytics model from the GoodData instance and store it to [gooddata_layouts](src/gooddata_layouts) folder.
It makes sense to do some operations by editing stored layout files, but other in GoodData UI applications.
For instance, it is more convenient to build more complex GoodData MAQL metrics in the Metric Editor UI application.
Then, to persist such metrics to [gooddata_layouts](src/gooddata_layouts) folder, run the following command:

```bash
dbt-gooddata store_analytics
```

## Invalidate analytics cache 

Anytime you update data, e.g. by running `dbt run` command, you have to invalidate GoodData caches to see the new data there.
The following command invalidates these caches:
```bash
dbt-gooddata upload_notification
```

### Test analytics

It is possible to test if all insights (visualizations) are possible to execute - it means that you know if insights (visualizations) render correctly.

Use the following command:
```bash
dbt-gooddata test_insights
```

---

If you want to learn more about the stack described in the document, do not hesitate to contact us.

If you find a bug, please [create a merge request](https://gitlab.com/patrikbraborec/gooddata-data-pipeline/-/merge_requests/new), or [create an issue](https://gitlab.com/patrikbraborec/gooddata-data-pipeline/-/issues/new).
