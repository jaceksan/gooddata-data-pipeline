from pathlib import Path

import attr
import yaml


@attr.s(auto_attribs=True, kw_only=True)
class Workspace:
    id: str
    name: str
    data_source_id: str


@attr.s(auto_attribs=True, kw_only=True)
class DataSource:
    id: str
    name: str


class Config:
    def __init__(self, config_file: str):
        self.config_file = Path(config_file)

    @property
    def config(self):
        with open(Path(self.config_file)) as fp:
            return yaml.safe_load(fp)

    @property
    def workspaces(self) -> list[Workspace]:
        workspaces = []
        for workspace in self.config['workspaces']:
            workspaces.append(
                Workspace(
                    id=workspace['id'],
                    name=workspace['name'],
                    data_source_id=workspace['data_source_id']
                )
            )
        return workspaces

    @property
    def data_sources(self) -> list[DataSource]:
        data_sources = []
        for data_source in self.config['data_sources']:
            data_sources.append(
                DataSource(
                    id=data_source['id'],
                    name=data_source['name'],
                )
            )
        return data_sources

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
