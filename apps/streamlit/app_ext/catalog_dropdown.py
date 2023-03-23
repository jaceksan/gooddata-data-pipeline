import streamlit as st
from app_ext.state import AppState
from gooddata.catalog import ObjectsLdm, get_title_for_obj_id
from gooddata_sdk.catalog.entity import CatalogEntity
from gooddata.__init import DEFAULT_EMPTY_SELECT_OPTION_ID


class CatalogDropDown:
    def __init__(self, app_state: AppState) -> None:
        self.app_state = app_state

    @staticmethod
    def get_object_ids(
            objects: list[CatalogEntity], add_empty=False
    ) -> list[str]:
        result = []
        if add_empty:
            result = [DEFAULT_EMPTY_SELECT_OPTION_ID]
        result.extend([f"{o.obj_id}" for o in objects])
        return result

    def render_multiselect(self, objects: ObjectsLdm, select_key: str, label: str, help_text: str = "") -> None:
        self.app_state.debug_state(select_key, "BEFORE")
        st.multiselect(
            label=label,
            options=self.get_object_ids(objects),
            format_func=lambda x: get_title_for_obj_id(objects, x),
            key=select_key,
            default=self.app_state.get(select_key, []),
            help=help_text,
        )
        self.app_state.debug_state(select_key, "AFTER")

    def render_singleselect(self, objects: ObjectsLdm, select_key: str, label: str, help_text: str = "") -> None:
        self.app_state.debug_state(select_key, "BEFORE")
        st.selectbox(
            label=label,
            options=self.get_object_ids(objects, add_empty=True),
            format_func=lambda x: get_title_for_obj_id(objects, x),
            key=select_key,
            help=help_text,
        )
        self.app_state.debug_state(select_key, "AFTER")

