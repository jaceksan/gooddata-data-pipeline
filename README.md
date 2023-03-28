# GoodData Data Pipeline

The demo inside this repository demonstrates e2e data pipeline following best software engineering practices.
It realizes the following steps:
- crawls data from sources ([Meltano](https://meltano.com/))
- loads data into a warehouse ([Meltano](https://meltano.com/))
- transforms data in the warehouse in a multi-dimensional model ready for analytics ([dbt](https://www.getdbt.com/))
- generates semantic model from physical model ([GoodData](https://www.gooddata.com/) model from [dbt](https://www.getdbt.com/) models)
- deploys analytics model (metrics, insights, dashboards) from locally stored [layout files](data_pipeline/gooddata_layouts/)
- deploys UI data apps coupled with the data pipeline. Read more details in [apps folder](apps/) 

Delivery into dev/staging/prod environments is orchestrated by [Gitlab](https://gitlab.com/) (except the data apps).
Data apps are delivered by [render.com](render.com) service after merge to `main` branch (staging), and after merge to `prod` branch(production).

Generally, you can change the whole data pipeline and UI apps by a single commit, and deliver everything consistently.

![Demo architecture](docs/MDS.png "Demo architecture")

Latest changes are highlighted by the green color. 

## If you need help
This README is just a brief how-to, it does not contain all details. If you need help, do not hesitate to ask in our [Slack community](https://www.gooddata.com/slack/).

## Authors
- [Jan Soubusta](https://twitter.com/jaceksan)
- [Patrik Braborec](https://twitter.com/patrikbraborec)

## Related articles
The following articles are based on this project:
- [How To Build a Modern Data Pipeline](https://medium.com/gooddata-developers/how-to-build-a-modern-data-pipeline-cfdd9d14fbea)
- [How GoodData Integrates With dbt](https://medium.com/gooddata-developers/how-gooddata-integrates-with-dbt-a0c6f207eca3)
- [Extending CI/CD data pipeline with Meltano](https://medium.com/gooddata-developers/extending-ci-cd-data-pipeline-with-meltano-7de3bce74f57)
- [Analytics Inside Virtual Reality: Too Soon?](TODO)

## Getting Started
I recommend to begin on your localhost, starting the whole ecosystem using [docker-compose.yaml](docker-compose.yaml) file.
It utilizes the [GoodData Community Edition](https://hub.docker.com/r/gooddata/gooddata-cn-ce) available for free in DockerHub.

```bash
# Build custom images based on Meltano, dbt and GoodData artefacts
docker-compose build
# Start GoodData, and Minio(AWS S3 Meltano state backend)
docker-compose up -d gooddata-cn-ce minio minio-bootstrap
# Wait 1-2 minutes to services successfully start

# Allow https://localhost:8443 in CORS
# This enables testing of locally started UI apps based on UI.SDK (examples in /apps folder) 
docker-compose up bootstrap_origins

# Extract/load pipeline based on Meltano
# Github token for authenticating with Github REST API 
export TAP_GITHUB_AUTH_TOKEN="<my github token>"
# Set AWS S3 credentials to be able to ELT the FAA data (stored in a public S3 bucket)
export AWS_ACCESS_KEY_ID="<my AWS access key>"
export AWS_SECRET_ACCESS_KEY="<my AWS secret key>"
docker-compose up extract_load_github
docker-compose up extract_load_faa
docker-compose up extract_load_exchangeratehost

# Transform model to be ready for analytics, with dbt
# Also, GoodData models are generated from dbt models and pushed to GoodData  
docker-compose up transform  

# Deliver analytics artefacts(metrics, visualizations, dashboards, ...) into GoodData
docker-compose up analytics
```

Then you can move to Gitlab, forking this repository and run the pipeline against your environments:
- Create a public GoodData instance
    - Go to [GoodData trial](https://www.gooddata.com/trial/) page, enter your e-mail,
        and in few tens of seconds you get your own GoodData instance running in our cloud, managed by us.
- Create a public PostgreSQL or Snowflake instance
  - Personally, I found [bit.io](https://bit.io/) as the only free-forever PostgreSQL offering.
  - Create required databases (for dev/staging/prod).
 
You have to set the following (sensitive) environment variables in the Gitlab(section Settings/CICD):
- TAP_GITHUB_AUTH_TOKEN
- GOODDATA_HOST - host name pointing to the GoodData instance
- GOODDATA_TOKEN - admin token to authenticate against the GoodData instance
- MELTANO_STATE_AWS_ACCESS_KEY_ID/MELTANO_STATE_AWS_SECRET_ACCESS_KEY - Meltano stores its state to AWS S3, and needs these credentials

The rest of environment variables (Github repos to be crawled, DB endpoints, ...) can be configured in [.gitlab-ci.yml](.gitlab-ci.yml)(section `variables`).

## Developer guide

Bootstrap developer environment:
```bash
# Creates virtualenv and installs all dependencies
make dev

# Activate virtualenv
source .venv/bin/activate
# You should see a `(.venv)` appear at the beginning of your terminal prompt indicating that you are working inside the `virtualenv`.

# Deactivate virtual env once you are done
deactivate
```

### Set environment variables
See [.env.local](.env.local) example. Fill in sensitive variables.

### Extract and Load
Meltano tool is used. Configuration file [meltano.yml](data_pipeline/meltano.yml) declares everything related.

How to run:
```bash
make extract_load
```

The output of this stage is `cicd_input_stage` schema in the database.

It is running incrementally, it stores its state into a dedicated schema `meltano`.
You can use `--full-refresh` flag to enforce full refresh of the whole model.

### Data transformation
The folder `data_pipeline/models` contains [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) to transform data from `cicd_input_stage` to `cicd_output_stage` that is used for analytics of data. You can use `--full-refresh` flag to enforce full refresh of the whole model.

How to run:
```bash
make transform
```

### Generate GoodData semantic model from dbt models
Plugin [dbt-gooddata](https://github.com/jaceksan/dbt-gooddata) provides generators of GoodData semantic model objects from dbt models.
In particular, it allows you to generate so called GoodData PDM (Physical Data Model), LDM(Logical Data Model, mapped to PDM), and metrics.
It is based on [GoodData Python SDK](https://github.com/gooddata/gooddata-python-sdk).

How to run:
```bash
make deploy_models
```

## Constraints
We wanted to define database constraints. Why? [GoodData](https://www.gooddata.com/) can join automatically between tables if you have tables that have foreign keys. This is a huge benefit that saves time, and also you can avoid mistakes thanks to that.

We used package [Snowflake-Labs/dbt_constraints](https://github.com/Snowflake-Labs/dbt_constraints) for defining constrains.

Another option is to declare these semantic properties into GoodData-specific `meta` sections in dbt models (it is utilized in this demo).

## Schema names
The dbt autogenerates the schema name but you can easily change it by custom macro - see our [approach how we dealt with schema names](data_transformation/macros/generate_schema_name.sql).

## Generate all columns into schema.yml files
This can help you to bootstrap schema.yaml files programmatically. Then, you can extend them by additional properties.

Example:
```bash
dbt --profiles-dir profile run-operation generate_source \
  --args "{\"schema_name\": \"$INPUT_SCHEMA_GITHUB\", \"generate_columns\": true, \"include_descriptions\": true}"
```

# Analytics
Folder [dbt-gooddata](data_pipeline/dbt-gooddata) contains a PoC of dbt plugin providing tools for loading/storing GoodData analytics model (metrics, insights, dashboards).
It is based on [GoodData Python SDK](https://github.com/gooddata/gooddata-python-sdk).

## Load analytics model to GoodData
Analytics model is stored in [gooddata_layouts](data_pipeline/gooddata_layouts) folder.

The following command reads the layout, and loads it into the GooData instance:
```bash
make deploy_analytics
```

It not only loads the stored layout, but it also reads metrics from dbt models and loads them too.

## Store analytics model
Anytime you can fetch analytics model from the GoodData instance and store it to [gooddata_layouts](data_pipeline/gooddata_layouts) folder.
It makes sense to do some operations by editing stored layout files, but other in GoodData UI applications.
For instance, it is more convenient to build more complex GoodData MAQL metrics in the Metric Editor UI application.
Then, to persist such metrics to [gooddata_layouts](data_pipeline/gooddata_layouts) folder, run the following command:

```bash
make store_analytics
```

## Invalidate analytics cache 

Anytime you update data, e.g. by running `dbt run` command, you have to invalidate GoodData caches to see the new data there.
The following command invalidates these caches:
```bash
make invalidate_analytics_caches
```

### Test analytics

It is possible to test if all insights (visualizations) are possible to execute - it means that you know if insights (visualizations) render correctly.

Use the following command:
```bash
make test_insights
```

## Applications

Applications are stored in [apps](apps/) folder. They are not delivered by the Gitlab pipeline, but by render.com service watching this repo.

### VR demo
[README](apps/vr_analytics/)

### Streamlit demo
[README](apps/streamlit/)

---

If you want to learn more about the stack described in the document, do not hesitate to contact us.

If you find a bug, please [create a merge request](https://gitlab.com/patrikbraborec/gooddata-data-pipeline/-/merge_requests/new), or [create an issue](https://gitlab.com/patrikbraborec/gooddata-data-pipeline/-/issues/new).
