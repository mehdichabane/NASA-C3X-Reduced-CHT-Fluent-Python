"""Reconstruct the solid temperature gradient from actual mesh connectivity."""
from pathlib import Path
import sys
import matplotlib.pyplot as plt

plt.rcParams["svg.hashsalt"] = "nasa-c3x-run145"
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.common.gradient_reconstruction import adjacency_dict, reconstruct_gradient

SOURCE = ROOT / "data/fluent_exports/run145_sst_solid_cell_temperature.csv"
ADJACENCY = ROOT / "data/fluent_exports/run145_sst_solid_cell_adjacency.csv"
PROFILE = ROOT / "geometry/raw/c3x_vane_profile_table3_xy_cm.csv"
OUTPUT_DIR = ROOT / "results/processed/solid_temperature"
FIGURE_DIR = ROOT / "results/figures/solid_temperature"


def read_cells(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, skipinitialspace=True)
    frame.columns = frame.columns.astype(str).str.strip()
    required = {"cellnumber", "x-coordinate", "y-coordinate", "temperature"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    for column in required:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    if frame[list(required)].isna().any().any():
        raise ValueError("NaN values found in the solid-cell export")
    if frame["cellnumber"].duplicated().any():
        raise ValueError("Duplicate solid cell numbers found")
    return frame.sort_values("cellnumber").reset_index(drop=True)


def plot_field(frame: pd.DataFrame, profile_path: Path, path: Path) -> None:
    profile = pd.read_csv(profile_path, skipinitialspace=True)
    figure, axis = plt.subplots(figsize=(5.8, 6.8), layout="constrained")
    field = axis.scatter(
        1000.0 * frame["x-coordinate"], 1000.0 * frame["y-coordinate"],
        c=frame["gradient_magnitude_K_m"], s=5.0, marker="s", linewidths=0.0,
        rasterized=True,
    )
    axis.plot(10.0 * profile["x_cm"], 10.0 * profile["y_cm"], linewidth=0.9)
    axis.set_aspect("equal")
    axis.set_xlabel(r"$x$ [mm]")
    axis.set_ylabel(r"$y$ [mm]")
    axis.set_title("Reconstructed solid temperature-gradient magnitude")
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    colorbar = figure.colorbar(field, ax=axis, pad=0.03)
    colorbar.set_label(r"$|\nabla T|$ [K m$^{-1}$]")
    figure.savefig(path.with_suffix(".svg"), metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    frame = read_cells(SOURCE)
    adjacency = adjacency_dict(pd.read_csv(ADJACENCY))
    ids = frame["cellnumber"].to_numpy(int)
    xy = frame[["x-coordinate", "y-coordinate"]].to_numpy(float)
    temperature = frame["temperature"].to_numpy(float)
    gradient, condition, residual, counts, rings = reconstruct_gradient(
        ids, xy, temperature, adjacency
    )
    frame["dT_dx_K_m"] = gradient[:, 0]
    frame["dT_dy_K_m"] = gradient[:, 1]
    frame["gradient_magnitude_K_m"] = np.linalg.norm(gradient, axis=1)
    frame["topology_neighbour_count"] = counts
    frame["topology_ring_depth"] = rings
    frame["fit_condition_number"] = condition
    frame["local_fit_rmse_K"] = residual

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / "run145_sst_temperature_gradient.csv"
    figure_path = FIGURE_DIR / "run145_sst_temperature_gradient.png"
    frame.to_csv(csv_path, index=False)
    plot_field(frame, PROFILE, figure_path)

    values = frame["gradient_magnitude_K_m"].to_numpy(float)
    p05, median, p95 = np.percentile(values, [5, 50, 95])
    print(f"Cells: {len(frame)}")
    print(f"|grad T| [K/m]: p05={p05:.1f}, median={median:.1f}, p95={p95:.1f}")
    print(f"Maximum local condition number: {condition.max():.3f}")
    print(f"95th-percentile local fit RMSE: {np.percentile(residual,95):.4f} K")


if __name__ == "__main__":
    main()
