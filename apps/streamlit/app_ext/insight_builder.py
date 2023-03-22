from logging import Logger
import pandas as pd
import streamlit as st
from app_ext.charts import Charts
from app_ext.catalog_dropdown import CatalogDropDown
from app_ext.state import AppState
from gooddata.catalog import Catalog
from gooddata.execute import execute_custom_insight, get_attribute_values
from gooddata.sdk_wrapper import GoodDataSdkWrapper
from gooddata_sdk import CatalogAttribute


class InsightBuilder:
    def __init__(self, logger: Logger, sdk_wrapper: GoodDataSdkWrapper, app_state: AppState) -> None:
        self.logger = logger
        self.sdk_wrapper = sdk_wrapper
        self.workspace_id = app_state.get("workspace_id")
        self.app_state = app_state
        self.dropdown = CatalogDropDown(self.app_state)

    def render_catalog(self, catalog: Catalog) -> None:
        with st.sidebar.container():
            self.logger.info(f"{catalog.filtered_objects.report_removed_metrics=}")
            self.dropdown.render_multiselect(
                catalog.filtered_all, "selected_metrics", "Metrics",
                catalog.filtered_objects.report_removed_metrics
            )

        with st.sidebar.container():
            self.dropdown.render_multiselect(
                catalog.filtered_attributes, "selected_view_by", "View By",
                catalog.filtered_objects.report_removed_attributes
            )
        with st.sidebar.container():
            self.dropdown.render_singleselect(
                catalog.filtered_attributes, "selected_segmented_by", "Segmented By",
                catalog.filtered_objects.report_removed_attributes
            )
        if catalog.filtered_objects.count_removed:
            with st.sidebar.container():
                st.info(f"Catalog - showing {catalog.filtered_objects.count_filtered}/{catalog.filtered_objects.count_all}")

    def collect_filter_values(
        self, selected_filter_attributes: list[str]
    ) -> dict[str, list[str]]:
        filter_values = {}
        for attribute_obj_id in selected_filter_attributes:
            attribute_id = attribute_obj_id.split("/")[1]
            values = get_attribute_values(self.sdk_wrapper.sdk, self.workspace_id, attribute_id)
            filter_values[attribute_obj_id] = values
        return filter_values

    def only_date_attributes_selected(self, attributes: list[CatalogAttribute]) -> bool:
        # Check if only date attributes are selected, without metrics/facts
        # Enumerating date attributes only is tricky, because the date dimension can be connected to various datasets
        date_attributes = [a.id for a in attributes if a.granularity]
        selected_date_attributes = [a for a in self.app_state.selected_attribute_ids() if a in date_attributes]
        return not self.app_state.get('selected_facts') \
            and not self.app_state.get('selected_metrics') \
            and selected_date_attributes \
            and set(selected_date_attributes).issubset(set(date_attributes))

    @staticmethod
    def sort_data_frame(
        df: pd.DataFrame, catalog: Catalog
    ) -> pd.DataFrame:
        sort_columns, ascending = catalog.selected_sort_columns
        if sort_columns:
            return df.sort_values(by=sort_columns, ascending=ascending)
        else:
            return df

    def main(self) -> None:
        catalog = Catalog(self.logger, self.sdk_wrapper.sdk, self.workspace_id, self.app_state)

        # Sidebar
        self.render_catalog(catalog)

        # Main canvas
        selected_filter_attributes_obj_ids = self.app_state.get('selected_filter_attributes', [])
        filter_values = self.collect_filter_values(selected_filter_attributes_obj_ids)

        if self.only_date_attributes_selected(catalog.filtered_attributes):
            st.error("Enumerating DATE attribute(s) only is not yet supported.")
            st.info("Add a non-date attribute or fact/metric.")
        elif self.app_state.is_anything_selected():
            charts = Charts(
                self.logger, self.app_state,
                catalog, filter_values
            )
            charts.render_chart_header()

            gd_frames = self.sdk_wrapper.pandas.data_frames(self.workspace_id)
            df = execute_custom_insight(
                self.logger, gd_frames,
                # Must pass each property separately to utilize st.cache_data feature!
                self.app_state.selected_metric_ids_with_functions(),
                self.app_state.selected_attribute_ids(),
                self.app_state.selected_filter_attribute_values(),
            )
            df = self.sort_data_frame(df, catalog)

            charts.render_chart(df)
        else:
            st.info("Select Metrics/View By/Segmented By in the sidebar to create an insight!")
