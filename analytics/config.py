from pathlib import Path

import attr
import yaml


@attr.s(auto_attribs=True, kw_only=True)
class Workspace:
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
                )
            )
        return workspaces

    def get_workspace(self, workspace_id: str) -> Workspace:
        for workspace in self.workspaces:
            if workspace.id == workspace_id:
                return workspace
        raise Exception(f"Workspace {workspace_id} not found in the config.yaml file")
