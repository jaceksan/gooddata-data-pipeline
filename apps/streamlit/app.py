from logging import Logger
import streamlit as st
from app_ext.insight_builder import InsightBuilder
from app_ext.state import AppState
from gooddata.catalog import get_workspaces, get_name_for_id, get_ids
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

    if app_state.get("workspace_id") is None:
        st.warning(f"Your GoodData instance is empty, no workspace is there, there is nothing to analyze.")
    else:
        InsightBuilder(logger, args, sdk_wrapper, app_state).main()


if __name__ == "__main__":
    main()
