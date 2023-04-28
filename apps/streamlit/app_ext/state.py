from logging import Logger
from typing import Union, Optional

import streamlit as st
import pandas as pd

from app_ext.__init import AppMode
from gooddata.__init import DEFAULT_EMPTY_SELECT_OPTION_ID

PER_PAGE = 20


class AppState:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        self.init_state()

    def init_state(self):
        self.logger.debug("INIT STATE")
        if 'app_mode' not in st.session_state:
            st.session_state.app_mode = AppMode.INSIGHT_BUILDER.value
        if 'page_number' not in st.session_state:
            st.session_state.page_number = 1

    def reset_state(self):
        self.logger.debug("RESET STATE")
        st.session_state.page_number = 1
        if self.get("selected_insight"):
            st.session_state.selected_insight = DEFAULT_EMPTY_SELECT_OPTION_ID
        if self.get('selected_metrics'):
            st.session_state.selected_metrics = []
        for metric_id in self.get('selected_metric', []):
            del st.session_state[f"selected_metric_function__{metric_id}"]
        if self.get('selected_view_by'):
            st.session_state.selected_view_by = []
        if self.get('selected_segmented_by'):
            st.session_state.selected_segmented_by = DEFAULT_EMPTY_SELECT_OPTION_ID
        if self.get('selected_filter_attributes'):
            st.session_state.selected_filter_attributes = []
        for attribute_id in self.get('selected_filter_attributes', []):
            del st.session_state[f"selected_filter_attribute_values__{attribute_id}"]

    @staticmethod
    def is_set(option_name: str) -> bool:
        return option_name and option_name != DEFAULT_EMPTY_SELECT_OPTION_ID

    @staticmethod
    def set(option_name: str, value: Optional[Union[bool, int, str, list[str]]]) -> None:
        st.session_state[option_name] = value

    @staticmethod
    def get(option_name: str, default=None) -> Union[bool, int, str, list[str]]:
        return st.session_state.get(option_name, default)

    def is_anything_selected(self) -> bool:
        return bool(self.get('selected_metrics')) \
            or bool(self.get('selected_view_by')) \
            or bool(self.get('selected_facts'))

    def selected_catalog_all(self) -> list[str]:
        return self.get('selected_metrics', []) + self.selected_attribute_ids()

    def selected_attribute_ids(self) -> list[str]:
        selected_segmented_by = self.get("selected_segmented_by", DEFAULT_EMPTY_SELECT_OPTION_ID)
        selected_view_by = self.get("selected_view_by", [])
        if selected_segmented_by and selected_segmented_by != DEFAULT_EMPTY_SELECT_OPTION_ID:
            return selected_view_by + [selected_segmented_by]
        else:
            return selected_view_by

    def selected_first_view_by_segmented_by(self) -> list[str]:
        result = []
        view_by = next(iter([x for x in self.get("selected_view_by")]))
        if view_by:
            result.append(view_by)
        segmented_by = self.get("selected_segmented_by", None)
        if segmented_by and segmented_by != DEFAULT_EMPTY_SELECT_OPTION_ID:
            result.append(segmented_by)
        return result

    def selected_first_view_by(self) -> list[str]:
        first = self.selected_first_view_by_segmented_by()
        if first:
            return [self.selected_first_view_by_segmented_by()[0]]
        else:
            return []

    def selected_first_metric_with_function(self) -> Optional[dict[str, str]]:
        selected_first_metric = next(iter(self.get("selected_metrics") or []), None)
        return None if not selected_first_metric \
            else {selected_first_metric: self.selected_metric_ids_with_functions()[selected_first_metric]}

    def selected_metric_ids_with_functions(self) -> dict[str, str]:
        result = {}
        for metric_id in self.get('selected_metrics', []):
            default = None
            if metric_id.startswith("fact"):
                default = "SUM"
            elif metric_id.startswith("attribute"):
                default = "COUNT"
            result[metric_id] = self.get(f"selected_metric_function__{metric_id}", default)
        return result

    def selected_filter_attribute_values(self) -> dict[str, list[str]]:
        result = {}
        for attribute_id in self.get('selected_filter_attributes', []):
            selected_values = self.get(f"selected_filter_attribute_values__{attribute_id}")
            if selected_values:
                result[attribute_id] = selected_values
        return result

    def selected_sort_by_desc(self) -> dict[str, bool]:
        result = {}
        for object_id in self.get("selected_sort_by", []):
            result[object_id] = self.get(f"selected_sort_by_desc__{object_id}", False)
        return result

    def handle_paging(self, df: pd.DataFrame) -> pd.DataFrame:
        last_page = (len(df) // PER_PAGE) + 1
        first_row = st.container()
        left_column, mid_column, right_column = first_row.columns([1, 1, 1])
        if left_column.button("Previous"):
            if self.get("page_number") < 2:
                self.set("page_number", last_page)
            else:
                self.set("page_number", self.get("page_number") - 1)
        if right_column.button("Next"):
            if self.get("page_number") > last_page - 1:
                self.set("page_number", 1)
            else:
                self.set("page_number", self.get("page_number") + 1)
        with mid_column:
            st.write(f"Page number: {self.get('page_number')}/{last_page}")

        # Get start and end indices of the next page of the dataframe
        start_idx = (self.get('page_number') - 1) * PER_PAGE
        end_idx = self.get('page_number') * PER_PAGE
        return df.iloc[start_idx:end_idx]

    def debug_state(self, state_field: str = None, suffix_msg: str = ""):
        if state_field:
            msg = f"SESSION.{state_field} = {self.get(state_field)}"
        else:
            msg = f"SESSION = {st.session_state}"
        if suffix_msg:
            msg = msg + " " + suffix_msg
        self.logger.debug(msg)