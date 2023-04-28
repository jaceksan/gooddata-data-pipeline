import altair as alt
import pandas as pd
from gooddata_sdk import AttrCatalogEntity
from gooddata.catalog import metric_column_name


class AltairCharts:
    def __init__(
        self, df: pd.DataFrame, chart_type: str, view_by: AttrCatalogEntity, metric: AttrCatalogEntity,
        metrics_with_functions: dict[str, str],
    ) -> None:
        self.df = df
        self.chart_type = chart_type
        self.metric = metric
        self.view_by = view_by
        self.metrics_with_functions = metrics_with_functions

    @property
    def metric_column(self):
        metric_func = self.metrics_with_functions[str(self.metric.obj_id)]
        return metric_column_name(self.metric, metric_func)

    def generate_line_bar_chart(self, segment_by: AttrCatalogEntity):
        kwargs = {
            "x": alt.X(self.view_by.title, title=self.view_by.title),
            "y": alt.Y(self.metric_column, title=self.metric.title, type="quantitative"),
        }
        chart_title = f"`{self.metric.title}` viewed by `{self.view_by.title}`"
        if segment_by:
            kwargs["color"] = segment_by.title
            chart_title = f"{chart_title} segmented by `{segment_by.title}`"

        if self.chart_type == "Bar chart":
            elements = (
                alt.Chart(self.df, height=500, title=chart_title)
                .mark_bar()
                .encode(**kwargs)
            )
        else:
            # Default is Line chart
            elements = (
                alt.Chart(self.df, height=500, title=chart_title)
                .mark_line()
                .encode(**kwargs)
            )
        return elements.interactive()


    def generate_donut_chart(self):
        chart_title = f"`{self.metric.title}` viewed by `{self.view_by.title}`"
        base = alt.Chart(self.df, height=500, title=chart_title).encode(
            color=alt.Color(field=self.view_by.title, type="nominal", title=self.view_by.title),
            theta=alt.Theta(field=self.metric_column, type="quantitative", title=self.metric.title),
            # Have to specify sort here even though input data frame is sorted properly
            order=alt.Order(field=self.metric_column, type="quantitative", sort="descending")
        )
        chart = base.mark_arc(innerRadius=50, outerRadius=200)
        # TODO - it is ugly, not correctly positioned
        #text = base.mark_text(radius=230, size=14).encode(text=metric_column)

        return chart.interactive()
