from time import time
from typing import Union, Optional, Set
from logging import Logger
import attr
import streamlit as st
from gooddata_sdk import (
    CatalogMetric, CatalogAttribute, CatalogLabel, CatalogFact, Insight, CatalogWorkspace,
    GoodDataSdk, CatalogWorkspaceContent, ObjId, AttrCatalogEntity,
)
from app_ext.state import AppState
from gooddata.__init import (
    DEFAULT_EMPTY_SELECT_OPTION_ID, DEFAULT_EMPTY_SELECT_OPTION_TITLE, log_duration, generate_execution_definition,
    get_local_id_metric, SIMPLE_METRIC_AGGREGATION
)

ObjectsWithTitle = list[Union[AttrCatalogEntity, Insight]]
ObjectsWithName = list[Union[CatalogWorkspace]]
ObjectsAll = Union[ObjectsWithTitle, ObjectsWithName]
ObjectsLdm = list[AttrCatalogEntity]
ObjectsWithOutObjId = list[Union[Insight, CatalogWorkspace]]

@attr.s(auto_attribs=True)
class FilteredObjects:
    filtered_facts: list[CatalogFact]
    filtered_metrics: list[CatalogMetric]
    filtered_attributes: list[CatalogAttribute]
    all_facts: list[CatalogFact] = []
    all_metrics: list[CatalogMetric] = []
    all_attributes: list[CatalogAttribute] = []

    @property
    def filtered_all(self):
        return [*self.all_facts, *self.all_metrics, *self.all_attributes]

    @property
    def removed_facts(self) -> list[CatalogFact]:
        return [f for f in self.all_facts if f.id not in [ff.id for ff in self.filtered_facts]]

    @property
    def removed_metrics(self) -> list[CatalogMetric]:
        return [f for f in self.all_metrics if f.id not in [fm.id for fm in self.filtered_metrics]]

    @property
    def removed_attributes(self) -> list[CatalogAttribute]:
        return [f for f in self.all_attributes if f.id not in [fa.id for fa in self.filtered_attributes]]

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
        self.insights = get_insights(logger, sdk, workspace_id)
        self.full_catalog = get_full_catalog(logger, sdk, workspace_id)

    @property
    def all_objects(self) -> ObjectsLdm:
        return [*self.full_catalog.attributes, *self.full_catalog.facts, *self.full_catalog.metrics]

    @property
    def filtered_objects(self) -> FilteredObjects:
        return FilteredObjects(
            self.filtered_catalog.facts, self.filtered_catalog.metrics, self.filtered_catalog.attributes,
            self.full_catalog.facts, self.full_catalog.metrics, self.full_catalog.attributes
        )

    @property
    def filtered_catalog(self) -> CatalogWorkspaceContent:
        if self.app_state.selected_first_metric_with_function() or self.app_state.selected_attribute_ids():
            valid_objects = compute_valid_objects(
                self.logger, self.sdk, self.workspace_id,
                self.app_state.selected_first_metric_with_function(),
                self.app_state.selected_attribute_ids(),
                self.app_state.selected_filter_attribute_values(),
            )
            new_datasets, new_metrics = self.full_catalog.filter_by_valid_objects(valid_objects)
            return CatalogWorkspaceContent(None, new_datasets, new_metrics)
        else:
            return self.full_catalog

    @staticmethod
    def get_object(objects: ObjectsLdm, obj_id: str) -> Optional[AttrCatalogEntity]:
        return next(iter([x for x in objects if str(x.obj_id) == obj_id]), None)

    @property
    def selected_metrics(self) -> ObjectsLdm:
        result = []
        for selected_metric_id in self.app_state.get("selected_metrics", []):
            filtered_object = self.get_object(self.all_objects, selected_metric_id)
            if filtered_object:
                result.append(filtered_object)
        return result

    @property
    def selected_view_by(self) -> list[CatalogAttribute]:
        result = []
        for selected_attribute_id in self.app_state.get("selected_view_by", []):
            result.append(self.get_object(self.full_catalog.attributes, selected_attribute_id))
        return result

    @property
    def selected_view_by_first(self):
        return next(iter(self.selected_view_by), None)
    @property
    def selected_view_by_geo_labels(self) -> Optional[list[CatalogLabel]]:
        if self.selected_view_by_first:
            return [l for l in self.selected_view_by_first.labels if l.value_type in ["GEO_LATITUDE", "GEO_LONGITUDE"]]
        return None

    @property
    def selected_segmented_by(self) -> AttrCatalogEntity:
        selected_attribute_id = self.app_state.get("selected_segmented_by")
        return self.get_object(self.all_objects, selected_attribute_id)

    @property
    def selected_filter_attributes(self) -> list[AttrCatalogEntity]:
        selected_filter_attributes_obj_ids = self.app_state.get('selected_filter_attributes', [])
        return [x for x in self.all_objects if str(x.obj_id) in selected_filter_attributes_obj_ids]

    @property
    def selected_all(self) -> list[AttrCatalogEntity]:
        # Used by sort_by, it is possible to sort by any column
        return [x for x in self.all_objects if str(x.obj_id) in self.app_state.selected_catalog_all()]

    @property
    def selected_sort_by(self) -> ObjectsLdm:
        # We must keep the order here!
        result = []
        for selected_obj_id in self.app_state.get("selected_sort_by", []):
            selected_object = next(iter([x for x in self.all_objects if str(x.obj_id) == selected_obj_id]))
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
                metric_func = self.app_state.selected_metric_ids_with_functions()[str(ldm_object.obj_id)]
                sort_columns.append(metric_column_name(ldm_object, metric_func))
            else:
                sort_columns.append(ldm_object.title)
            ascending.append(not selected_desc[str(ldm_object.obj_id)])
        return sort_columns, ascending

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
                metric_id = metric.item_id
                metric_type = metric.item_type
                obj_id = ObjId(metric_id, metric_type)
                result_metrics.append(next(iter([x for x in self.all_objects if x.obj_id == obj_id])))
                func = metric.aggregation
                if func and func.upper() in SIMPLE_METRIC_AGGREGATION:
                    result_metrics_funcs[str(obj_id)] = func.upper()
                elif func:
                    if metric_type == "attribute":
                        result_metrics_funcs[str(obj_id)] = "COUNT"
                    else:
                        result_metrics_funcs[str(obj_id)] = "SUM"
            return result_metrics, result_metrics_funcs

    def insight_attributes(self, insight_id: str) -> list[AttrCatalogEntity]:
        insight = self.get_insight(insight_id)
        if insight:
            insight_attributes = [ObjId(x.label_id, "attribute") for x in insight.attributes]
            return [x for x in self.all_objects if x.obj_id in insight_attributes]
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
    start = time()
    # Valid Objects function cannot be injected to the result container,
    # it can't be pickled, it can't be cached by Streamlit
    result = _sdk.catalog_workspace_content.get_full_catalog(workspace_id, inject_valid_objects_func=False)
    log_duration(_logger, "get_full_catalog", start)
    return result

@st.cache_data
def compute_valid_objects(
    _logger: Logger, _sdk: GoodDataSdk, workspace_id: str,
    metrics_with_func: dict[str, str],
    attribute_ids: list[str],
    filter_values: dict[str, list[str]] = None,
) -> dict[str, Set[str]]:
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

def get_object_ids(objects: list[AttrCatalogEntity]) -> list[str]:
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

def metric_column_name(ldm_object: AttrCatalogEntity, metric_func: str) -> str:
    if ldm_object.type in ["fact", "attribute"]:
        return get_local_id_metric(str(ldm_object.obj_id), metric_func)
    else:
        return ldm_object.title
