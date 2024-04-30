import os
from typing import Any

import crystal_toolkit.components as ctc
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash import dcc, html
from dash.dependencies import Input, Output
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
    # legend=dict(
    #     orientation="h",
    #     yanchor="bottom",
    #     y=1.02,
    #     xanchor="right",
    #     x=1,
    # ),
    margin=dict(b=20, l=40, r=20, t=100),
)
fig.update_layout(showlegend=True)

fig.update_xaxes(title_text="", showticklabels=False)
fig.update_yaxes(title_text="", showticklabels=False)

# Hide the gridlines
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)


structure_component = ctc.StructureMoleculeComponent(
    id="structure",
)
app = dash.Dash(
    prevent_initial_callbacks=True, external_stylesheets=[dbc.themes.BOOTSTRAP]
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
app.layout = dbc.Row(
    [
        dbc.Col([graph], md=6, sm=12),
        dbc.Col([struct_title, structure_component.layout(size="100%")], md=6, sm=12),
    ],
    # style=dict(display="flex", gap="2em", margin="2em 0"),
)
# table = get_data_table(
#     df.drop(columns="structure").reset_index(), id="data-table", virtualized=False
# )
ctc.register_crystal_toolkit(app=app, layout=app.layout)


@app.callback(
    Output(structure_component.id(), "data"),
    Output(struct_title, "children"),
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
    app.run(host="0.0.0.0", port=5000, debug=False)
