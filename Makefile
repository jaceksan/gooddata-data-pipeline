SRC_DATA_PIPELINE = "data_pipeline"

all:
	echo "Nothing here yet."

.PHONY: dbt_compile dev extract_load deploy_models deploy_analytics

# TODO - remove this, do not depend on manifest.json
dbt_compile:
	cd $(SRC_DATA_PIPELINE) && dbt compile --profiles-dir profile --profile $$ELT_ENVIRONMENT --target $$DBT_TARGET

dev:
	# Create virtualenv
	python3.10 -m venv .venv_el --upgrade-deps
	# Install Meltano and required plugins
	.venv_el/bin/pip3 install -r $(SRC_DATA_PIPELINE)/requirements-meltano.txt
	.venv_el/bin/meltano --cwd $(SRC_DATA_PIPELINE) install
	# dbt must be installed to separate venv, there are conflicts with what Meltano needs
	python3.10 -m venv .venv_t --upgrade-deps
	# Install dbt and required plugins
	.venv_t/bin/pip3 install -r $(SRC_DATA_PIPELINE)/requirements-dbt.txt
	.venv_t/bin/dbt deps --project-dir $(SRC_DATA_PIPELINE)
	# Install dbt-gooddata plugin and related dependencies
	.venv_t/bin/pip3 install -r $(SRC_DATA_PIPELINE)/requirements-gooddata.txt

extract_load:
	cd $(SRC_DATA_PIPELINE) && export TARGET_SCHEMA=$$INPUT_SCHEMA_GITHUB && meltano --environment $$ELT_ENVIRONMENT run tap-github-repo $$MELTANO_TARGET tap-github-org $$MELTANO_TARGET $$FR
	cd $(SRC_DATA_PIPELINE) && export TARGET_SCHEMA=$$INPUT_SCHEMA_FAA && meltano --environment $$ELT_ENVIRONMENT run tap-s3-csv-faa $$MELTANO_TARGET $$FR
	cd $(SRC_DATA_PIPELINE) && export TARGET_SCHEMA=$$INPUT_SCHEMA_ECOMMERCE_DEMO && meltano --environment $$ELT_ENVIRONMENT run tap-s3-csv-ecommerce-demo $$MELTANO_TARGET $$FR
	cd $(SRC_DATA_PIPELINE) && export TARGET_SCHEMA=$$INPUT_SCHEMA_DATA_SCIENCE && meltano --environment $$ELT_ENVIRONMENT run tap-s3-csv-data-science $$MELTANO_TARGET $$FR
# TODO - uncomment once https://github.com/anelendata/tap-exchangeratehost/issues/3 is fixed
#	cd $(SRC_DATA_PIPELINE) && export TARGET_SCHEMA=$$INPUT_SCHEMA_EXCHANGERATEHOST && meltano --environment $$ELT_ENVIRONMENT run tap-exchangeratehost $$MELTANO_TARGET $$FR

extract_load_github:
	cd $(SRC_DATA_PIPELINE) && export TARGET_SCHEMA=$$INPUT_SCHEMA_GITHUB && meltano --environment $$ELT_ENVIRONMENT run tap-github-repo $$MELTANO_TARGET tap-github-org $$MELTANO_TARGET $$FR

extract_load_faa:
	cd $(SRC_DATA_PIPELINE) && export TARGET_SCHEMA=$$INPUT_SCHEMA_FAA && meltano --environment $$ELT_ENVIRONMENT run tap-s3-csv-faa $$MELTANO_TARGET $$FR

extract_load_ecommerce_demo:
	cd $(SRC_DATA_PIPELINE) && export TARGET_SCHEMA=$$INPUT_SCHEMA_ECOMMERCE_DEMO && meltano --environment $$ELT_ENVIRONMENT run tap-s3-csv-ecommerce-demo $$MELTANO_TARGET $$FR

extract_load_data_science:
	cd $(SRC_DATA_PIPELINE) && export TARGET_SCHEMA=$$INPUT_SCHEMA_DATA_SCIENCE && meltano --environment $$ELT_ENVIRONMENT run tap-s3-csv-data-science $$MELTANO_TARGET $$FR

# TODO - uncomment once https://github.com/anelendata/tap-exchangeratehost/issues/3 is fixed
#extract_load_exchange:
#	cd $(SRC_DATA_PIPELINE) && export TARGET_SCHEMA=$$INPUT_SCHEMA_EXCHANGERATEHOST && meltano --environment $$ELT_ENVIRONMENT run tap-exchangeratehost $$MELTANO_TARGET $$FR

transform:
	cd $(SRC_DATA_PIPELINE) && dbt run --profiles-dir profile --profile $$ELT_ENVIRONMENT --target $$DBT_TARGET $$FR
	cd $(SRC_DATA_PIPELINE) && dbt test --profiles-dir profile --profile $$ELT_ENVIRONMENT --target $$DBT_TARGET

transform_cloud:
	cd $(SRC_DATA_PIPELINE) && gooddata-dbt dbt_cloud_run --profiles-dir profile_cloud --profile $$ELT_ENVIRONMENT --target $$DBT_TARGET $$GOODDATA_UPPER_CASE

transform_cloud_stats:
	cd $(SRC_DATA_PIPELINE) && gooddata-dbt dbt_cloud_stats --profiles-dir profile_cloud --profile $$ELT_ENVIRONMENT --target $$DBT_TARGET $$GOODDATA_UPPER_CASE --environment-id $$DBT_ENVIRONMENT_ID

invalidate_caches:
	# Invalidate GoodData caches after new data are delivered
	cd $(SRC_DATA_PIPELINE) && gooddata-dbt upload_notification --profile $$ELT_ENVIRONMENT --target $$DBT_TARGET

deploy_models: dbt_compile
	cd $(SRC_DATA_PIPELINE) && gooddata-dbt deploy_models --profile $$ELT_ENVIRONMENT --target $$DBT_TARGET $$GOODDATA_UPPER_CASE

deploy_models_cloud:
	cd $(SRC_DATA_PIPELINE) && gooddata-dbt deploy_models --profiles-dir profile_cloud --profile $$ELT_ENVIRONMENT --target $$DBT_TARGET $$GOODDATA_UPPER_CASE

deploy_analytics: dbt_compile
	cd $(SRC_DATA_PIPELINE) && gooddata-dbt deploy_analytics $$GOODDATA_UPPER_CASE
	cd $(SRC_DATA_PIPELINE) && gooddata-dbt test_insights

store_analytics:
	cd $(SRC_DATA_PIPELINE) && gooddata-dbt store_analytics

test_insights:
	cd $(SRC_DATA_PIPELINE) && gooddata-dbt test_insights
