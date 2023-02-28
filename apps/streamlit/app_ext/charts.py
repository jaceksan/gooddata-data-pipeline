from logging import Logger
from typing import Optional
import pandas as pd
import streamlit as st
from app_ext.catalog_dropdown import CatalogDropDown
from app_ext.state import AppState
from gooddata_sdk import CatalogAttribute, CatalogFact
from gooddata.catalog import Catalog
from streamlit_ext.altair_charts import AltairCharts

FACT_AGG_FUNC = [
    "SUM",
    "AVG",
    "MAX",
    "MEDIAN",
    "MIN",
    "RUNSUM",
]

ATTRIBUTE_AGG_FUNC = [
    "COUNT",
    "APPROXIMATE_COUNT",
]


class Charts:
    def __init__(
        self, logger: Logger, app_state: AppState,
        catalog: Catalog,
        filter_values: Optional[dict[str, list[str]]] = None,
    ) -> None:
        self.logger = logger
        self.app_state = app_state
        self.dropdown = CatalogDropDown(self.app_state)
        self.catalog = catalog
        self.filter_values = filter_values or []

    @property
    def chart_types(self):
        chart_types = ["Table"]
        if self.catalog.selected_view_by and self.catalog.selected_metrics:
            chart_types.extend(["Line chart", "Bar chart", "Donut chart"])
        return chart_types

    @property
    def chart_type(self):
        return self.app_state.get("chart_type") or "Table"

    def render_filter_attributes(self):
        # Non DATE attributes. TODO - date filters
        standard_attributes = [x for x in self.catalog.all_attributes if not x.granularity]
        if standard_attributes:
            with st.container():
                self.dropdown.render_multiselect(
                    standard_attributes,
                    "selected_filter_attributes",
                    "Filter attributes"
                )

    def render_attribute_filter_values(self) -> None:
        columns = st.columns(len(self.catalog.selected_filter_attributes))
        for i, attribute in enumerate(self.catalog.selected_filter_attributes):
            with columns[i]:
                # TODO - support more filter operators (<>, ...), metric filters, date filters, etc.
                st.multiselect(
                    label=f"{attribute.title} values",
                    options=self.filter_values[str(attribute.obj_id)],
                    key=f"selected_filter_attribute_values__{attribute.obj_id}",
                    default=self.app_state.get(f"selected_filter_attribute_values__{attribute.obj_id}", []),
                )

    def render_metric_functions(self):
        columns = st.columns(len(self.catalog.selected_metrics))
        for i, metric in enumerate(self.catalog.selected_metrics):
            func_list = None
            default = None
            if isinstance(metric, CatalogFact):
                func_list = FACT_AGG_FUNC
                default = "SUM"
            elif isinstance(metric, CatalogAttribute):
                default = "COUNT"
                func_list = ATTRIBUTE_AGG_FUNC
            if func_list:
                select_key = f"selected_metric_function__{metric.obj_id}"
                kwargs = {
                    "label": f"{metric.title} function",
                    "options": func_list,
                    "key": select_key,
                }
                if not self.app_state.get(select_key):
                    kwargs["index"] = func_list.index(default)
                with columns[i]:
                    st.selectbox(**kwargs)

    def render_sort_by(self):
        with st.container():
            self.dropdown.render_multiselect(self.catalog.selected_all, "selected_sort_by", "Sort by")

    def render_sort_by_methods(self):
        columns = st.columns(len(self.catalog.selected_sort_by))
        for i, ldm_object in enumerate(self.catalog.selected_sort_by):
            with columns[i]:
                st.checkbox(label=f"{ldm_object.title} DESC", key=f"selected_sort_by_desc__{ldm_object.obj_id}")

    def render_chart_header(self):
        with st.container():
            columns = st.columns((2, 10))
            with columns[0]:
                st.selectbox(label="Chart type", options=self.chart_types, key="chart_type")
            with columns[1]:
                if self.catalog.selected_metrics:
                    with st.container():
                        self.render_metric_functions()

        with st.container():
            columns = st.columns((2, 10))
            with columns[0]:
                self.render_filter_attributes()

                if self.chart_type == "Table":
                    self.render_sort_by()

            with columns[1]:
                if self.app_state.get("selected_filter_attributes"):
                    self.render_attribute_filter_values()

                if self.catalog.selected_sort_by:
                    self.render_sort_by_methods()


    def display_skipped_entities(self) -> None:
        if self.chart_type != "Table" and len(self.catalog.selected_metrics) > 1 or len(self.catalog.selected_view_by) > 1:
            skipped_metrics = [x.title for x in self.catalog.selected_metrics[1:]]
            skipped_view_by = [x.title for x in self.catalog.selected_view_by[1:]]
            st.info(
                "These selected catalog entities cannot be visualized in selected type of chart: "
                f"{skipped_metrics=} {skipped_view_by=}"
            )

    def render_chart(self, df: pd.DataFrame) -> None:
        with st.container():
            self.display_skipped_entities()
            if self.chart_type == "Table":
                sub_df = self.app_state.handle_paging(df)
                st.dataframe(sub_df, use_container_width=True, height=500)
            else:
                metric_for_chart = next(iter(self.catalog.selected_metrics), None)
                view_by_for_chart = next(iter(self.catalog.selected_view_by), None)
                if view_by_for_chart:
                    # Altair charts do not accept df.MultiIndex
                    df.reset_index(inplace=True)
                if self.chart_type in ["Line chart", "Bar chart"]:
                    st.altair_chart(
                        AltairCharts(
                            df, self.chart_type, view_by_for_chart, metric_for_chart
                        ).generate_line_bar_chart(self.catalog.selected_segmented_by),
                        use_container_width=True
                    )
                elif self.chart_type == "Donut chart":
                    st.altair_chart(
                        AltairCharts(
                            df, self.chart_type, view_by_for_chart, metric_for_chart
                        ).generate_donut_chart(),
                        use_container_width=True
                    )
