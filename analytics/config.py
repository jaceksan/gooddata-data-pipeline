import os
from pathlib import Path
from typing import Any

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
    sdk: GoodDataSdk = GoodDataSdk.create(host_=os.environ["GOODDATA_HOST"], token_=os.environ["GOODDATA_TOKEN"])
