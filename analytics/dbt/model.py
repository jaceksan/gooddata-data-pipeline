import json
from typing import Optional


META_GOODDATA_KEY = "gooddata"
DATE_GRANULARITIES = [
    "DAY",
    "WEEK",
    "MONTH",
    "QUARTER",
    "YEAR",
    "DAY_OF_WEEK",
    "DAY_OF_MONTH",
    "DAY_OF_YEAR",
    "WEEK_OF_YEAR",
    "MONTH_OF_YEAR",
    "QUARTER_OF_YEAR",
]
TIMESTAMP_GRANULARITIES = [
    "MINUTE",
    "HOUR",
    "MINUTE_OF_HOUR",
    "HOUR_OF_DAY",
]


class DbtBase:
    def __init__(self, model_def: dict) -> None:
        self.model_def = model_def

    @property
    def name(self) -> str:
        return self.model_def["name"]

    @property
    def description(self) -> str:
        return self.model_def["description"]

    @property
    def tags(self) -> list[str]:
        return self.model_def["tags"]

    @property
    def meta(self) -> dict:
        return self.model_def["meta"]

    @property
    def gooddata(self) -> Optional[dict]:
        return self.meta.get(META_GOODDATA_KEY)

    def get_if_gooddata(self, property_name: str):
        if self.gooddata is not None:
            return self.gooddata.get(property_name)
        return None


class DbtColumn(DbtBase):
    @property
    def data_type(self) -> str:
        return self.model_def["data_type"]

    @property
    def ldm_type(self) -> Optional[str]:
        return self.get_if_gooddata("ldm_type")

    @property
    def referenced_table(self) -> Optional[str]:
        return self.get_if_gooddata("referenced_table")

    @property
    def referenced_column_name(self) -> Optional[str]:
        return self.get_if_gooddata("referenced_column_name")

    @property
    def label_type(self) -> Optional[str]:
        return self.get_if_gooddata("label_type")

    @property
    def attribute_column(self) -> Optional[str]:
        return self.get_if_gooddata("attribute_column")


class DbtTable(DbtBase):
    @property
    def schema(self) -> str:
        return self.model_def["schema"]

    @property
    def columns(self) -> list[DbtColumn]:
        return [DbtColumn(c) for c in self.model_def['columns'].values()]

    @property
    def model_id(self) -> Optional[str]:
        return self.get_if_gooddata("model_id")


class DbtTables:
    def __init__(self):
        with open("../data_transformation/target/manifest.json") as fp:
            self.dbt_catalog = json.load(fp)

    @property
    def tables(self) -> list[DbtTable]:
        result = []
        for model_name, model_def in self.dbt_catalog["nodes"].items():
            result.append(DbtTable(model_def))
        # Return only gooddata labelled tables
        # TODO - enable other filters by args (e.g. meta.model_id, list of dbt models, tags, ...)
        return [r for r in result if r.gooddata is not None]

    def make_pdm(self):
        result = {"tables": []}
        for table in self.tables:
            columns = []
            for column in table.columns:
                columns.append({
                    "name": column.name,
                    "data_type": column.data_type
                })
            result["tables"].append({
                "id": table.name,  # TODO - may not be unique
                "path": [table.schema, table.name],
                "type": "TABLE",
                "columns": columns,
            })
        return result

    @staticmethod
    def make_grain(table: DbtTable) -> list[dict]:
        grain = []
        for column in table.columns:
            if column.ldm_type == "primary_key":
                grain.append({"id": column.name, "type": "attribute"})
        return grain

    @staticmethod
    def make_references(table: DbtTable) -> list[dict]:
        references = []
        for column in table.columns:
            referenced_object_id = None
            if column.ldm_type == "reference":
                referenced_object_id = column.referenced_table
            elif column.ldm_type == "date":
                referenced_object_id = column.name
            if referenced_object_id is not None:
                references.append({
                    "identifier": {"id": referenced_object_id, "type": "dataset"},
                    "multivalue": False,
                    "source_columns": [column.name]
                })
        return references

    @staticmethod
    def make_facts(table: DbtTable) -> list[dict]:
        facts = []
        for column in table.columns:
            if column.ldm_type == "fact":
                facts.append({
                    "id": column.name,
                    # TODO - all titles filled from dbt descriptions, incorrect! No title in dbt models.
                    "title": column.description,
                    "description": column.description,
                    "source_column": column.name,
                    "tags": [table.description] + column.tags,
                })
        return facts

    @staticmethod
    def make_labels(table: DbtTable, attribute_column: DbtColumn) -> list[dict]:
        labels = []
        for column in table.columns:
            if column.ldm_type == "label" and attribute_column.name == column.attribute_column:
                labels.append({
                    "id": column.name,
                    # TODO - all titles filled from dbt descriptions, incorrect! No title in dbt models.
                    "title": column.description,
                    "description": column.description,
                    "source_column": column.name,
                    "value_type": column.label_type,
                    "tags": [table.description] + column.tags,
                })
        return labels

    def make_attributes(self, table: DbtTable) -> list[dict]:
        attributes = []
        for column in table.columns:
            if column.ldm_type in ["attribute", "primary_key"]:
                attributes.append({
                    "id": column.name,
                    # TODO - all titles filled from dbt descriptions, incorrect! No title in dbt models.
                    "title": column.description,
                    "description": column.description,
                    "source_column": column.name,
                    "tags": [table.description] + column.tags,
                    "labels": self.make_labels(table, column)
                })
        return attributes

    @staticmethod
    def make_date_datasets(table: DbtTable, existing_date_datasets: list[dict]) -> list[dict]:
        date_datasets = []
        for column in table.columns:
            existing_dataset_ids = [d["id"] for d in existing_date_datasets]
            if column.ldm_type == "date" and column.name not in existing_dataset_ids:
                if column.data_type in ["TIMESTAMP", "TIMESTAMPTZ"]:
                    granularities = DATE_GRANULARITIES + TIMESTAMP_GRANULARITIES
                else:
                    granularities = DATE_GRANULARITIES
                date_datasets.append({
                    "id": column.name,
                    "title": column.description,
                    "description": column.description,
                    "tags": [table.description] + column.tags,
                    "granularities": granularities,
                    "granularities_formatting": {
                        "title_base": "",
                        "title_pattern": "%titleBase - %granularityTitle"
                    },
                })
        return date_datasets

    def make_declarative_datasets(self, data_source_id: str) -> dict:
        result = {"datasets": [], "date_instances": []}
        for table in self.tables:
            grain = self.make_grain(table)
            references = self.make_references(table)
            facts = self.make_facts(table)
            attributes = self.make_attributes(table)

            result["datasets"].append({
                "id": table.name,
                "title": table.description,
                "description": table.description,
                "tags": [table.description] + table.tags,
                "data_source_table_id": {
                    "data_source_id": data_source_id,
                    "id": table.name,  # TODO - may not be unique
                    "type": "dataSource"
                },
                "grain": grain,
                "references": references,
                "facts": facts,
                "attributes": attributes,
            })

            date_datasets = self.make_date_datasets(table, result["date_instances"])
            result["date_instances"] = result["date_instances"] + date_datasets

        return result
