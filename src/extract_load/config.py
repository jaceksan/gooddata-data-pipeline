from pathlib import Path
from typing import Optional

import attr
import cattr
import yaml

OUTPUT_FOLDER = "/tmp"
CSV_FILE_PATH_TMPL_ORG = OUTPUT_FOLDER + "/{org_name}_{table_name}.csv"
CSV_FILE_PATH_TMPL_REPO = OUTPUT_FOLDER + "/{org_name}_{repo_name}_{table_name}.csv"
DEFAULT_DATE_FROM = "2020-01-01T00:00:00"


@attr.s(auto_attribs=True, kw_only=True)
class Table:
    name: str
    endpoint: str
    date_col: Optional[str] = None
    custom_params: dict = attr.field(factory=dict)
    org_level: Optional[bool] = None


@attr.s(auto_attribs=True, kw_only=True)
class Organization:
    name: str
    repos: list[str] = attr.field(factory=list)


class Config:
    def __init__(self, config_file: str):
        self.config_file = Path(config_file)

    @property
    def config(self):
        with open(Path(self.config_file)) as fp:
            return yaml.safe_load(fp)

    @property
    def tables(self) -> list[Table]:
        return cattr.structure(self.config['tables'], list[Table])

    @property
    def organizations(self) -> list[Organization]:
        return cattr.structure(self.config['organizations'], list[Organization])
