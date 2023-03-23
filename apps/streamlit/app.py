import os
from logging import Logger
import streamlit as st
from app_ext.__init import APP_MODES, AppMode
from app_ext.insight_builder import InsightBuilder
from app_ext.insight_viewer import insight_viewer
from app_ext.state import AppState
from gooddata.catalog import get_workspaces, get_name_for_id, get_ids
from gooddata.execute import invalidate_gd_caches
from gooddata.sdk_wrapper import GoodDataSdkWrapper
from gooddata.args import parse_arguments
from gooddata.logger import get_logger
from gooddata_sdk import GoodDataSdk

def render_workspace_picker(logger: Logger, sdk: GoodDataSdk, app_state: AppState):
    workspaces = get_workspaces(logger, sdk)
    st.sidebar.selectbox(
        label="Workspaces:",
        options=get_ids(workspaces),
        format_func=lambda x: get_name_for_id(workspaces, x),
        key="workspace_id",
        on_change=app_state.reset_state
    )

def render_application_mode(app_state: AppState):
    st.sidebar.selectbox(
        label="Application mode:",
        options=APP_MODES,
        key="app_mode",
        on_change=app_state.reset_state
    )

def main():
    st.set_page_config(
        layout="wide", page_icon="favicon.ico", page_title="Streamlit-GoodData integration demo"
    )

    args = parse_arguments("streamlit-gooddata example application")
    logger = get_logger("streamlit-gooddata", args.debug)
    logger.info("Start rendering page")

    sdk_wrapper = GoodDataSdkWrapper(args, logger)
    gd_sdk = sdk_wrapper.sdk
    app_state = AppState(logger)
    app_state.debug_state()
    render_workspace_picker(logger, gd_sdk, app_state)
    render_application_mode(app_state)

    with st.sidebar.container():
        column_count = 1
        if args.gooddata_allow_clear_caches:
            column_count += 1
        cache_columns = st.sidebar.columns(column_count)
        with cache_columns[0]:
            if st.button("Clear app cache"):
                st.cache_data.clear()
        if args.gooddata_allow_clear_caches:
            with cache_columns[1]:
                if st.button("Clear GD cache"):
                    invalidate_gd_caches(logger, gd_sdk, st.session_state.workspace_id)

    with st.sidebar.container():
        if st.button("Clear report def"):
            app_state.reset_state()

    if st.session_state.app_mode == AppMode.INSIGHT_BUILDER.value:
        InsightBuilder(logger, sdk_wrapper, app_state).main()
    else:
        insight_viewer(logger, sdk_wrapper, app_state)


if __name__ == "__main__":
    main()
