SRC_DATA_PIPELINE = "data_pipeline"

all:
	echo "Nothing here yet."

.PHONY: dbt_gooddata dbt_compile dev extract_load deploy_models analytics

# Install dbt-gooddata PoC plugin
dbt_gooddata:
	cd $(SRC_DATA_PIPELINE)/dbt-gooddata && python3 setup.py install

# TODO - remove this, do not depend on manifest.json
dbt_compile:
	cd $(SRC_DATA_PIPELINE) && dbt compile --profiles-dir profile --target $$ELT_ENVIRONMENT

dev:
	# Create virtualenv
	python3.10 -m venv .venv --upgrade-deps
	# Install Meltano and required plugins
	.venv/bin/pip3 install -r $(SRC_DATA_PIPELINE)/requirements-meltano.txt
	.venv/bin/meltano --cwd $(SRC_DATA_PIPELINE) install
	# Install dbt and required plugins
	.venv/bin/pip3 install -r $(SRC_DATA_PIPELINE)/requirements-dbt.txt
	.venv/bin/dbt deps --project-dir $(SRC_DATA_PIPELINE)
	cd $(SRC_DATA_PIPELINE)/dbt-gooddata && ../../.venv/bin/python3 setup.py install


extract_load:
	cd $(SRC_DATA_PIPELINE) && meltano --environment $$ELT_ENVIRONMENT run tap-github-repo $$MELTANO_TARGET tap-github-org $$MELTANO_TARGET

transform:
	cd $(SRC_DATA_PIPELINE) && dbt run --profiles-dir profile --target $$ELT_ENVIRONMENT
	cd $(SRC_DATA_PIPELINE) && dbt test --profiles-dir profile --target $$ELT_ENVIRONMENT
	# Invalidate GoodData caches after new data are delivered
	cd $(SRC_DATA_PIPELINE) && dbt-gooddata upload_notification

deploy_models: dbt_gooddata dbt_compile
	cd $(SRC_DATA_PIPELINE) && dbt-gooddata deploy_models $$GOODDATA_UPPER_CASE

deploy_analytics: dbt_gooddata dbt_compile
	cd $(SRC_DATA_PIPELINE) && dbt-gooddata deploy_analytics $$GOODDATA_UPPER_CASE
	cd $(SRC_DATA_PIPELINE) && dbt-gooddata test_insights

store_analytics: dbt_gooddata
	cd $(SRC_DATA_PIPELINE) && dbt-gooddata store_analytics

test_insights: dbt_gooddata
	cd $(SRC_DATA_PIPELINE) && dbt-gooddata test_insights

invalidate_analytics_caches: dbt_gooddata
	cd $(SRC_DATA_PIPELINE) && dbt-gooddata upload_notification
