import base64
import io
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html, no_update
from PIL import Image

image_base_path = Path("/mnt/datasets/jmprenders/flat/")


def image_to_base64(image_path: str | Path) -> str:
    im = Image.open(image_path)

    # dump it to base64
    with io.BytesIO() as buffer:
        im.save(buffer, format="JPEG")
        encoded_iamge = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/jpeg;base64,{encoded_iamge}"


# Load the data
df = pd.read_pickle("/workspaces/jmp-homepage/df_small.pkl")

# Color for each dataset
datasets = df["dataset_name"].unique()
color_map = {
    0: "#E52B50",
    1: "#9F2B68",
    2: "#3B7A57",
    3: "#3DDC84",
    4: "#FFBF00",
    5: "#915C83",
    6: "#008000",
    7: "#7FFFD4",
    8: "#E9D66B",
    9: "#007FFF",
}
color_map = {dataset: color_map[i] for i, dataset in enumerate(datasets)}
colors = [color_map[label] for label in df["dataset_name"]]

fig = go.Figure(
    data=[
        go.Scatter3d(
            x=df["3d_x"],
            y=df["3d_y"],
            z=df["3d_z"],
            mode="markers",
            marker=dict(
                size=2,
                color=colors,
            ),
        )
    ]
)

fig.update_layout(
    scene=dict(
        xaxis=dict(
            showticklabels=False,
        ),
        yaxis=dict(
            showticklabels=False,
        ),
        zaxis=dict(
            showticklabels=False,
        ),
    )
)

fig.update_traces(
    hoverinfo="none",
    hovertemplate=None,
)

app = Dash(__name__)

app.layout = html.Div(
    className="container",
    children=[
        dcc.Graph(id="graph-5", figure=fig, clear_on_unhover=True),
        dcc.Tooltip(id="graph-tooltip-5", direction="bottom"),
    ],
)


@callback(
    Output("graph-tooltip-5", "show"),
    Output("graph-tooltip-5", "bbox"),
    Output("graph-tooltip-5", "children"),
    Input("graph-5", "hoverData"),
)
def display_hover(hoverData):
    if hoverData is None:
        return False, no_update, no_update

    # demo only shows the first point, but other points may also be available
    hover_data = hoverData["points"][0]
    bbox = hover_data["bbox"]
    num = hover_data["pointNumber"]
    # if "original_index" in df.columns:
    #     num = df["original_index"].iloc[num]

    # The image path is image_base_path / f"{num}.jpeg"
    image_path = image_base_path / f"{num}.jpeg"
    assert image_path.exists(), f"Image path {image_path} does not exist."
    image_url = image_to_base64(image_path)

    children = [
        html.Div(
            [
                html.H6(f"Image {num}"),
                html.Img(
                    src=image_url,
                    # style={"width": "50px", "display": "block", "margin": "0 auto"},
                ),
                # html.P(
                #     "MNIST Digit " + str(labels[num]), style={"font-weight": "bold"}
                # ),
            ]
        )
    ]

    return True, bbox, children


if __name__ == "__main__":
    app.run(debug=True)
