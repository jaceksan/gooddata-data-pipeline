from time import time
from logging import Logger
import re
from typing import Optional

from gooddata_sdk import (
    ExecutionDefinition, Attribute, SimpleMetric, ObjId,
    PositiveAttributeFilter, NegativeAttributeFilter
)

DEFAULT_EMPTY_SELECT_OPTION_ID = "xxxxxxxxxxxxxxxxx"
DEFAULT_EMPTY_SELECT_OPTION_TITLE = '<select>'

SIMPLE_METRIC_AGGREGATION = [
    "SUM",
    "AVG",
    "COUNT",
    "APPROXIMATE_COUNT",
    "MAX",
    "MEDIAN",
    "MIN",
    "RUNSUM",
]


def duration(start: float) -> int:
    return int((time() - start) * 1000)

def log_duration(logger: Logger, method_name: str, start: float) -> None:
    logger.info(f"{method_name} duration={duration(start)}")


def get_local_id_metric(object_id: str, metric_func: Optional[str]) -> str:
    re_local_id = re.compile(r'[^a-z0-9]', re.I)
    base = re_local_id.sub('_', object_id)
    if metric_func:
        return f"{metric_func}_{base}"
    else:
        return base

def get_local_id_attribute(object_id: str) -> str:
    re_local_id = re.compile(r'[^a-z0-9]', re.I)
    return "a_" + re_local_id.sub('_', object_id)

def get_obj_id_from_str(obj_id: str) -> ObjId:
    parts = obj_id.split("/")
    return ObjId(id=parts[1], type=parts[0])

def generate_metrics_for_exec_def(metrics_with_func: dict[str, str]) -> list[SimpleMetric]:
    result = []
    if isinstance(metrics_with_func, dict):
        for metric_id, metric_func in metrics_with_func.items():
            kwargs = {
                "item": get_obj_id_from_str(metric_id),
                "local_id": get_local_id_metric(metric_id, metric_func),
            }
            if metric_func:
                kwargs["aggregation"] = metric_func
            result.append(SimpleMetric(**kwargs))
    return result

def generate_attributes(attribute_ids: list[str]) -> list[Attribute]:
    return [
        Attribute(label=get_obj_id_from_str(a), local_id=get_local_id_attribute(a))
        for a in attribute_ids
    ]

def generate_filters(filter_values: dict[str, list[str]] = None) -> list[PositiveAttributeFilter | NegativeAttributeFilter]:
    # TODO - NegativeAttributeFilter
    filters = []
    if filter_values:
        for a_id, a_values in filter_values.items():
            # Backend expects label, not attribute
            # TODO - add full support for attribute labels
            label_id = get_obj_id_from_str(a_id).id
            kwargs = {"label": ObjId(label_id, "label"), "values": a_values}
            filters.append(PositiveAttributeFilter(**kwargs))
    return filters

def generate_execution_definition(
    metrics_with_func: dict[str, str],
    attribute_ids: list[str],
    filter_values: dict[str, list[str]] = None
):
    attributes = generate_attributes(attribute_ids)
    dim = [get_local_id_attribute(a) for a in attribute_ids]
    metrics = generate_metrics_for_exec_def(metrics_with_func)
    filters = generate_filters(filter_values)

    if metrics:
        dimensions = [dim, ["measureGroup"]]
    else:
        dimensions = [dim]
    result = ExecutionDefinition(
        attributes=attributes,
        metrics=metrics,
        filters=filters,
        dimensions=dimensions,
    )
    return result
