from __future__ import annotations

import os

import crystal_toolkit.components as ctc
import dash
import pandas as pd
import plotly.io as pio
from dash import html

pio.templates.default = "plotly_white"


df = pd.read_pickle(os.environ.get("INPUT_FILE", "./df_small.pkl"))
row = df[df["dataset_name"] == "ANI1x"].iloc[0]
# structure: Structure = row.structure
# print(type(structure))
# # structure.lattice.pbc = (True, True, False)
# structure.lattice = Lattice(structure.lattice.matrix, (True, True, False))


structure_component = ctc.StructureMoleculeComponent(
    row.structure,
    id="structure",
)
app = dash.Dash()
app.layout = html.Div(
    [structure_component.layout()],
    style=dict(margin="2em", padding="1em"),
)
ctc.register_crystal_toolkit(app=app, layout=app.layout)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
