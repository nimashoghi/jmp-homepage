import argparse
import tempfile
from pathlib import Path

import ovito
import pandas as pd
from ovito.io import import_file
from ovito.vis import TachyonRenderer, Viewport
from pymatgen.core import Structure
from tqdm import tqdm


def convert(
    *,
    structure: Structure,
    id: str,
    out_dir: Path,
    temp_dir: Path,
    image_size: tuple[int, int] = (500, 500),
    show_unit_cell: bool = False,
):
    # First, convert the structure to a cif file in the temporary directory.
    cif_path = (temp_dir / f"{id}.cif").absolute()
    structure.to_file(str(cif_path), "cif")

    # Next, convert the cif file to a jpeg file using ovito.
    out_path = (out_dir / f"{id}.jpeg").absolute()
    pipeline = import_file(cif_path)
    pipeline.add_to_scene()

    # Hide the unit cell if requested.
    if not show_unit_cell:
        cell_vis = pipeline.source.data.cell.vis
        cell_vis.line_width = 1.3
        cell_vis.enabled = False
        cell_vis.rendering_color = (0.0, 0.1, 0.0)

    # Render the image and save it to the output directory.
    vp = Viewport(type=Viewport.Type.Ortho, camera_dir=(2, 1, -1))
    vp.zoom_all(size=image_size)
    vp.render_image(
        size=image_size,
        filename=str(out_path),
        renderer=TachyonRenderer(),
    )

    # Remove the pipeline from the scene.
    pipeline.remove_from_scene()


PBC_DATASETS = ["MatBench", "OC20", "OC22", "QMOF"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("df", type=Path, help="Path to the dataframe.")
    parser.add_argument("out_dir", type=Path, help="Output directory.")
    parser.add_argument(
        "--flat",
        action=argparse.BooleanOptionalAction,
        help="Flatten the output directory.",
    )
    args = parser.parse_args()

    # Make the temporary directory.
    root_temp_dir = Path(tempfile.mkdtemp())

    # Iterate through each unique dataset in the dataframe and handle each one.
    df = pd.read_pickle(args.df)
    for dataset in tqdm(
        df["dataset"].unique(),
        desc="Rendering",
        leave=True,
        position=0,
    ):
        show_unit_cell = (
            df[df["dataset"] == dataset]["dataset_name"].unique().item() in PBC_DATASETS
        )

        if args.flat:
            dataset_dir = args.out_dir / "flat"
        else:
            dataset_dir = args.out_dir / dataset
        dataset_dir.mkdir(exist_ok=True, parents=True)

        if args.flat:
            dataset_temp_dir = root_temp_dir / "flat"
        else:
            dataset_temp_dir = root_temp_dir / dataset
        dataset_temp_dir.mkdir(exist_ok=True, parents=True)

        dataset_df = df[df["dataset"] == dataset]
        for idx, row in tqdm(
            dataset_df.iterrows(),
            desc=dataset,
            total=len(dataset_df),
            leave=False,
            position=1,
        ):
            structure = row["structure"]
            convert(
                structure=structure,
                id=str(idx),
                out_dir=dataset_dir,
                temp_dir=dataset_temp_dir,
                show_unit_cell=show_unit_cell,
            )


if __name__ == "__main__":
    main()
