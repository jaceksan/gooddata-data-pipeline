import json
from typing import Optional
import attrs

from dbt_gooddata.dbt.base import Base, DATE_GRANULARITIES, TIMESTAMP_GRANULARITIES, GoodDataLdmTypes


@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelMetaGoodDataTableProps(Base):
    model_id: Optional[str] = None


@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelMetaGoodDataColumnProps(Base):
    ldm_type: Optional[str] = None
    referenced_table: Optional[str] = None
    referenced_column_name: Optional[str] = None
    label_type: Optional[str] = None
    attribute_column: Optional[str] = None


@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelMetaGoodDataTable(Base):
    gooddata: Optional[DbtModelMetaGoodDataTableProps] = None


@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelMetaGoodDataColumn(Base):
    gooddata: Optional[DbtModelMetaGoodDataColumnProps] = None


@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelBase(Base):
    name: str
    description: str
    tags: list[str]


@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelColumn(DbtModelBase):
    data_type: Optional[str]
    meta: DbtModelMetaGoodDataColumn


@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelTable(DbtModelBase):
    schema: str
    columns: dict[str, DbtModelColumn]
    meta: DbtModelMetaGoodDataTable


class DbtModelTables:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        with open("target/manifest.json") as fp:
            self.dbt_catalog = json.load(fp)

    @property
    def tables(self) -> list[DbtModelTable]:
        result = []
        for model_name, model_def in self.dbt_catalog["nodes"].items():
            result.append(DbtModelTable.from_dict(model_def))
        # Return only gooddata labelled tables marked by model_id (if requested in args)
        return [
            r for r in result
            if r.meta.gooddata is not None and (not self.model_id or r.meta.gooddata.model_id == self.model_id)
        ]

    @property
    def schema_name(self):
        schemas = set([t.schema for t in self.tables if t.schema])
        if len(schemas) != 1:
            raise Exception("Unsupported feature: GoodData does not support multiple schemas.")
        else:
            return next(iter(schemas))

    def make_pdm(self):
        result = {"tables": []}
        for table in self.tables:
            columns = []
            for column in table.columns.values():
                columns.append({
                    "name": column.name,
                    "data_type": column.data_type
                })
            result["tables"].append({
                "id": table.name,
                "path": [table.schema, table.name],
                "type": "TABLE",
                "columns": columns,
            })
        return result

    @staticmethod
    def make_grain(table: DbtModelTable) -> list[dict]:
        grain = []
        for column in table.columns.values():
            if column.meta.gooddata.ldm_type == GoodDataLdmTypes.PRIMARY_KEY.value:
                grain.append({"id": column.name, "type": "attribute"})
        return grain

    @staticmethod
    def make_references(table: DbtModelTable) -> list[dict]:
        references = []
        for column in table.columns.values():
            referenced_object_id = None
            if column.meta.gooddata.ldm_type == GoodDataLdmTypes.REFERENCE.value:
                referenced_object_id = column.meta.gooddata.referenced_table
            elif column.meta.gooddata.ldm_type == GoodDataLdmTypes.DATE.value:
                referenced_object_id = column.name
            if referenced_object_id is not None:
                references.append({
                    "identifier": {"id": referenced_object_id, "type": "dataset"},
                    "multivalue": False,
                    "source_columns": [column.name]
                })
        return references

    @staticmethod
    def make_facts(table: DbtModelTable) -> list[dict]:
        facts = []
        for column in table.columns.values():
            if column.meta.gooddata.ldm_type == GoodDataLdmTypes.FACT.value:
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
    def make_labels(table: DbtModelTable, attribute_column: DbtModelColumn) -> list[dict]:
        labels = []
        for column in table.columns.values():
            if column.meta.gooddata.ldm_type == GoodDataLdmTypes.LABEL.value \
                    and attribute_column.name == column.meta.gooddata.attribute_column:
                labels.append({
                    "id": column.name,
                    # TODO - all titles filled from dbt descriptions, incorrect! No title in dbt models.
                    "title": column.description,
                    "description": column.description,
                    "source_column": column.name,
                    "value_type": column.meta.gooddata.label_type,
                    "tags": [table.description] + column.tags,
                })
        return labels

    def make_attributes(self, table: DbtModelTable) -> list[dict]:
        attributes = []
        for column in table.columns.values():
            if column.meta.gooddata.ldm_type in [GoodDataLdmTypes.ATTRIBUTE.value, GoodDataLdmTypes.PRIMARY_KEY.value]:
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
    def make_date_datasets(table: DbtModelTable, existing_date_datasets: list[dict]) -> list[dict]:
        date_datasets = []
        for column in table.columns.values():
            existing_dataset_ids = [d["id"] for d in existing_date_datasets]
            if column.meta.gooddata.ldm_type == "date" and column.name not in existing_dataset_ids:
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
