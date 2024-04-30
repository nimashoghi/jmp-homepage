import os
from typing import Any

import crystal_toolkit.components as ctc
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash import dcc, html
from dash.dependencies import Input, Output, State
from pymatgen.core import Structure

pio.templates.default = "presentation"

df = pd.read_pickle(os.environ.get("INPUT_FILE", "./df_small.pkl"))

plot_labels = {
    "dataset_name": "Dataset",
    "subset": "Subset",
}
dataset_colors: dict[str, str] = {
    "QM9": "#8dd3c7",
    "MD17": "#bebada",
    "MD22": "#b3de69",
    "SPICE": "#fb8072",
    "Matbench": "#80b1d3",
    "QMOF": "#fdb462",
}
dataset_colors_pt = {
    "OC20": "#bc80bd",
    "OC22": "#994c00",
    "ANI1x": "#d9d9d9",
    "Transition1x": "#fccde5",
}
colors = {**dataset_colors, **dataset_colors_pt}
fig = px.scatter(
    df,
    x="2d_x",
    y="2d_y",
    color="dataset_name",
    color_discrete_map=colors,
    labels=plot_labels,
    hover_name="dataset_full_name",
    hover_data=["subset", "description", "url"],
)
title = "t-SNE of JMP Embeddings"
fig.update_layout(
    title=dict(text=f"<b>{title}</b>", x=0.5, font_size=20),
    margin=dict(b=20, l=40, r=20, t=100),
)
fig.update_layout(showlegend=True)

fig.update_xaxes(title_text="", showticklabels=False)
fig.update_yaxes(title_text="", showticklabels=False)

# Hide the gridlines
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)


benzene = df[df["dataset"] == "md17.benzene"].iloc[-1]["structure"]
largest_structure_idx = 2680
largest_structure_idx_relative_to_qmof = 66
largest_structure_row = df.iloc[largest_structure_idx]

SELECTED_DICT = {
    "marker": {"size": 20, "color": "#010101", "opacity": 0.95},
}


def update_fig_for_initial():
    new_data_list = []
    for data in fig.data:
        if data.name != largest_structure_row["dataset_name"]:
            new_data_list.append(data)
            continue
        new_data_list.append(
            data.update(
                {
                    "selected": SELECTED_DICT,
                    "selectedpoints": [largest_structure_idx_relative_to_qmof],
                }
            )
        )
    fig.data = tuple(new_data_list)


update_fig_for_initial()

structure_component = ctc.StructureMoleculeComponent(
    largest_structure_row.structure,
    id="structure",
)
app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body style="background-color: white !important;">
        <!--[if IE]><script>
        alert("Dash v2.7+ does not support Internet Explorer. Please use a newer browser.");
        </script><![endif]-->
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""
graph = dcc.Graph(
    id="tsne-scatter-plot",
    figure=fig,
    style={"width": "100%"},
)
struct_title = html.H2(
    "Try clicking on a point in the plot to see its corresponding structure here",
    id="struct-title",
    style=dict(position="absolute", padding="1ex 1em", maxWidth="25em"),
)
app.layout = dbc.Row(
    [
        dbc.Col([graph], md=6, sm=12),
        dbc.Col([struct_title, structure_component.layout(size="100%")], md=6, sm=12),
    ],
)
ctc.register_crystal_toolkit(app=app, layout=app.layout)


@app.callback(
    Output(structure_component.id(), "data"),
    Output(struct_title, "children"),
    Output(graph, "figure"),
    Input(graph, "clickData"),
    State(graph, "figure"),
)
def update_structure(
    click_data: dict[str, list[dict[str, Any]]],
    current_fig: dict,
) -> tuple[Structure, str, dict]:
    if (
        click_data is None
        or (points := click_data.get("points")) is None
        or len(points) == 0
    ):
        raise dash.exceptions.PreventUpdate

    data = click_data["points"][0]

    curve_number = data.get("curveNumber", 0)
    unique_dataset_list = list(df["dataset_name"].unique())
    df_filtered = df[df["dataset_name"] == unique_dataset_list[curve_number]]

    point_idx = data.get("pointIndex", 0)
    row = df_filtered.iloc[point_idx]

    structure = row.structure
    dataset = row.dataset_full_name

    # Update the style of the selected point in the t-SNE plot
    updated_fig = current_fig.copy()
    selected_point = SELECTED_DICT
    # Unselect the previous points
    for data in updated_fig["data"]:
        data.pop("selectedpoints", None)
        data.pop("selected", None)

    updated_fig["data"][curve_number]["selectedpoints"] = [point_idx]
    updated_fig["data"][curve_number]["selected"] = selected_point

    return structure, dataset, updated_fig


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
