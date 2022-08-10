# GoodData Data Pipeline

The document describes some basics of the project of the GoodData data pipeline.

Authors of the project are:

- [Jan Soubusta](https://twitter.com/jaceksan).
- [Patrik Braborec](https://twitter.com/patrikbraborec).

You can also read the article that describes the whole flow here.

# Getting Started

The following paragraphs describe the setting for local development.

### Setup virtual environment

Please setup the virtual environment in folders `extract_load` and `analytics` (in both folders separately). The tutorial on how to set up a virtual environment follows:

**Create virtual environment**:

```bash
$ virtualenv venv
```

**Activate virtual environment**:

```bash
$ source venv/bin/activate
```

You should see a `(venv)` appear at the beginning of your terminal prompt indicating that you are working inside the `virtualenv`.

**Leave virtual environment run**:

```bash
$ deactivate
```

You will also need to setup `env variables` in virtual environments:

**extract_load**:

```bash
export GITHUB_TOKEN=<github-token>
export POSTGRES_DBNAME=<postgres-db-name>
export POSTGRES_HOST=<postgres-host>
export POSTGRES_INPUT_SCHEMA=<postgres-input-schema>
export POSTGRES_OUTPUT_SCHEMA=<postgres-output-schema>
export POSTGRES_PASS=<postgres-pass>
export POSTGRES_PORT=<postgres-port>
export POSTGRES_USER=<postgres-user>
```

**analytics**:

```bash
export GOODDATA_HOST=<gooddata-uri>
export GOODDATA_TOKEN=<gooddata-api-token>
export STAGING_WORKSPACE_ID=staging
export PRODUCTION_WORKSPACE_ID=production
export GOODDATA_DATA_SOURCE_ID="cicd"
```

### Install dependencies 

If you want to run scripts locally, please install dependencies in folders `extract_load` and `analytics`:

**extract_load**:

```bash
$ cd extract_load
$ pip install -r requirements.txt
```

**analytics**:

```bash
$ cd analytics
$ pip install -r requirements.txt
```

---

# Extract and Load

The folder `extract_load` contains scripts ([extract.py](extract_load/extract.py), [load.py](extract_load/load.py)) to extract data from [GitHub REST API](https://docs.github.com/en/rest) and load data to [PostgreSQL](https://www.postgresql.org/) database.

The output of this stage is `cicd_input_stage` schema in the database.

During implementation, we discovered that we always do a complete refresh of data and do not do incremental loading that would be more suitable for long-term use. It is possible to solve it programmatically and extend scripts, for example, to create a new table where you keep the state of your data or use other tools such as [Airbyte](https://airbyte.com/) that would solve these problems with data extracting for us.

# Data transformation

The folder `data_transformation` contains [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) to transform data from `cicd_input_stage` to `cicd_output_stage` that is used for analytics of data.

As described in the *Extract and Load* section, we do full refresh of tables but dbt allows you to do so-called [incremental models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/configuring-incremental-models) that would allow you transforms only the rows in your source data (in our case `cicd_input_stage`) that you tell dbt to filter for, inserting them into the target table/schema (in our case `cicd_output_stage`).

### Constraints 

We wanted to define database constraints. Why? [GoodData](https://www.gooddata.com/) will join automatically between tables if you have tables that have foreign keys. This is a huge benefit that saves time and also you can avoid mistakes thanks to that. 

We used package [Snowflake-Labs/dbt_constraints](https://github.com/Snowflake-Labs/dbt_constraints) for defining constrains.

### Schema names

The dbt autogenerates the schema name but you can easily change it by custom macro - see our [approach how we dealt with schema names](data_transformation/macros/generate_schema_name.sql).

# Analytics

The folder `analytics` contains bunch of scripts to manage [GoodData](https://www.gooddata.com/) with [GoodData Python SDK](https://github.com/gooddata/gooddata-python-sdk).

### Connect data to GoodData

The script [gooddata_register_data_source.py](analytics/gooddata_register_data_source.py) connects new data source to GoodData. A data source is a logical object in GoodData that represents the database where your source data is stored. When you create a data source for your database, GoodData scans the database, transforms its metadata to a declarative definition of the physical data model (PDM), and stores the PDM under the data source entity. You then generate a logical data model (LDM) from the stored PDM. If you want to learn more, check the [Connect Data](https://www.gooddata.com/developers/cloud-native/doc/hosted/connect-data/) documentation.

### Store and load analytics metadata

The script [gooddata_store_metadata.py](analytics/gooddata_store_metadata.py) is not part of the pipeline and you have to run it manually. It stores metadata of analytics saved in folder structure [gooddata_layouts](analytics/gooddata_layouts). The script is a pre-requisite for the script [gooddata_load_metadata.py](analytics/gooddata_load_metadata.py).

The script [gooddata_load_metadata.py](analytics/gooddata_load_metadata.py) takes the metadata of analytics saved in folder structure [gooddata_layouts](analytics/gooddata_layouts) and put it in the staging workspace. It is good to save metadata in the folder structure because you immediately gain versioning of analytics.

### Invalidate analytics cache 

The script [gooddata_upload_notification.py](analytics/gooddata_upload_notification.py) invalidate cache of computed reports to force analytics to be recomputed (GoodData caches computation to return results more quickly and not overload the database).

### Test analytics

The script [gooddata_tests.py](analytics/gooddata_tests.p) tests if all insights (visualizations) are possible to execute - it means that you know if insights (visualizations) render correctly.

### Deploy analytics

The script [gooddata_provisioning.py](analytics/gooddata_provisioning.py) loads everything from the staging workspace and put everything in the production workspace. It basically deploys new analytics to production.

---

If you want to learn more about the stack described in the document, do not hesitate to contact us.

If you find a bug, please [create a merge request](https://gitlab.com/patrikbraborec/gooddata-data-pipeline/-/merge_requests/new), or [create an issue](https://gitlab.com/patrikbraborec/gooddata-data-pipeline/-/issues/new).