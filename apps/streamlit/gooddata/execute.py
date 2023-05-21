from time import time
from datetime import date
from typing import Union
import streamlit as st
import pandas as pd
from logging import Logger
from gooddata_sdk import (
    ObjId, CatalogMetric, CatalogAttribute, Insight, CatalogWorkspace,
    AbsoluteDateFilter,
)
import gooddata_pandas as gp
from gooddata_sdk import GoodDataSdk
from gooddata.__init import log_duration, generate_execution_definition
from gooddata.catalog import get_data_source_id

ValidObjectTypes = Union[list[CatalogMetric], list[CatalogAttribute], list[Insight], list[CatalogWorkspace]]

@st.cache_data
def execute_stored_insight(_logger: Logger, _frames: gp.DataFrameFactory, insight_id: str) -> pd.DataFrame:
    start = time()
    result = _frames.for_insight(insight_id, auto_index=False)
    log_duration(_logger, f"execute_stored_insight {insight_id=}", start)
    return result

@st.cache_data
def get_attribute_values(_sdk: GoodDataSdk, workspace_id: str, attribute_id: str) -> list[str]:
    return _sdk.catalog_workspace_content.get_label_elements(workspace_id, attribute_id)

@st.cache_data
def execute_custom_insight(
    _logger: Logger,
    _frames: gp.DataFrameFactory,
    metrics_with_func: dict[str, str],
    attribute_ids: list[str],
    filter_values: dict[str, list[str]] = None
) -> pd.DataFrame:
    start = time()
    execution_definition = generate_execution_definition(
        metrics_with_func,
        attribute_ids,
        filter_values
    )
    df, df_metadata = _frames.for_exec_def(exec_def=execution_definition, page_size=10000)
    df_from_result_id, df_metadata_from_result_id = _frames.for_exec_result_id(
        result_id=df_metadata.execution_response.result_id,
    )
    df_from_result_id.columns = df_from_result_id.columns.map(''.join)
    log_duration(_logger, f"execute_custom_insight", start)
    return df_from_result_id

def datetime_to_str(date_obj: date) -> str:
    return date_obj.strftime("%Y-%m-%d")

def create_absolute_date_filter(date_attribute: str, dates: tuple) -> AbsoluteDateFilter:
    dataset_name = date_attribute.split(".")[0]
    return AbsoluteDateFilter(
        ObjId(id=dataset_name, type="dataset"),
        datetime_to_str(dates[0]),
        datetime_to_str(dates[1])
    )

def invalidate_gd_caches(logger: Logger, sdk: GoodDataSdk, workspace_id: str) -> None:
    ds_id = get_data_source_id(logger, sdk, workspace_id)
    sdk.catalog_data_source.register_upload_notification(ds_id)
