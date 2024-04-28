from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import crystal_toolkit.components as ctc
import dash
import pandas as pd
import plotly.express as px
import plotly.io as pio
from crystal_toolkit.settings import SETTINGS
from dash import dcc, html
from dash.dependencies import Input, Output

if TYPE_CHECKING:
    from pymatgen.core import Structure

pio.templates.default = "plotly_white"


__author__ = "Your Name"
__date__ = "2023-06-09"
__email__ = "your.email@example.com"

"""
Run this app with:
    python script_name.py
"""


df = pd.read_pickle(os.environ["INPUT_FILE"])
# print(df)

plot_labels = {
    "dataset_name": "Dataset",
    "subset": "Subset",
}

fig_tsne = px.scatter(
    df,
    x="x",
    y="y",
    color="dataset_name",
    labels=plot_labels,
    hover_name="dataset_full_name",
    hover_data=["subset", "description", "url"],
)
title = "t-SNE of JMP Embeddings"
fig_tsne.update_layout(
    title=dict(text=f"<b>{title}</b>", x=0.5, font_size=20),
    legend=dict(x=1, y=1, xanchor="right"),
    margin=dict(b=20, l=40, r=20, t=100),
)

# turn off native plotly.js hover effects - make sure to use
# hoverinfo="none" rather than "skip" which also halts events.
fig_tsne.update_traces(hoverinfo="none", hovertemplate=None)


structure_component = ctc.StructureMoleculeComponent(
    id="structure",
    bonded_sites_outside_unit_cell=True,
    hide_incomplete_bonds=False,
    scene_settings=dict(
        unit_cell=False,
    ),
)

app = dash.Dash(prevent_initial_callbacks=True, assets_folder=SETTINGS.ASSETS_PATH)
graph = dcc.Graph(
    id="tsne-scatter-plot",
    figure=fig_tsne,
    style={"width": "90vh"},
    clear_on_unhover=True,
)
# hover_click_dd = dcc.Dropdown(
#     id="hover-click-dropdown",
#     options=["hover", "click"],
#     value="hover",
#     clearable=False,
#     style=dict(minWidth="5em"),
# )
# hover_click_dropdown = html.Div(
#     [html.Label("Update structure on:", style=dict(fontWeight="bold")), hover_click_dd],
#     style=dict(
#         display="flex",
#         placeContent="center",
#         placeItems="center",
#         gap="1em",
#         margin="1em",
#     ),
# )
struct_title = html.H2(
    "Try clicking on a point in the plot to see its corresponding structure here",
    id="struct-title",
    style=dict(position="absolute", padding="1ex 1em", maxWidth="25em"),
)
graph_structure_div = html.Div(
    [
        graph,
        html.Div([struct_title, structure_component.layout()]),
    ],
    style=dict(display="flex", gap="2em", margin="2em 0"),
)
# table = get_data_table(
#     df.drop(columns="structure").reset_index(), id="data-table", virtualized=False
# )

hover_structure_component = ctc.StructureMoleculeComponent(
    id="structure",
    bonded_sites_outside_unit_cell=True,
    hide_incomplete_bonds=False,
    scene_settings=dict(
        unit_cell=False,
    ),
)
app.layout = html.Div(
    [
        # hover_click_dropdown,
        graph_structure_div,
        dcc.Tooltip([hover_structure_component.layout()], id="graph-tooltip"),
    ],
    style=dict(margin="2em", padding="1em"),
)
ctc.register_crystal_toolkit(app=app, layout=app.layout)


@app.callback(
    Output("graph-tooltip", "show"),
    Output("graph-tooltip", "bbox"),
    Output(hover_structure_component.id(), "data"),
    # Output("graph-tooltip", "children"),
    Input(graph, "hoverData"),
)
def display_hover(hover_data):
    if hover_data is None:
        raise dash.exceptions.PreventUpdate

    # hover_data and click_data are identical since a hover event always precedes a click so
    # we always use hover_data
    data = hover_data["points"][0]
    bbox = data["bbox"]

    # Get the row index of the material in the dataframe
    curve_number = data.get("curveNumber", 0)
    # Use the curve number as the index of the dataset
    unique_dataset_list = list(df["dataset_name"].unique())
    df_filtered = df[df["dataset_name"] == unique_dataset_list[curve_number]]

    # Now, get the corresponding row
    point_idx = data.get("pointIndex", 0)
    row = df_filtered.iloc[point_idx]

    # return True, bbox, children
    return True, bbox, row.structure


@app.callback(
    Output(structure_component.id(), "data"),
    Output(struct_title, "children"),
    # Output("graph-tooltip", "children"),
    # Output(table, "style_data_conditional"),
    # Input(graph, "hoverData"),
    Input(graph, "clickData"),
    # State(hover_click_dd, "value"),
)
def update_structure(
    # hover_data: dict[str, list[dict[str, Any]]],
    click_data: dict[str, list[dict[str, Any]]],  # needed only as callback trigger
    # dropdown_value: str,
) -> tuple[Structure, str]:
    """Update StructureMoleculeComponent with pymatgen structure when user clicks or hovers a
    scatter point.
    """
    # triggered = dash.callback_context.triggered[0]
    # if dropdown_value == "click" and triggered["prop_id"].endswith(".hoverData"):
    #     # do nothing if we're in update-on-click mode but callback was triggered by hover event
    #     raise dash.exceptions.PreventUpdate

    # hover_data and click_data are identical since a hover event always precedes a click so
    # we always use hover_data
    data = click_data["points"][0]

    # Get the row index of the material in the dataframe
    curve_number = data.get("curveNumber", 0)
    # Use the curve number as the index of the dataset
    unique_dataset_list = list(df["dataset_name"].unique())
    df_filtered = df[df["dataset_name"] == unique_dataset_list[curve_number]]

    # Now, get the corresponding row
    point_idx = data.get("pointIndex", 0)
    row = df_filtered.iloc[point_idx]

    structure = row.structure
    dataset = row.dataset_full_name
    # print(material_id, dataset, hover_data)

    # # highlight corresponding row in table
    # style_data_conditional = {
    #     "if": {"row_index": material_id},
    #     "backgroundColor": "#3D9970",
    #     "color": "white",
    # }

    return structure, dataset


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
