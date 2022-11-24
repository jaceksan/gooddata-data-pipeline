import os
from pathlib import Path
from typing import Any, Optional

import attr
import cattr
import yaml
from gooddata_sdk import GoodDataSdk


@attr.s(auto_attribs=True, kw_only=True)
class Workspace:
    id: str
    name: str
    data_source_id: str


@attr.s(auto_attribs=True, kw_only=True)
class DataSource:
    id: str
    name: str
    db_name: str


class Config:
    def __init__(self, config_file: str):
        self.config_file = Path(config_file)

    @property
    def config(self) -> dict[str, Any]:
        with open(Path(self.config_file)) as fp:
            return yaml.safe_load(fp)

    @property
    def workspaces(self) -> list[Workspace]:
        return cattr.structure(self.config['workspaces'], list[Workspace])

    @property
    def data_sources(self) -> list[DataSource]:
        return cattr.structure(self.config['data_sources'], list[DataSource])

    @property
    def layout_data_source_id(self) -> str:
        return self.config['layout_data_source_id']

    @property
    def layout_workspace_folder_name(self) -> str:
        return self.config['layout_workspace_folder_name']

    def get_workspace(self, workspace_id: str) -> Workspace:
        for workspace in self.workspaces:
            if workspace.id == workspace_id:
                return workspace
        raise Exception(f"Workspace {workspace_id} not found in the config.yaml file")

    def get_data_source(self, data_source_id: str) -> DataSource:
        for data_source in self.data_sources:
            if data_source.id == data_source_id:
                return data_source
        raise Exception(f"Data source {data_source_id} not found in the config.yaml file")


class GoodDataSdkWrapper:
    def __init__(self, timeout=600):
        kwargs = {}
        if self.override_host:
            kwargs["Host"] = self.override_host
        self.sdk = GoodDataSdk.create(host_=self.host, token_=self.token, **kwargs)
        self.wait_for_gooddata_is_up(timeout)

    @property
    def host(self) -> str:
        return os.getenv("GOODDATA_HOST", "localhost")

    @property
    def token(self) -> str:
        return os.getenv("GOODDATA_TOKEN", "YWRtaW46Ym9vdHN0cmFwOmFkbWluMTIz")

    @property
    def override_host(self) -> Optional[str]:
        return os.getenv("OVERRIDE_HOST")

    def wait_for_gooddata_is_up(self, timeout) -> None:
        # Wait for the GoodData.CN docker image to start up
        print(f"Waiting for {self.host} to be up.", flush=True)
        self.sdk.support.wait_till_available(timeout=timeout)
        print(f"Host {self.host} is up.", flush=True)

    def pre_cache_insights(self, workspaces: list = None) -> None:
        if not workspaces:
            workspaces = [w.id for w in self.sdk.catalog_workspace.list_workspaces()]
        for workspace_id in workspaces:
            insights = self.sdk.insights.get_insights(workspace_id)

            for insight in insights:
                self.sdk.tables.for_insight(workspace_id, insight)
