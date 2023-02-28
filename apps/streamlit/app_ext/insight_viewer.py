from logging import Logger
import streamlit as st
from app_ext.charts import Charts
from app_ext.state import AppState
from gooddata.catalog import get_insights, ids_with_default, get_title_for_id
from gooddata.execute import execute_stored_insight
from gooddata.sdk_wrapper import GoodDataSdkWrapper

def insight_viewer(logger: Logger, sdk_wrapper: GoodDataSdkWrapper, app_state: AppState) -> None:
    sdk = sdk_wrapper.sdk
    workspace_id = app_state.get('workspace_id')
    insights = get_insights(logger, sdk, workspace_id)
    option_insight = st.sidebar.selectbox(
        label="Stored insights",
        options=ids_with_default(insights),
        format_func=lambda x: get_title_for_id(insights, x)
    )
    if app_state.is_set(option_insight):
        gd_frames = sdk_wrapper.pandas.data_frames(workspace_id)
        df = execute_stored_insight(logger, gd_frames, option_insight)
        Charts(logger, app_state).render_chart(df)
