all:
	echo "Nothing here yet."

.PHONY: dbt_compile dev extract_load deploy_models deploy_analytics

# TODO - remove this, do not depend on manifest.json
dbt_compile:
	dbt compile --profiles-dir profile --profile rt_dev --target redshift

dev:
	python3.11 -m venv .venv --upgrade-deps
	.venv/bin/pip3 install -r requirements.txt
	.venv/bin/pip3 install -r requirements-dbt.txt
	.venv/bin/dbt deps --profiles-dir profile
	.venv/bin/pip3 install -r requirements-gooddata.txt

elt_local:
	python generate.py -sf $${SCALE_FACTOR:-1}
	time ./upload_to_minio.sh
	python load.py --duckdb
	dbt run --profiles-dir profile --profile rt_dev_local --target duckdb $$FR
	dbt test --profiles-dir profile --profile rt_dev_local --target duckdb

elt_cloud:
	python generate.py -sf $${SCALE_FACTOR:-1}
	time ./upload_to_s3.sh
	python load.py --redshift
	export DBT_INCREMENTAL_STRATEGY="merge" && dbt run --profiles-dir profile --profile rt_dev --target redshift $$FR
	dbt test --profiles-dir profile --profile rt_dev --target redshift

generate_data:
	python generate.py -sf $${SCALE_FACTOR:-1}

upload_data_local:
	time ./upload_to_minio.sh

upload_data_s3:
	time ./upload_to_s3.sh

load_local:
	python load.py --duckdb

load_cloud:
	python load.py --redshift

transform_local:
	dbt run --profiles-dir profile --profile rt_dev_local --target duckdb $$FR
	dbt test --profiles-dir profile --profile rt_dev_local --target duckdb

transform_cloud:
	dbt run --profiles-dir profile --profile rt_dev --target redshift $$FR
	dbt test --profiles-dir profile --profile rt_dev --target redshift

invalidate_caches:
	# Invalidate GoodData caches after new data are delivered
	gooddata-dbt upload_notification --profile rt_dev --target redshift $$DR

deploy_models: dbt_compile
	# Set DR with --dry-run for testing
	gooddata-dbt $$DR provision_workspaces
	gooddata-dbt $$DR register_data_sources --profile rt_dev --target redshift
	gooddata-dbt $$DR deploy_ldm --profile rt_dev --target redshift

provision_workspaces:
	gooddata-dbt $$DR provision_workspaces

register_data_sources:
	gooddata-dbt $$DR register_data_sources --profile rt_dev --target redshift

deploy_ldm: dbt_compile
	gooddata-dbt $$DR deploy_ldm --profile rt_dev --target redshift

deploy_and_test_analytics:
	gooddata-dbt $$DR deploy_analytics
	gooddata-dbt $$DR test_visualizations

deploy_analytics:
	gooddata-dbt $$DR deploy_analytics

store_analytics:
	gooddata-dbt store_analytics

test_visualizations:
	gooddata-dbt $$DR test_visualizations
