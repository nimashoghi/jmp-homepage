from __future__ import annotations

from typing import TYPE_CHECKING, Any

import crystal_toolkit.components as ctc
import dash
import pandas as pd
import plotly.express as px
import plotly.io as pio
from crystal_toolkit.helpers.utils import get_data_table
from crystal_toolkit.settings import SETTINGS
from dash import dcc, html
from dash.dependencies import Input, Output, State

if TYPE_CHECKING:
    from pymatgen.core import Structure

pio.templates.default = "plotly_white"


__author__ = "Janosh Riebesell"
__date__ = "2022-07-21"
__email__ = "janosh@lbl.gov"

"""
Run this app with:
    python crystal_toolkit/apps/examples/tsne_structure_on_hover.py
"""


df = pd.read_pickle("/workspaces/fm/fm/notebooks/webpage/df.pkl")
# print(df)

plot_labels = {
    "dataset": "Dataset",
    "x": "t-SNE Dimension 1",
    "y": "t-SNE Dimension 2",
}

fig_tsne = px.scatter(
    df,
    x="x",
    y="y",
    color="dataset",
    labels=plot_labels,
    hover_name="dataset",
)
title = "t-SNE Projection of GNN Embeddings"
fig_tsne.update_layout(
    title=dict(text=f"<b>{title}</b>", x=0.5, font_size=20),
    legend=dict(x=1, y=1, xanchor="right"),
    margin=dict(b=20, l=40, r=20, t=100),
)
# slightly increase scatter point size (lower sizeref means larger)
fig_tsne.update_traces(marker_sizeref=0.05, selector=dict(mode="markers"))


structure_component = ctc.StructureMoleculeComponent(id="structure")

app = dash.Dash(prevent_initial_callbacks=True, assets_folder=SETTINGS.ASSETS_PATH)
graph = dcc.Graph(
    id="tsne-scatter-plot",
    figure=fig_tsne,
    style={"width": "90vh"},
)
hover_click_dd = dcc.Dropdown(
    id="hover-click-dropdown",
    options=["hover", "click"],
    value="hover",
    clearable=False,
    style=dict(minWidth="5em"),
)
hover_click_dropdown = html.Div(
    [html.Label("Update structure on:", style=dict(fontWeight="bold")), hover_click_dd],
    style=dict(
        display="flex",
        placeContent="center",
        placeItems="center",
        gap="1em",
        margin="1em",
    ),
)
struct_title = html.H2(
    "Try hovering on a point in the plot to see its corresponding structure",
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
table = get_data_table(
    df.drop(columns="structure").reset_index(), id="data-table", virtualized=False
)
app.layout = html.Div(
    [hover_click_dropdown, graph_structure_div, table],
    style=dict(margin="2em", padding="1em"),
)
ctc.register_crystal_toolkit(app=app, layout=app.layout)


@app.callback(
    Output(structure_component.id(), "data"),
    Output(struct_title, "children"),
    Output(table, "style_data_conditional"),
    Input(graph, "hoverData"),
    Input(graph, "clickData"),
    State(hover_click_dd, "value"),
)
def update_structure(
    hover_data: dict[str, list[dict[str, Any]]],
    click_data: dict[str, list[dict[str, Any]]],  # needed only as callback trigger
    dropdown_value: str,
) -> tuple[Structure, str]:
    """Update StructureMoleculeComponent with pymatgen structure when user clicks or hovers a
    scatter point.
    """
    triggered = dash.callback_context.triggered[0]
    if dropdown_value == "click" and triggered["prop_id"].endswith(".hoverData"):
        # do nothing if we're in update-on-click mode but callback was triggered by hover event
        raise dash.exceptions.PreventUpdate

    # hover_data and click_data are identical since a hover event always precedes a click so
    # we always use hover_data
    data = hover_data["points"][0]
    material_id = data["pointIndex"]

    structure = df.structure[material_id]
    dataset = df.dataset[material_id]

    # highlight corresponding row in table
    style_data_conditional = {
        "if": {"row_index": material_id},
        "backgroundColor": "#3D9970",
        "color": "white",
    }

    return structure, dataset, [style_data_conditional]


if __name__ == "__main__":
    app.run(debug=True, port=8050)
