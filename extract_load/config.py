from pathlib import Path

import attr
import yaml


OUTPUT_FOLDER = "/tmp"
CSV_FILE_PATH_TMPL = OUTPUT_FOLDER + "/{table_name}.csv"
DEFAULT_DATE_FROM = "2021-01-01T00:00:00"


@attr.s(auto_attribs=True, kw_only=True)
class Table:
    name: str
    endpoint: str
    date_col: str = None
    custom_params: dict = {}


@attr.s(auto_attribs=True, kw_only=True)
class Organization:
    name: str
    repos: list[str]


class Config:
    def __init__(self, config_file: str):
        self.config_file = Path(config_file)

    @property
    def config(self):
        with open(Path(self.config_file)) as fp:
            return yaml.safe_load(fp)

    @property
    def tables(self) -> list[Table]:
        tables = []
        for table in self.config['tables']:
            tables.append(
                Table(
                    name=table['name'],
                    endpoint=table['endpoint'],
                    date_col=table.get('date_col'),
                    custom_params=table.get('custom_params'),
                )
            )
        return tables

    @property
    def organizations(self) -> list[Organization]:
        orgs = []
        for org in self.config['organizations']:
            orgs.append(Organization(name=org['name'], repos=org['repos']))
        return orgs

