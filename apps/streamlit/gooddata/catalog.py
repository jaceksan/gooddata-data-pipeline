from time import time
from typing import Union, Optional
from logging import Logger
import attr
import streamlit as st
from gooddata_sdk import (
    CatalogMetric, CatalogAttribute, CatalogFact, Insight, CatalogWorkspace,
)
from gooddata_sdk import GoodDataSdk, CatalogWorkspaceContent, ObjId
# TODO - expose this object in sdk.__init.py
from gooddata_sdk.catalog.entity import CatalogEntity, CatalogNameEntity
from app_ext.state import AppState
from gooddata.__init import (
    DEFAULT_EMPTY_SELECT_OPTION_ID, DEFAULT_EMPTY_SELECT_OPTION_TITLE, log_duration, generate_execution_definition,
    get_local_id_metric, SIMPLE_METRIC_AGGREGATION
)

ObjectsWithTitle = list[Union[CatalogEntity, Insight]]
ObjectsWithName = list[Union[CatalogNameEntity, CatalogWorkspace]]
ObjectsAll = Union[ObjectsWithTitle, ObjectsWithName]
ObjectsLdm = list[CatalogEntity]
ObjectsWithOutObjId = list[Union[CatalogNameEntity, Insight, CatalogWorkspace]]

@attr.s(auto_attribs=True, kw_only=True)
class FilteredObjects:
    filtered_facts: list[CatalogFact]
    filtered_metrics: list[CatalogMetric]
    filtered_attributes: list[CatalogAttribute]
    removed_facts: list[CatalogFact] = []
    removed_metrics: list[CatalogMetric] = []
    removed_attributes: list[CatalogAttribute] = []

    @property
    def count_filtered(self):
        return len([
            *self.filtered_facts, *self.filtered_metrics, *self.filtered_attributes,
        ])

    @property
    def count_removed(self):
        return len([
            *self.removed_facts, *self.removed_metrics, *self.removed_attributes,
        ])

    @property
    def count_all(self):
        return self.count_filtered + self.count_removed

    @property
    def report_removed_metrics(self) -> Optional[str]:
        if self.count_removed:
            result = "Removed objects:\n"
            if self.removed_facts:
                result = "- Removed facts:\n"
                for i, fact in enumerate(self.removed_facts):
                    result += f"\t{i+1}. {fact.title}\n"
                return result
            if self.removed_metrics:
                result = "- Removed metrics:\n"
                for i, metric in enumerate(self.removed_metrics):
                    result += f"\t{i+1}. {metric.title}\n"
                return result
            if self.removed_attributes:
                result = "- Removed attributes:\n"
                for i, attribute in enumerate(self.removed_attributes):
                    result += f"\t{i+1}. {attribute.title}\n"
            return result
        else:
            return None

    @property
    def report_removed_attributes(self) -> Optional[str]:
        if self.removed_attributes:
            result = "Removed attributes:\n"
            for i, attribute in enumerate(self.removed_attributes):
                result += f"{i+1}. {attribute.title}\n"
            return result
        else:
            return None

class Catalog:
    def __init__(self, logger: Logger, sdk: GoodDataSdk, workspace_id: str, app_state: AppState) -> None:
        self.logger = logger
        self.sdk = sdk
        self.workspace_id = workspace_id
        self.app_state = app_state
        self.insights = get_insights(self.logger, self.sdk, workspace_id)
        self.filtered_objects = None
        self.set_filtered_objects()


    def set_filtered_objects(self):
        self.filtered_objects = self.filter_catalog_by_existing_context()

    @property
    def all_facts(self) -> list[CatalogFact]:
        return get_facts(self.logger, self.sdk, self.workspace_id)

    @property
    def all_metrics(self) -> list[CatalogMetric]:
        return get_metrics(self.logger, self.sdk, self.workspace_id)

    @property
    def all_attributes(self) -> list[CatalogAttribute]:
        return get_attributes(self.logger, self.sdk, self.workspace_id)

    @property
    def all(self) -> ObjectsLdm:
        return [*self.all_facts, *self.all_metrics, *self.all_attributes]
    
    @property
    def filtered_facts(self) -> list[CatalogFact]:
        return self.filtered_objects.filtered_facts

    @property
    def filtered_metrics(self) -> list[CatalogMetric]:
        return self.filtered_objects.filtered_metrics

    @property
    def filtered_attributes(self) -> list[CatalogAttribute]:
        return self.filtered_objects.filtered_attributes

    @property
    def filtered_all(self) -> ObjectsLdm:
        return [*self.filtered_facts, *self.filtered_metrics, *self.filtered_attributes]

    @staticmethod
    def get_object(objects: ObjectsLdm, obj_id: str) -> Optional[CatalogEntity]:
        return next(iter([x for x in objects if str(x.obj_id) == obj_id]), None)

    @property
    def selected_metrics(self) -> ObjectsLdm:
        result = []
        for selected_metric_id in self.app_state.get("selected_metrics", []):
            filtered_object = self.get_object(self.filtered_all, selected_metric_id)
            if filtered_object:
                result.append(filtered_object)
        return result

    @property
    def selected_view_by(self) -> ObjectsLdm:
        result = []
        for selected_attribute_id in self.app_state.get("selected_view_by", []):
            filtered_object = self.get_object(self.filtered_attributes, selected_attribute_id)
            if filtered_object:
                result.append(filtered_object)
        return result

    @property
    def selected_segmented_by(self) -> CatalogEntity:
        result = []
        for selected_attribute_id in self.app_state.get("selected_segmented_by", []):
            filtered_object = self.get_object(self.filtered_attributes, selected_attribute_id)
            if filtered_object:
                result.append(filtered_object)
        return next(iter(result), None)

    @property
    def selected_filter_attributes(self) -> list[CatalogAttribute]:
        selected_filter_attributes_obj_ids = self.app_state.get('selected_filter_attributes', [])
        return [x for x in self.filtered_attributes if str(x.obj_id) in selected_filter_attributes_obj_ids]

    @property
    def selected_sort_by(self) -> ObjectsLdm:
        # We must keep the order here!
        result = []
        for selected_obj_id in self.app_state.get("selected_sort_by", []):
            selected_object = next(iter([x for x in self.filtered_all if str(x.obj_id) == selected_obj_id]))
            result.append(selected_object)
        return result

    @property
    def selected_sort_columns(self) -> tuple[list[str], list[bool]]:
        selected_desc = self.app_state.selected_sort_by_desc()
        sort_columns = []
        ascending = []
        for ldm_object in self.selected_sort_by:
            # Attribute can be as metric (COUNT) or as view_by/segment_by
            # Column name is generated differently for these cases
            if ldm_object.obj_id in [x.obj_id for x in self.selected_metrics]:
                metric_func = self.selected_metrics_with_functions[str(ldm_object.obj_id)]
                sort_columns.append(metric_column_name(ldm_object, metric_func))
            else:
                sort_columns.append(ldm_object.title)
            ascending.append(not selected_desc[str(ldm_object.obj_id)])
        return sort_columns, ascending

    @property
    def selected_all(self) -> ObjectsLdm:
        result = [*self.selected_metrics, *self.selected_view_by]
        if self.selected_segmented_by:
            result.append(self.selected_segmented_by)
        return result

    @property
    def selected_metrics_with_functions(self) -> dict[str, str]:
        return self.app_state.selected_metric_ids_with_functions()

    def get_date_attributes(self, attributes: Optional[list[CatalogAttribute]] = None) -> Optional[list[CatalogAttribute]]:
        return [a for a in (attributes or self.all_attributes) if isinstance(a, CatalogAttribute) and a.granularity]

    def get_standard_attributes(self, attributes: Optional[list[CatalogAttribute]] = None) -> Optional[list[CatalogAttribute]]:
        return [
            a for a in (attributes or self.all_attributes) if not a.granularity
        ]

    def filter_catalog_by_existing_context(self) -> FilteredObjects:
        selected_attributes = self.app_state.selected_attribute_ids()
        selected_filter_values = self.app_state.selected_filter_attribute_values()
        if self.selected_metrics_with_functions or selected_attributes:
            filtered_objects = compute_valid_catalog_objects(
                self.logger, self.sdk, self.workspace_id,
                self.selected_metrics_with_functions,
                selected_attributes,
                selected_filter_values,
            )

            # TODO - Fix BUG in backend - it returns internal .timestamp attributes
            filtered_attribute_ids = [a for a in filtered_objects.get("attribute", []) if not a.endswith(".timestamp")]
            filtered_fact_ids = filtered_objects.get("fact", [])
            filtered_metric_ids = filtered_objects.get("metric", [])
            filtered_facts = [x for x in self.all_facts if x.id in filtered_fact_ids]
            filtered_metrics = [x for x in self.all_metrics if x.id in filtered_metric_ids]
            filtered_attributes = [x for x in self.all_attributes if x.id in filtered_attribute_ids]
            removed_facts = [x for x in self.all_facts if x.id not in filtered_fact_ids]
            removed_metrics = [x for x in self.all_metrics if x.id not in filtered_metric_ids]
            removed_attributes = [x for x in self.all_attributes if x.id not in filtered_attribute_ids]
            result = FilteredObjects(
                filtered_facts=filtered_facts, filtered_metrics=filtered_metrics, filtered_attributes=filtered_attributes,
                removed_facts=removed_facts, removed_metrics=removed_metrics, removed_attributes=removed_attributes,
            )
            self.logger.debug(f"Catalog - filtered {result.count_filtered}/{result.count_all}")
            return result
        else:
            self.logger.debug(f"Catalog - nothing filtered")
            return FilteredObjects(
                filtered_facts=self.all_facts, filtered_metrics=self.all_metrics, filtered_attributes=self.all_attributes,
            )

    def get_insight(self, insight_id: str) -> Optional[Insight]:
        return next(iter([x for x in self.insights if x.id == insight_id]), None)
    def insight_metrics(
        self, insight_id: str
    ) -> tuple[ObjectsLdm, dict[str, str]]:
        insight = self.get_insight(insight_id)
        if insight:
            result_metrics = []
            result_metrics_funcs = {}
            for i, metric in enumerate(insight.metrics):
                metric_id = metric.item["identifier"]["id"]
                metric_type = metric.item["identifier"]["type"]
                obj_id = ObjId(metric_id, metric_type)
                result_metrics.append(next(iter([x for x in self.all if x.obj_id == obj_id])))
                # TODO - expose it to InsightMetric object
                measure_def = metric._metric.get("measureDefinition")
                if measure_def:
                    func = metric._metric["measureDefinition"].get("aggregation")
                    if func and func.upper() in SIMPLE_METRIC_AGGREGATION:
                        result_metrics_funcs[str(obj_id)] = func.upper()
                    elif func:
                        if metric_type == "attribute":
                            result_metrics_funcs[str(obj_id)] = "COUNT"
                        else:
                            result_metrics_funcs[str(obj_id)] = "SUM"
            return result_metrics, result_metrics_funcs

    def insight_attributes(self, insight_id: str) -> list[CatalogAttribute]:
        insight = self.get_insight(insight_id)
        if insight:
            insight_attributes = [ObjId(x.label_id, "attribute") for x in insight.attributes]
            return [x for x in self.all_attributes if x.obj_id in insight_attributes]
        return []


# Below are methods annotated by st.cache_data. They cannot be a part of a class yet (not yet supported by Streamlit)

@st.cache_data
def get_workspaces(_logger: Logger, _sdk: GoodDataSdk) -> list[CatalogWorkspace]:
    start = time()
    result = _sdk.catalog_workspace.list_workspaces()
    log_duration(_logger, "get_workspaces", start)
    return result

@st.cache_data
def get_full_catalog(_logger: Logger, _sdk: GoodDataSdk, workspace_id: str) -> CatalogWorkspaceContent:
    # TODO - extend entities returned by this method and use only this method (instead of get_attributes, ...)
    start = time()
    result = _sdk.catalog_workspace_content.get_full_catalog(workspace_id)
    #valid_objects = result.catalog_with_valid_objects()
    log_duration(_logger, "get_full_catalog", start)
    return result

@st.cache_data
def get_attributes(_logger: Logger, _sdk: GoodDataSdk, workspace_id: str) -> list[CatalogAttribute]:
    start = time()
    result = _sdk.catalog_workspace_content.get_attributes_catalog(workspace_id)
    log_duration(_logger, "get_attributes", start)
    return result

@st.cache_data
def get_facts(_logger: Logger, _sdk: GoodDataSdk, workspace_id: str) -> list[CatalogFact]:
    start = time()
    result = _sdk.catalog_workspace_content.get_facts_catalog(workspace_id)
    log_duration(_logger, "get_facts", start)
    return result

@st.cache_data
def get_metrics(_logger: Logger, _sdk: GoodDataSdk, workspace_id: str) -> list[CatalogMetric]:
    start = time()
    result = _sdk.catalog_workspace_content.get_metrics_catalog(workspace_id)
    log_duration(_logger, "get_metrics", start)
    return result

@st.cache_data
def compute_valid_catalog_objects(
    _logger: Logger, _sdk: GoodDataSdk, workspace_id: str,
    metrics_with_func: dict[str, str],
    attribute_ids: list[str],
    filter_values: dict[str, list[str]] = None,
) -> dict[str, set[str]]:
    exec_def = generate_execution_definition(metrics_with_func, attribute_ids, filter_values)
    result = _sdk.catalog_workspace_content.compute_valid_objects(workspace_id, exec_def)
    return result


@st.cache_data
def get_insights(_logger: Logger, _sdk: GoodDataSdk, workspace_id: str) -> list[Insight]:
    start = time()
    result = _sdk.insights.get_insights(workspace_id)
    log_duration(_logger, "get_insights", start)
    return result

@st.cache_data
def get_data_source_id(_logger: Logger, _sdk: GoodDataSdk, workspace_id: str) -> str:
    start = time()
    ldm = _sdk.catalog_workspace_content.get_declarative_ldm(workspace_id)
    # DS_ID is defined in each dataset, but GoodData does not support multiple different data sources in a single workspace
    data_source_id = [d.data_source_table_id.data_source_id for d in ldm.ldm.datasets if d.data_source_table_id.data_source_id][0]
    log_duration(_logger, "get_data_source_id", start)
    return data_source_id

def get_ids(objects: ObjectsWithOutObjId) -> list[str]:
    return [str(o.id) for o in objects]

def get_object_ids(objects: list[CatalogEntity]) -> list[str]:
    return [str(o.obj_id) for o in objects]

def get_title_for_id(objects: list[Insight], object_id: str) -> str:
    if object_id == DEFAULT_EMPTY_SELECT_OPTION_ID:
        return DEFAULT_EMPTY_SELECT_OPTION_TITLE
    for g in objects:
        if g.id == object_id:
            return g.title

def get_title_for_obj_id(objects: ObjectsWithTitle, object_id: str, title_obj_type: bool = False) -> str:
    if object_id == DEFAULT_EMPTY_SELECT_OPTION_ID:
        return DEFAULT_EMPTY_SELECT_OPTION_TITLE
    for g in objects:
        if str(g.obj_id) == object_id:
            if title_obj_type:
                return g.title + f" ({g.type})"
            else:
                return g.title

def get_name_for_id(objects: ObjectsWithName, object_id: str) -> str:
    if object_id == DEFAULT_EMPTY_SELECT_OPTION_ID:
        return DEFAULT_EMPTY_SELECT_OPTION_TITLE
    for g in objects:
        if g.id == object_id:
            return g.name

def ids_with_default(objects: ObjectsWithOutObjId) -> list[str]:
    return [DEFAULT_EMPTY_SELECT_OPTION_ID] + [str(x.id) for x in objects]

def obj_ids_with_default(objects: ObjectsAll) -> list[str]:
    return [DEFAULT_EMPTY_SELECT_OPTION_ID] + [str(x.obj_id) for x in objects]

def metric_column_name(ldm_object: CatalogEntity, metric_func: str) -> str:
    if ldm_object.type in ["fact", "attribute"]:
        return get_local_id_metric(str(ldm_object.obj_id), metric_func)
    else:
        return ldm_object.title
