from argparse import Namespace
from logging import Logger
import pandas as pd
import streamlit as st
from gooddata.__init import DEFAULT_EMPTY_SELECT_OPTION_ID
from app_ext.charts import Charts
from app_ext.catalog_dropdown import CatalogDropDown
from app_ext.state import AppState
from gooddata.catalog import Catalog
from gooddata.execute import execute_custom_insight, get_attribute_values, invalidate_gd_caches
from gooddata.sdk_wrapper import GoodDataSdkWrapper
from gooddata_sdk import CatalogAttribute, CatalogLabel

# Workaround - when we utilize "key" property in multiselect/selectbox,
#   a warning is produced if we reset the default value in a custom way
st.elements.utils._shown_default_value_warning = True
#st.elements._shown_default_value_warning = False


class InsightBuilder:
    def __init__(self, logger: Logger, args: Namespace, sdk_wrapper: GoodDataSdkWrapper, app_state: AppState) -> None:
        self.logger = logger
        self.args = args
        self.sdk_wrapper = sdk_wrapper
        self.workspace_id = app_state.get("workspace_id")
        self.app_state = app_state
        self.dropdown = CatalogDropDown(self.app_state)

    def render_clear_buttons(self) -> bool:
        with st.sidebar.container():
            column_count = 1
            if self.args.gooddata_allow_clear_caches:
                column_count += 1
            cache_columns = st.sidebar.columns(column_count)
            with cache_columns[0]:
                if st.button("Clear app cache"):
                    st.cache_data.clear()
            if self.args.gooddata_allow_clear_caches:
                with cache_columns[1]:
                    if st.button("Clear GD cache"):
                        invalidate_gd_caches(self.logger, self.sdk_wrapper.sdk, st.session_state.workspace_id)

        with st.sidebar.container():
            if st.button("Clear report def"):
                self.app_state.reset_state()
                return True
        return False

    def update_catalog_by_selected_insight(self, catalog: Catalog, clear_report_def: bool):
        previous_insight_id = self.app_state.get("previous_selected_insight")
        insight_id = self.app_state.get("selected_insight")
        # Update catalog by selected insight only if the insight picker is used (value is changed)
        if insight_id not in [DEFAULT_EMPTY_SELECT_OPTION_ID, previous_insight_id]:
            # Set Insight in the dropdown to another value
            metrics, metrics_with_func = catalog.insight_metrics(insight_id)
            self.app_state.set("selected_metrics", [str(x.obj_id) for x in metrics])
            # TODO - how to distinguish view by and segmented by attributes Insight object?
            self.app_state.set("selected_view_by", [str(x.obj_id) for x in catalog.insight_attributes(insight_id)])
            self.app_state.set("selected_segmented_by", DEFAULT_EMPTY_SELECT_OPTION_ID)
            for metric_obj_id, metric_func in metrics_with_func.items():
                self.app_state.set(f"selected_metric_function__{metric_obj_id}", metric_func)
        elif (previous_insight_id in [x.id for x in catalog.insights] and insight_id == DEFAULT_EMPTY_SELECT_OPTION_ID) or clear_report_def:
            # Unset Insight in the dropdown
            self.app_state.reset_state()

    def render_catalog(self, catalog: Catalog, clear_report_def: bool) -> None:
        self.update_catalog_by_selected_insight(catalog, clear_report_def)

        with st.sidebar.container():
            self.dropdown.render_multiselect(
                # Inject filtered_all, metrics can be created from facts/attributes with functions (SUM, COUNT, ...)
                catalog.filtered_objects.filtered_all, "selected_metrics", "Metrics",
                help_text=catalog.filtered_objects.report_removed_metrics,
                title_obj_type=True,
            )
        with st.sidebar.container():
            self.dropdown.render_multiselect(
                catalog.filtered_objects.filtered_attributes, "selected_view_by", "View By",
                help_text=catalog.filtered_objects.report_removed_attributes
            )
        with st.sidebar.container():
            self.dropdown.render_singleselect(
                catalog.filtered_objects.filtered_attributes, "selected_segmented_by", "Segmented By",
                help_text=catalog.filtered_objects.report_removed_attributes
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

    def only_date_attributes_selected(self, catalog: Catalog) -> bool:
        # Check if only date attributes are selected, without metrics/facts
        # Enumerating date attributes only is tricky, because the date dimension can be connected to various datasets
        date_attribute_ids = [str(a.obj_id) for a in catalog.full_catalog.date_attributes]
        selected_standard_attributes = [a for a in self.app_state.selected_attribute_ids() if a not in date_attribute_ids]
        selected_date_attributes = [a for a in self.app_state.selected_attribute_ids() if a in date_attribute_ids]
        return not catalog.selected_metrics \
            and selected_date_attributes \
            and not selected_standard_attributes

    @staticmethod
    def sort_data_frame(
        df: pd.DataFrame, catalog: Catalog
    ) -> pd.DataFrame:
        sort_columns, ascending = catalog.selected_sort_columns
        if sort_columns:
            return df.sort_values(by=sort_columns, ascending=ascending)
        else:
            return df

    @staticmethod
    def get_geo_labels(attribute: CatalogAttribute) -> list[CatalogLabel]:
        return [l for l in attribute.labels if l.value_type in ["GEO_LATITUDE", "GEO_LONGITUDE"]]

    def get_relevant_metrics_attributes(self, chart_type: str, catalog: Catalog) -> tuple[dict[str, str], list[str]]:
        metrics_with_functions = self.app_state.selected_metric_ids_with_functions()
        attribute_ids = self.app_state.selected_attribute_ids()
        if chart_type == "Donut chart":
            metrics_with_functions = self.app_state.selected_first_metric_with_function()
            attribute_ids = self.app_state.selected_first_view_by()
        elif chart_type in ["Line chart", "Bar chart"]:
            metrics_with_functions = self.app_state.selected_first_metric_with_function()
            attribute_ids = self.app_state.selected_first_view_by_segmented_by()
        elif chart_type in ["Geo chart"]:
            geo_labels = catalog.selected_view_by_geo_labels
            attribute_ids = [str(l.obj_id) for l in geo_labels]
        return metrics_with_functions, attribute_ids

    def main(self) -> None:
        catalog = Catalog(self.logger, self.sdk_wrapper.sdk, self.workspace_id, self.app_state)

        # Sidebar
        clear_report_def = self.render_clear_buttons()
        self.render_catalog(catalog, clear_report_def)

        # Main canvas
        selected_filter_attributes_obj_ids = self.app_state.get('selected_filter_attributes', [])
        filter_values = self.collect_filter_values(selected_filter_attributes_obj_ids)

        charts = Charts(
            self.logger, self.app_state,
            catalog, clear_report_def, filter_values
        )
        charts.render_chart_header_type_stored_insights()

        if self.only_date_attributes_selected(catalog):
            st.warning("Enumerating DATE attribute(s) only is not yet supported.")
            st.info("Add a non-date attribute or fact/metric.")
        elif self.app_state.is_anything_selected():
            charts.render_chart_header_filters_metric_func_sort_by()
            gd_frames = self.sdk_wrapper.pandas.data_frames(self.workspace_id)
            # Execute report only with metrics/attributes relevant for the chart type
            # E.g. Donut Chart makes sense with only 1 metric and 1 attribute(view_by)
            metrics_with_functions, attribute_ids = self.get_relevant_metrics_attributes(charts.chart_type, catalog)
            df = execute_custom_insight(
                self.logger, gd_frames,
                # Must pass each property separately to utilize st.cache_data feature!
                metrics_with_functions,
                attribute_ids,
                self.app_state.selected_filter_attribute_values(),
            )
            df = self.sort_data_frame(df, catalog)

            charts.render_chart(df, metrics_with_functions)
        else:
            st.info(
                "Either pick metrics/view_by/segmented_by in the left panel "
                "or pick already stored report from the top dropdown."
            )
