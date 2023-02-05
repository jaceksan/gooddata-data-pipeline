all:
	echo "Nothing here yet."

.PHONY: dev
dev:
	# Create virtualenv
	python3.10 -m venv .venv --upgrade-deps
	# Install Meltano and required plugins
	.venv/bin/pip3 install -r src/requirements-meltano.txt
	.venv/bin/meltano --cwd src install
	# Install dbt and required plugins
	.venv/bin/pip3 install -r src/requirements-dbt.txt
	.venv/bin/dbt deps --project-dir src
	# Install dbt-gooddata PoC plugin
	cd src/dbt-gooddata && ../../.venv/bin/python3 setup.py install
