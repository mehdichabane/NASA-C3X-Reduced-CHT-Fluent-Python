"""Plot mesh-quality threshold counts and worst-cell locations."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

plt.rcParams["svg.hashsalt"] = "nasa-c3x-run145"
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/fluent_exports/mesh_sensitivity/mesh_quality_distribution_all_grids.csv"
OUTPUT_DIR = ROOT / "results/figures/mesh"
MESH_ORDER = ["coarse", "medium", "fine"]


def zone_label(raw: str) -> str:
    if "fluid_hot_gas" in raw:
        return "hot-gas fluid"
    if "solid_vane" in raw:
        return "solid vane"
    return raw


def count_percent(row: pd.Series, prefix: str) -> str:
    count = int(row[f"{prefix}_count"])
    percent = float(row[f"{prefix}_percent"])
    return f"{count:,}\n({percent:.3f}%)"


def location(row: pd.Series, prefix: str, value_format: str) -> str:
    value = float(row[prefix])
    cell = int(row[f"{prefix}_cell"])
    x_mm = 1000.0 * float(row[f"{prefix}_x_m"])
    y_mm = 1000.0 * float(row[f"{prefix}_y_m"])
    zone = zone_label(str(row[f"{prefix}_zone"]))
    return f"{value:{value_format}}\ncell {cell:,}; ({x_mm:.2f}, {y_mm:.2f}) mm\n{zone}"


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    data = pd.read_csv(SOURCE).set_index("mesh").loc[MESH_ORDER].reset_index()

    threshold_rows = [
        [
            str(row["mesh"]).title(),
            f"{int(row['cells']):,}",
            count_percent(row, "orthogonal_quality_below_0p1"),
            count_percent(row, "skewness_above_0p75"),
            count_percent(row, "aspect_ratio_above_100"),
            count_percent(row, "aspect_ratio_above_500"),
            count_percent(row, "aspect_ratio_above_1000"),
        ]
        for _, row in data.iterrows()
    ]
    worst_rows = [
        [
            str(row["mesh"]).title(),
            location(row, "minimum_orthogonal_quality", ".6f"),
            location(row, "maximum_equiangle_skewness", ".6f"),
            location(row, "maximum_fluent_aspect_ratio", ".3f"),
        ]
        for _, row in data.iterrows()
    ]

    figure = plt.figure(figsize=(12.0, 6.8))
    top = figure.add_axes([0.035, 0.52, 0.93, 0.40])
    bottom = figure.add_axes([0.035, 0.08, 0.93, 0.34])
    top.axis("off")
    bottom.axis("off")
    top.set_title("Threshold counts", fontsize=11, loc="left", pad=6)
    bottom.set_title("Worst cells (CFF centroid coordinates)", fontsize=11, loc="left", pad=6)

    threshold_table = top.table(
        cellText=threshold_rows,
        colLabels=["Mesh", "Cells", "OQ < 0.10", "Skewness > 0.75", "AR > 100", "AR > 500", "AR > 1000"],
        cellLoc="center",
        colLoc="center",
        loc="center",
        colWidths=[0.10, 0.11, 0.15, 0.16, 0.15, 0.15, 0.15],
    )
    worst_table = bottom.table(
        cellText=worst_rows,
        colLabels=["Mesh", "Minimum orthogonal quality", "Maximum equiangle skewness", "Maximum Fluent aspect ratio"],
        cellLoc="center",
        colLoc="center",
        loc="center",
        colWidths=[0.10, 0.29, 0.29, 0.29],
    )

    for table, fontsize, scale in (
        (threshold_table, 8.5, 2.1),
        (worst_table, 8.1, 2.4),
    ):
        table.auto_set_font_size(False)
        table.set_fontsize(fontsize)
        table.scale(1.0, scale)
        for (row_index, _), cell in table.get_celld().items():
            cell.set_facecolor("0.92" if row_index == 0 else "1.0")
            cell.set_edgecolor("0.72")
            cell.set_linewidth(0.55)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / "run145_mesh_quality_distribution.svg"
    figure.savefig(output, metadata={"Date": None})
    plt.close(figure)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
