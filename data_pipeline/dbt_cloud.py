import json
import logging
import os
from pathlib import Path
from typing import Any, List
import time

import attrs

import requests
import yaml
from cattrs import structure
from requests import Response

_CURRENT_DIR = Path(__file__).parent
_PROFILES_FILE = _CURRENT_DIR / "profile" / "profiles.yml"
_URL_BASE_V2 = "https://cloud.getdbt.com/api/v2"
_URL_BASE_V3 = "https://cloud.getdbt.com/api/v3"

_ACCOUNT_ID = os.environ['DBT_ACCOUNT_ID']
_JOB_ID = os.environ['DBT_JOB_ID']
_PROJECT_ID = os.environ['DBT_PROJECT_ID']


@attrs.define
class Environment:
    name: str
    environment_name: str
    environment_id: str = attrs.field(init=False,
                                      default=os.environ["ELT_ENVIRONMENT"])
    title: str = attrs.field(init=False, default="")
    type: str
    account: str
    database: str
    warehouse: str
    schema: str

    user: str = attrs.field(init=False, default=os.environ.get("DBT_SNOWFLAKE_USER", "cicd"))
    password: str = attrs.field(init=False, default=os.environ["DBT_SNOWFLAKE_PASS"])

    def __attrs_post_init__(self):
        if "DBT_ENVIRONMENT_TITLE" in os.environ:
            self.title = os.environ["DBT_ENVIRONMENT_TITLE"]
        else:
            self.title = f"{self.name} dbt Cloud {self.environment_name}"

    @classmethod
    def from_dict(cls, data: dict):
        return structure(data, cls)

    def to_dict(self) -> dict:
        return attrs.asdict(self)

    def to_profile(self) -> dict:
        required = ["title", "type", "account", "user", "password", "database", "warehouse", "schema"]
        environment_dict = self.to_dict()
        return {r: environment_dict[r] for r in required}


def call_get_dbt_endpoint(url: str) -> Response:
    response = requests.get(url, headers={"Authorization": f"Bearer {os.environ['DBT_TOKEN']}"})
    if response.status_code != 200:
        raise ValueError(
            f"Response code {response.status_code} was returned. With the following message {response.text}.")
    return response


def get_logger(name: str, debug: bool = False) -> logging.Logger:
    level = logging.INFO if not debug else logging.DEBUG
    logging.basicConfig(level=level, format="%(levelname)-8s: %(name)s : %(asctime)-15s - %(message)s")
    logging.basicConfig(level=level)
    logger = logging.getLogger(name)
    return logger


def safeget(var: Any, path: List[str]) -> Any:
    if len(path) == 0:
        return var
    elif not isinstance(var, dict):
        return None
    else:
        key = path[0]
        if key in var:
            return safeget(var[key], path[1:])
        else:
            return None


def is_fetch_done(response: dict) -> bool:
    in_progress = safeget(response, ["data", "in_progress"])
    return not in_progress


def was_fetch_success(response: dict) -> bool:
    is_complete = safeget(response, ["data", "is_complete"])
    is_success = safeget(response, ["data", "is_success"])
    return is_complete and is_success


def fetch_run_result(run_id: str,
                     timeout: float = 120.0,
                     retry: float = 0.2,
                     max_retry: float = 5.0, ) -> None:
    logger = get_logger("fetch_run_result")
    time_sum = 0
    url = f"{_URL_BASE_V2}/accounts/{_ACCOUNT_ID}/runs/{run_id}"
    while True:
        response = call_get_dbt_endpoint(url)
        result = response.json()
        if is_fetch_done(result) and time_sum <= timeout:
            break
        time.sleep(retry)
        time_sum += retry
        retry = min(retry * 2, max_retry)
    if not was_fetch_success(result):
        raise ValueError(f"Job with {run_id=} failed.")
    if time_sum >= timeout:
        raise ValueError(f"Job with {run_id=} timed out. The time out was {timeout}.")
    logger.info(f"Job with {run_id=} completed successfully.")


def download_artifact(run_id: str,
                      identifier: str,
                      path: str | Path):
    """
    :param run_id: Identifier of the run.
    :param identifier: E.g., manifest.json
    :param path: Path where to store file.
    """
    logger = get_logger("download_artifact")
    url = f"{_URL_BASE_V2}/accounts/{_ACCOUNT_ID}/runs/{run_id}/artifacts/{identifier}"
    response = call_get_dbt_endpoint(url)
    result = response.json()
    os.makedirs(path)
    with open(path / identifier, "w") as f:
        json.dump(result, f)
    logger.info(f"Artifact {identifier} download successfully and stored in {path}")


def download_manifest(run_id: str, path: str | Path) -> None:
    download_artifact(run_id, "manifest.json", path)


def run_job():
    logger = get_logger("run_job")
    url = f"{_URL_BASE_V2}/accounts/{_ACCOUNT_ID}/jobs/{_JOB_ID}/run/"
    data = {"cause": "Triggered via API"}
    response = requests.post(url, headers={"Authorization": f"Bearer {os.environ['DBT_TOKEN']}"}, data=data)
    if response.status_code != 200:
        raise ValueError(
            f"Response code {response.status_code} was returned. With the following message {response.text}.")
    result = response.json()
    run_id = safeget(result, ["data", "id"])
    run_href = safeget(result, ["data", "href"])
    if run_id is None:
        raise ValueError("Could not find wanted content.")
    logger.info(f"Job with {run_id=} started. Link to job run {run_href}")
    return run_id


def read_env_vars() -> dict:
    logger = get_logger("read_env_vars")
    url = f"{_URL_BASE_V3}/accounts/{_ACCOUNT_ID}/projects/{_PROJECT_ID}/environment-variables/job/?job_definition_id={_JOB_ID}"
    response = call_get_dbt_endpoint(url)
    result = response.json()
    data = result["data"]
    env_vars = {}
    for k, v in data.items():
        env_vars[k] = safeget(v, ["project", "value"])
    logger.info(f"Environment variables from job_definition_id={_JOB_ID} loaded.")
    return env_vars


def get_environment_id() -> str:
    logger = get_logger("get_environment_id")
    url = f"{_URL_BASE_V2}/accounts/{_ACCOUNT_ID}/jobs/{_JOB_ID}/"
    response = call_get_dbt_endpoint(url)
    result = response.json()
    environment_id = safeget(result, ["data", "environment_id"])
    logger.info(f"Found environment with {environment_id=} for job_id={_JOB_ID}.")
    return environment_id


def read_environment(environment_id: str) -> Environment:
    logger = get_logger("read_environment")
    url = f"{_URL_BASE_V2}/accounts/{_ACCOUNT_ID}/environments/{environment_id}"
    response = call_get_dbt_endpoint(url)
    result = response.json()
    connection = safeget(result, ["data", "connection"])
    env_vars = read_env_vars()
    environment_dict = connection | {"environment_name": safeget(result, ["data", "name"]), "schema": env_vars["DBT_OUTPUT_SCHEMA"]}
    environment = Environment.from_dict(environment_dict)
    logger.info(f"Environment with {environment_id=} loaded.")
    return environment


def make_profiles(environment: Environment) -> None:
    with open(_PROFILES_FILE, "r") as f:
        data = yaml.safe_load(f)
    data["default"]["outputs"] = {environment.environment_id: environment.to_profile()}
    with open(_PROFILES_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, encoding="utf-8")


def run_workflow():
    run_id = run_job()
    fetch_run_result(run_id)
    download_manifest(run_id, _CURRENT_DIR / "target")
    environment_id = get_environment_id()
    environment = read_environment(environment_id=environment_id)
    make_profiles(environment)


if __name__ == "__main__":
    run_workflow()
