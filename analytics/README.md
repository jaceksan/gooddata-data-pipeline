# Scripts

## Getting Started

### Set up Python virtual environment

Create virtual environment:

```bash
$ virtualenv venv
```

Activate virtual environment:

```bash
$ source venv/bin/activate
```

You should see a `(venv)` appear at the beginning of your terminal prompt indicating that you are working inside the `virtualenv`.

To leave virtual environment run:

```bash
$ deactivate
```

### Install all packages

```bash
$ pip install -r requirements.txt
```

### Set env variables

export GOODDATA_HOST=https://cicd.anywhere.gooddata.com
export GOODDATA_TOKEN=<gooddata-api-token>
export STAGING_WORKSPACE_ID=staging
export PRODUCTION_WORKSPACE_ID=production
export GOODDATA_DATA_SOURCE_ID="cicd"
