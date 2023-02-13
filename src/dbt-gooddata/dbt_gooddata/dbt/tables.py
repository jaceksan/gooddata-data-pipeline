import copy
import json
from pathlib import Path
from typing import Optional
import attrs

from dbt_gooddata.dbt.base import (
    Base, DATE_GRANULARITIES, TIMESTAMP_GRANULARITIES, GoodDataLdmTypes,
    TIMESTAMP_DATA_TYPES, DATETIME_DATA_TYPES, DBT_PATH_TO_MANIFEST
)
from gooddata_sdk import CatalogDeclarativeTables, CatalogDeclarativeTable, CatalogDeclarativeColumn


@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelMetaGoodDataTableProps(Base):
    model_id: Optional[str] = None


@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelMetaGoodDataColumnProps(Base):
    ldm_type: Optional[str] = None
    referenced_table: Optional[str] = None
    label_type: Optional[str] = None
    attribute_column: Optional[str] = None

    @property
    def gooddata_ref_table_ldm_id(self) -> Optional[str]:
        if self.referenced_table:
            return self.referenced_table.lower()

    def upper_case_names(self):
        if self.referenced_table:
            self.referenced_table = self.referenced_table.upper()
        if self.attribute_column:
            self.attribute_column = self.attribute_column.upper()


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
    # If 2+ references point to the same table, the table plays multiple roles,
    # it must be generated as multiple datasets
    role_name: Optional[str] = None

    # Title is not supported by dbt, we fill it here
    @property
    def title(self) -> str:
        return self.description or self.name.lower()

    @property
    def gooddata_ldm_id(self) -> str:
        if self.role_name:
            return f"{self.name.lower()}_{self.role_name.lower()}"
        else:
            return self.name.lower()

    @property
    def gooddata_ldm_title(self) -> str:
        if self.role_name:
            return f"{self.title} ({self.role_name.lower()})"
        else:
            return self.title

    @property
    def gooddata_ldm_description(self) -> str:
        if self.role_name and self.description:
            return f"{self.description} ({self.role_name.lower()})"
        else:
            return self.description

    def upper_case_name(self):
        self.name = self.name.upper()


@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelColumn(DbtModelBase):
    data_type: Optional[str]
    meta: Optional[DbtModelMetaGoodDataColumn] = None

    def has_gooddata_metadata(self) -> bool:
        return self.meta is not None and self.meta.gooddata is not None

    def gooddata_is_fact(self) -> bool:
        return self.has_gooddata_metadata() and self.meta.gooddata.ldm_type == GoodDataLdmTypes.FACT.value

    def gooddata_is_attribute(self) -> bool:
        valid_ldm_types = [GoodDataLdmTypes.ATTRIBUTE.value, GoodDataLdmTypes.PRIMARY_KEY.value]
        # Without GD metadata, attribute is default unless it is DATETIME data type
        return (not self.has_gooddata_metadata() and not self.is_date()) \
            or (self.has_gooddata_metadata() and self.meta.gooddata.ldm_type in valid_ldm_types)

    def gooddata_is_label(self, attribute_column_name: str) -> bool:
        return self.has_gooddata_metadata() \
            and self.meta.gooddata.ldm_type == GoodDataLdmTypes.LABEL.value \
            and attribute_column_name == self.meta.gooddata.attribute_column

    def is_date(self) -> bool:
        gooddata_date = self.has_gooddata_metadata() and self.meta.gooddata.ldm_type == "date"
        return gooddata_date or self.data_type.upper() in DATETIME_DATA_TYPES

    def is_reference(self) -> bool:
        return self.has_gooddata_metadata() and self.meta.gooddata.ldm_type == GoodDataLdmTypes.REFERENCE.value

@attrs.define(auto_attribs=True, kw_only=True)
class DbtModelTable(DbtModelBase):
    schema: str
    columns: dict[str, DbtModelColumn]
    meta: DbtModelMetaGoodDataTable

    def has_gooddata_metadata(self) -> bool:
        return self.meta is not None and self.meta.gooddata is not None


class DbtModelTables:
    def __init__(self, model_ids: list[str], upper_case: bool, scan_pdm: CatalogDeclarativeTables) -> None:
        self.model_ids = model_ids
        self.upper_case = upper_case
        self.scan_pdm = scan_pdm
        with open(DBT_PATH_TO_MANIFEST) as fp:
            self.dbt_catalog = json.load(fp)

    @property
    def tables(self) -> list[DbtModelTable]:
        tables = []
        for model_name, model_def in self.dbt_catalog["nodes"].items():
            tables.append(DbtModelTable.from_dict(model_def))

        for table in tables:
            scan_table = self.get_scan_table(table.name)
            if self.upper_case:
                table.upper_case_name()
            for column in table.columns.values():
                # dbt does not provide data types in manifest.json
                # get it from GoodData scan API
                scan_column = self.get_scan_column(scan_table, column.name)
                column.data_type = scan_column.data_type
                if self.upper_case:
                    column.upper_case_name()
                    if column.has_gooddata_metadata():
                        column.meta.gooddata.upper_case_names()

        # Return only gooddata labelled tables.
        # Optionally marked by model_id
        result = [
            t for t in tables
            if t.has_gooddata_metadata() and (len(self.model_ids) == 0 or t.meta.gooddata.model_id in self.model_ids)
        ]
        if len(result) == 0:
            raise Exception(f"No tables found in the data source model_ids={self.model_ids}")
        else:
            return result

    @property
    def schema_name(self):
        schemas = set([t.schema for t in self.tables if t.schema])
        if len(schemas) > 1:
            raise Exception(f"Unsupported feature: GoodData does not support multiple schemas - {schemas=}")
        elif len(schemas) < 1:
            raise Exception(f"No schema found")
        else:
            schema_name = next(iter(schemas))
            if self.upper_case:
                return schema_name.upper()
            else:
                return schema_name

    def get_scan_table(self, table_name: str) -> CatalogDeclarativeTable:
        for table in self.scan_pdm.tables:
            if table.id.lower() == table_name.lower():
                return table
        # Scan can find more tables being a part of ELT, which we do not want to use for analytics.
        # Such tables are skipped because we do not prepare schema.yml for them.

    @staticmethod
    def get_scan_column(table: CatalogDeclarativeTable, column_name: str) -> CatalogDeclarativeColumn:
        for column in table.columns:
            if column.name.lower() == column_name.lower():
                return column
        raise Exception(f"get_scan_column table={table.id} column={column_name} not found in scan")

    def make_pdm(self):
        result = {"tables": []}
        for table in self.tables:
            scan_table = self.get_scan_table(table.name)
            columns = []
            for column in table.columns.values():
                # dbt does not propagate data types to manifest (not yet?)
                scan_column = self.get_scan_column(scan_table, column.name)
                column.data_type = column.data_type or scan_column.data_type

                columns.append({
                    "name": column.name,
                    "data_type": column.data_type
                })
            result["tables"].append({
                "id": table.name,
                "path": [self.schema_name, table.name],
                "type": "TABLE",
                "columns": columns,
            })
        return result

    @staticmethod
    def get_ldm_title(column: DbtModelColumn) -> str:
        return column.description or column.name

    @staticmethod
    def is_primary_key(column: DbtModelColumn) -> bool:
        result = False
        # TODO - constraints are stored in special nodes
        # for test in column.tests:
        #     if DbtTests.PRIMARY_KEY.value in test:
        #         result = True
        if column.has_gooddata_metadata() and column.meta.gooddata.ldm_type == GoodDataLdmTypes.PRIMARY_KEY.value:
            result = True
        return result

    def make_grain(self, table: DbtModelTable) -> list[dict]:
        grain = []
        for column in table.columns.values():
            if self.is_primary_key(column):
                grain.append({"id": column.gooddata_ldm_id, "type": "attribute"})
        return grain

    # TODO - constraints are stored in special nodes
    # @staticmethod
    # def get_dbt_foreign_key(column: DbtModelColumn) -> Optional[str]:
    #     referenced_object_id = None
    #     if column.meta.gooddata.ldm_type == GoodDataLdmTypes.REFERENCE.value:
    #         referenced_object_id = column.meta.gooddata.gooddata_ref_table_ldm_id
    #     else:
    #         for test in column.tests:
    #             if DbtTests.FOREIGN_KEY.value in test:
    #                 referenced_object_id = test[DbtTests.FOREIGN_KEY.value][DbtTests.FOREIGN_KEY_REF.value]
    #     return referenced_object_id

    @staticmethod
    def find_role_playing_tables(tables: list[DbtModelTable]) -> dict:
        result = {}
        for table in tables:
            references = {}
            for column in table.columns.values():
                if column.is_reference():
                    referenced_table = column.meta.gooddata.referenced_table
                    if referenced_table in references:
                        references[referenced_table].append(column.name)
                    else:
                        references[referenced_table] = [column.name]
            for referenced_object_id, columns in references.items():
                if len(columns) > 1:
                    result[referenced_object_id] = columns
        return result

    def make_references(self, table: DbtModelTable, role_playing_tables: dict) -> list[dict]:
        references = []
        for column in table.columns.values():
            referenced_object_id = None
            if column.is_reference():
                referenced_object_id = column.meta.gooddata.gooddata_ref_table_ldm_id
                referenced_object_name = referenced_object_id
                if self.upper_case:
                    referenced_object_name = referenced_object_name.upper()
                if referenced_object_name in role_playing_tables:
                    referenced_object_id = f"{referenced_object_id}_{column.gooddata_ldm_id}"
            elif column.is_date():
                referenced_object_id = column.gooddata_ldm_id
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
            if column.gooddata_is_fact():
                facts.append({
                    "id": column.gooddata_ldm_id,
                    # TODO - all titles filled from dbt descriptions, incorrect! No title in dbt models.
                    "title": column.gooddata_ldm_title,
                    "description": column.gooddata_ldm_description,
                    "source_column": column.name,
                    "tags": [table.description] + column.tags,
                })
        return facts

    @staticmethod
    def make_labels(table: DbtModelTable, attribute_column: DbtModelColumn) -> list[dict]:
        labels = []
        for column in table.columns.values():
            if column.gooddata_is_label(attribute_column.name):
                labels.append({
                    "id": column.gooddata_ldm_id,
                    "title": column.gooddata_ldm_title,
                    "description": column.gooddata_ldm_description,
                    "source_column": column.name,
                    "value_type": column.meta.gooddata.label_type,
                    "tags": [table.description] + column.tags,
                })
        return labels

    def make_attributes(self, table: DbtModelTable) -> list[dict]:
        attributes = []
        for column in table.columns.values():
            # Default is attribute
            if column.gooddata_is_attribute():
                attributes.append({
                    "id": column.gooddata_ldm_id,
                    "title": column.gooddata_ldm_title,
                    "description": column.gooddata_ldm_description,
                    "source_column": column.name,
                    "tags": [table.description] + column.tags,
                    "labels": self.make_labels(table, column)
                })
        return attributes

    def make_date_datasets(self, table: DbtModelTable, existing_date_datasets: list[dict]) -> list[dict]:
        date_datasets = []
        for column in table.columns.values():
            existing_dataset_ids = [d["id"] for d in existing_date_datasets]
            if column.is_date() and column.gooddata_ldm_id not in existing_dataset_ids:
                if column.data_type in TIMESTAMP_DATA_TYPES:
                    granularities = DATE_GRANULARITIES + TIMESTAMP_GRANULARITIES
                else:
                    granularities = DATE_GRANULARITIES
                date_datasets.append({
                    "id": column.gooddata_ldm_id,
                    "title": self.get_ldm_title(column),
                    "description": column.description,
                    "tags": [table.description] + column.tags,
                    "granularities": granularities,
                    "granularities_formatting": {
                        "title_base": "",
                        "title_pattern": "%titleBase - %granularityTitle"
                    },
                })
        return date_datasets

    def make_dataset(self, data_source_id: str, table: DbtModelTable, role_playing_tables: dict, result: dict) -> dict:
        grain = self.make_grain(table)
        references = self.make_references(table, role_playing_tables)
        facts = self.make_facts(table)
        attributes = self.make_attributes(table)

        result["datasets"].append({
            "id": table.gooddata_ldm_id,
            "title": table.gooddata_ldm_title,
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

    @staticmethod
    def populate_role_playing_tables(tables: list[DbtModelTable], role_playing_tables: dict) -> list[DbtModelTable]:
        result = []
        for table in tables:
            if table.name in role_playing_tables:
                for role_column in role_playing_tables[table.name]:
                    new_table = copy.deepcopy(table)
                    new_table.role_name = role_column
                    for column in new_table.columns.values():
                        column.role_name = role_column
                    result.append(new_table)
            else:
                result.append(table)
        return result

    def make_declarative_datasets(self, data_source_id: str, model_id: Optional[str]) -> dict:
        result = {"datasets": [], "date_instances": []}
        model_tables = [t for t in self.tables if model_id is None or model_id == t.meta.gooddata.model_id]
        role_playing_tables = self.find_role_playing_tables(model_tables)
        model_tables_with_roles = self.populate_role_playing_tables(model_tables, role_playing_tables)

        for table in model_tables_with_roles:
            result = self.make_dataset(data_source_id, table, role_playing_tables, result)
        # print(result)
        return result

    def get_entity_type(self, table_name: str, column_name: str) -> Optional[str]:
        comp_table_name = table_name
        if self.upper_case:
            comp_table_name = table_name.upper()
        comp_column_name = column_name
        if self.upper_case:
            comp_column_name = column_name.upper()
        for table in self.tables:
            if table.name == comp_table_name:
                for column in table.columns.values():
                    if column.name == comp_column_name:
                        return column.meta.gooddata.ldm_type
