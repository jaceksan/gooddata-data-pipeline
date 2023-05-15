import pandas as pd
import folium
from streamlit_folium import folium_static
import branca.colormap as cm
from gooddata.catalog import Catalog

MAX_RADIUS = 16

def render_geo_chart(df: pd.DataFrame, catalog: Catalog) -> None:
    lat_column = None
    lon_column = None

    for label in catalog.selected_view_by_geo_labels:
        if label.value_type == "GEO_LATITUDE":
            lat_column = label.title
        else:
            lon_column = label.title

    metric1 = catalog.selected_metrics[0]
    map_center = [df[lat_column][1:].astype(float).mean(), df[lon_column][1:].astype(float).mean()]
    max_m1 = df[metric1.title][1:].max()

    m = folium.Map(location=map_center, zoom_start=3)

    colormap = None
    metric2 = None
    if len(catalog.selected_metrics) > 1:
            metric2 = catalog.selected_metrics[1]
            max_m2 = float(df[metric2.title].max())
            color_indexes = [max_m2/8, max_m2/6, max_m2/4, max_m2/2, max_m2]
            colormap = cm.LinearColormap(colors=['blue', 'cyan', 'yellow', 'orange', 'red'],
                                         index=color_indexes, vmin=0, vmax=100,
                                         caption=f'{metric2.title}').add_to(m)

    # Add the markers to the map
    for i, row in df.iterrows():
        tooltip = f"{metric1.title}: {row[metric1.title]}"
        kwargs = {
            "location": (row[lat_column], row[lon_column]),
            "radius": row[metric1.title] / max_m1 * MAX_RADIUS,
            "popup": tooltip,
            "tooltip": tooltip,
            "fill": True,
            "fill_color": "blue",
            "color": "blue",
            "fill_opacity": 0.7
        }
        if len(catalog.selected_metrics) > 1:
            kwargs["popup"] = f"{metric1.title}: {row[metric1.title]}, {metric2.title}: {row[metric2.title]}"
            kwargs["tooltip"] = kwargs["popup"]
            kwargs["fill_color"] = colormap(row[metric2.title])
            kwargs["color"] = kwargs["fill_color"]

        folium.CircleMarker(**kwargs).add_to(m)

    # Display the map
    folium_static(m, width=1024, height=768)
