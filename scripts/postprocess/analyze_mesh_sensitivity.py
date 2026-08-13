"""Build the three-grid wall-profile and global mesh-sensitivity results."""

from __future__ import annotations

from pathlib import Path
import math

import matplotlib.pyplot as plt

plt.rcParams["svg.hashsalt"] = "nasa-c3x-run145"
import numpy as np
import pandas as pd
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = ROOT / "data/fluent_exports/mesh_sensitivity"
GEOMETRY_FILE = ROOT / "geometry/raw/c3x_vane_profile_table3_xy_cm.csv"
OUTPUT_DIR = ROOT / "results/processed/mesh_sensitivity"
FIGURE_DIR = ROOT / "results/figures/mesh_sensitivity"

MESHES = ("coarse", "medium", "fine")
CELL_COUNTS = {"coarse": 14_657, "medium": 23_781, "fine": 44_760}
PT_INLET_PA = 403_800.0
NASA_REFERENCE_TEMPERATURE_K = 811.0
AXIAL_CHORD_M = 0.078161
COMMON_POINTS = 501

RAW_COLUMNS = {
    "cellnumber",
    "x-coordinate",
    "y-coordinate",
    "pressure",
    "temperature",
    "y-plus",
    "heat-flux",
    "face-area-magnitude",
}

PROFILE_QUANTITIES = (
    "ps_over_pt",
    "wall_temperature_K",
    "heat_flux_into_vane_W_m2",
    "htc_nasa_W_m2K",
    "wall_yplus",
)


def read_wall_export(mesh: str) -> pd.DataFrame:
    path = EXPORT_DIR / f"run145_sst_{mesh}_wall.csv"
    frame = pd.read_csv(path, skipinitialspace=True)
    frame.columns = [column.strip() for column in frame.columns]
    missing = RAW_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name}: missing columns {sorted(missing)}")
    if "nodenumber" in frame.columns:
        raise ValueError(f"{path.name}: expected a Cell Center export, found nodal data")
    return frame


def prepare_reference_surfaces() -> dict[str, np.ndarray]:
    profile = pd.read_csv(GEOMETRY_FILE)

    suction = profile.loc[profile["surface"] == "suction", ["x_cm", "y_cm"]].to_numpy(float)
    if np.allclose(suction[0], suction[-1]):
        suction = suction[:-1]

    pressure = profile.loc[profile["surface"] == "pressure", ["x_cm", "y_cm"]].to_numpy(float)
    pressure = pressure[::-1]

    return {
        "pressure": pressure * 0.01,
        "suction": suction * 0.01,
    }


def project_point_to_polyline(point: np.ndarray, polyline: np.ndarray) -> tuple[float, float]:
    starts = polyline[:-1]
    vectors = polyline[1:] - starts
    squared_lengths = np.einsum("ij,ij->i", vectors, vectors)
    parameters = np.einsum("ij,ij->i", point - starts, vectors) / squared_lengths
    parameters = np.clip(parameters, 0.0, 1.0)
    projections = starts + parameters[:, None] * vectors
    distances = np.linalg.norm(point - projections, axis=1)
    segment = int(np.argmin(distances))

    lengths = np.linalg.norm(vectors, axis=1)
    cumulative = np.concatenate(([0.0], np.cumsum(lengths)))
    arc_length = cumulative[segment] + parameters[segment] * lengths[segment]
    return float(distances[segment]), float(arc_length / cumulative[-1])


def map_wall_export(frame: pd.DataFrame, reference: dict[str, np.ndarray]) -> pd.DataFrame:
    mapped = frame.copy()
    surfaces: list[str] = []
    normalized_arc: list[float] = []
    mapping_distance: list[float] = []

    points = mapped[["x-coordinate", "y-coordinate"]].to_numpy(float)
    for point in points:
        candidates = {
            surface: project_point_to_polyline(point, polyline)
            for surface, polyline in reference.items()
        }
        surface = min(candidates, key=lambda name: candidates[name][0])
        distance, s_over_l = candidates[surface]
        surfaces.append(surface)
        normalized_arc.append(s_over_l)
        mapping_distance.append(distance)

    mapped["surface"] = surfaces
    mapped["s_over_l"] = normalized_arc
    mapped["mapping_distance_m"] = mapping_distance
    mapped["x_over_c"] = mapped["x-coordinate"] / AXIAL_CHORD_M
    mapped["signed_x_over_c"] = np.where(
        mapped["surface"].eq("pressure"), -mapped["x_over_c"], mapped["x_over_c"]
    )
    mapped["ps_over_pt"] = mapped["pressure"] / PT_INLET_PA
    mapped["wall_temperature_K"] = mapped["temperature"]
    mapped["wall_yplus"] = mapped["y-plus"]
    mapped["heat_flux_into_vane_W_m2"] = -mapped["heat-flux"]
    temperature_difference = NASA_REFERENCE_TEMPERATURE_K - mapped["wall_temperature_K"]
    mapped["htc_nasa_W_m2K"] = mapped["heat_flux_into_vane_W_m2"] / temperature_difference

    return mapped.sort_values(["surface", "s_over_l"]).reset_index(drop=True)


def make_common_profiles(mapped: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    grid = np.linspace(0.0, 1.0, COMMON_POINTS)

    for surface in ("pressure", "suction"):
        common = pd.DataFrame({"surface": surface, "s_over_l": grid})
        for mesh in MESHES:
            source = mapped[mesh].loc[mapped[mesh]["surface"] == surface].sort_values("s_over_l")
            source = source.drop_duplicates("s_over_l")
            for quantity in PROFILE_QUANTITIES:
                common[f"{mesh}_{quantity}"] = np.interp(
                    grid,
                    source["s_over_l"].to_numpy(float),
                    source[quantity].to_numpy(float),
                )
        rows.append(common)

    return pd.concat(rows, ignore_index=True)


def normalized_mae(reference: np.ndarray, comparison: np.ndarray) -> float:
    scale = float(np.ptp(reference))
    if scale == 0.0:
        scale = max(abs(float(np.mean(reference))), 1.0)
    return float(np.mean(np.abs(comparison - reference)) / scale * 100.0)


def summarize_local_profiles(common: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for surface in ("pressure", "suction"):
        surface_data = common.loc[common["surface"] == surface]
        for region, mask in {
            "full_surface": np.ones(len(surface_data), dtype=bool),
            "core_1_to_99_percent": surface_data["s_over_l"].between(0.01, 0.99).to_numpy(),
            "trailing_edge_last_5_percent": (surface_data["s_over_l"] >= 0.95).to_numpy(),
        }.items():
            subset = surface_data.loc[mask]
            for quantity in PROFILE_QUANTITIES:
                fine = subset[f"fine_{quantity}"].to_numpy(float)
                for comparison_mesh in ("coarse", "medium"):
                    comparison = subset[f"{comparison_mesh}_{quantity}"].to_numpy(float)
                    difference = comparison - fine
                    rows.append(
                        {
                            "comparison": f"{comparison_mesh}_vs_fine",
                            "quantity": quantity,
                            "surface": surface,
                            "region": region,
                            "mae": float(np.mean(np.abs(difference))),
                            "rmse": float(np.sqrt(np.mean(difference**2))),
                            "maximum_absolute_difference": float(np.max(np.abs(difference))),
                            "normalized_mae_percent": normalized_mae(fine, comparison),
                        }
                    )
    return pd.DataFrame(rows)


def observed_order(phi_fine: float, phi_medium: float, phi_coarse: float, r21: float, r32: float) -> float:
    epsilon21 = phi_medium - phi_fine
    epsilon32 = phi_coarse - phi_medium
    if epsilon21 == 0.0 or epsilon32 == 0.0 or epsilon21 * epsilon32 <= 0.0:
        return math.nan

    sign = 1.0

    def residual(order: float) -> float:
        numerator = r21**order - sign
        denominator = r32**order - sign
        if numerator <= 0.0 or denominator <= 0.0:
            return math.nan
        right_side = abs(
            math.log(abs(epsilon32 / epsilon21)) + math.log(numerator / denominator)
        ) / math.log(r21)
        return order - right_side

    samples = np.linspace(0.01, 20.0, 4000)
    for lower, upper in zip(samples[:-1], samples[1:]):
        try:
            f_lower = residual(float(lower))
            f_upper = residual(float(upper))
            if np.isfinite(f_lower) and np.isfinite(f_upper) and f_lower * f_upper < 0.0:
                return float(brentq(residual, float(lower), float(upper)))
        except (ValueError, ZeroDivisionError):
            continue
    return math.nan


def build_global_metrics(global_data: pd.DataFrame) -> pd.DataFrame:
    indexed = global_data.set_index("mesh")
    h = {mesh: 1.0 / math.sqrt(float(indexed.loc[mesh, "fluent_cells"])) for mesh in MESHES}
    r21 = h["medium"] / h["fine"]
    r32 = h["coarse"] / h["medium"]

    quantities = {
        "outlet_mach": "-",
        "mean_wall_temperature_K": "K",
        "external_heat_rate_W_per_m": "W/m",
    }
    rows: list[dict[str, float | str | bool]] = []

    for quantity, unit in quantities.items():
        fine = float(indexed.loc["fine", quantity])
        medium = float(indexed.loc["medium", quantity])
        coarse = float(indexed.loc["coarse", quantity])
        order = observed_order(fine, medium, coarse, r21, r32)
        monotonic = (coarse < medium < fine) or (coarse > medium > fine)

        extrapolated = math.nan
        gci_fine_medium = math.nan
        asymptotic_ratio = math.nan
        if monotonic and np.isfinite(order):
            extrapolated = (r21**order * fine - medium) / (r21**order - 1.0)
            approximate_error21 = abs((fine - medium) / fine)
            approximate_error32 = abs((medium - coarse) / medium)
            safety_factor = 1.25
            gci_fine_medium = safety_factor * approximate_error21 / (r21**order - 1.0) * 100.0
            gci_medium_coarse = safety_factor * approximate_error32 / (r32**order - 1.0) * 100.0
            asymptotic_ratio = gci_medium_coarse / (r21**order * gci_fine_medium)

        rows.append(
            {
                "quantity": quantity,
                "unit": unit,
                "coarse": coarse,
                "medium": medium,
                "fine": fine,
                "medium_to_fine_change_percent": abs((fine - medium) / fine) * 100.0,
                "coarse_to_fine_change_percent": abs((fine - coarse) / fine) * 100.0,
                "monotonic_sequence": monotonic,
                "r_fine_medium": r21,
                "r_medium_coarse": r32,
                "observed_order": order,
                "richardson_extrapolated": extrapolated,
                "gci_fine_medium_percent": gci_fine_medium,
                "asymptotic_ratio": asymptotic_ratio,
                "gci_status": "screening",
            }
        )
    return pd.DataFrame(rows)


def plot_global(global_data: pd.DataFrame) -> None:
    indexed = global_data.set_index("mesh").loc[list(MESHES)]
    x = np.arange(len(MESHES))
    labels = [f"{name.capitalize()}\n{int(indexed.loc[name, 'fluent_cells']):,} cells" for name in MESHES]

    figure, axes = plt.subplots(1, 3, figsize=(11.6, 3.5), sharey=True, layout="constrained")
    panels = (
        ("outlet_mach", "Outlet Mach"),
        ("mean_wall_temperature_K", "Mean wall temperature"),
        ("external_heat_rate_W_per_m", "External heat-transfer rate"),
    )
    for axis, (quantity, title) in zip(axes, panels):
        values = indexed[quantity].to_numpy(float)
        fine = values[-1]
        relative = 100.0 * (values - fine) / abs(fine)
        axis.plot(x, relative, marker="o", linewidth=1.4)
        axis.axhline(0.0, linewidth=0.8, color="0.45")
        axis.set_xticks(x, labels)
        axis.set_title(title)
        axis.grid(axis="y", linewidth=0.6, alpha=0.22)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        for xpos, value in zip(x, relative):
            axis.annotate(
                f"{value:+.3f}%",
                xy=(xpos, value),
                xytext=(0, 7),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    axes[0].set_ylabel("Signed difference from fine-grid value [%]")
    figure.savefig(FIGURE_DIR / "run145_three_grid_global_sensitivity.svg", metadata={"Date": None})
    plt.close(figure)


def plot_profiles(common: pd.DataFrame) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(10.6, 7.0), sharex=True, layout="constrained")
    panels = (
        ("ps_over_pt", r"$p_s/p_{t,\mathrm{in}}$", 1.0),
        ("wall_temperature_K", "Wall temperature [K]", 1.0),
        ("heat_flux_into_vane_W_m2", r"Heat flux into vane [kW/m$^2$]", 1.0 / 1000.0),
        ("htc_nasa_W_m2K", r"HTC, $T_{\mathrm{ref}}=811$ K [W m$^{-2}$ K$^{-1}$]", 1.0),
    )
    styles = {"coarse": ":", "medium": "--", "fine": "-"}
    widths = {"coarse": 1.35, "medium": 1.35, "fine": 1.6}
    colors = {"coarse": "C0", "medium": "C1", "fine": "C2"}
    markers = {"coarse": "o", "medium": "s", "fine": None}
    zorders = {"fine": 1, "medium": 2, "coarse": 3}
    pressure = common.loc[common["surface"] == "pressure"]
    suction = common.loc[common["surface"] == "suction"]

    # Draw the fine result first so the nearly coincident coarse and medium
    # curves remain visible rather than being hidden underneath it.
    for axis, (quantity, ylabel, scale) in zip(axes.flat, panels):
        for mesh in ("fine", "medium", "coarse"):
            plot_args = {
                "linestyle": styles[mesh],
                "linewidth": widths[mesh],
                "color": colors[mesh],
                "marker": markers[mesh],
                "markevery": 70,
                "markersize": 3.0,
                "markerfacecolor": "white",
                "zorder": zorders[mesh],
            }
            axis.plot(
                -pressure["s_over_l"],
                pressure[f"{mesh}_{quantity}"] * scale,
                label=f"{mesh.capitalize()} ({CELL_COUNTS[mesh]:,} cells)",
                **plot_args,
            )
            axis.plot(
                suction["s_over_l"],
                suction[f"{mesh}_{quantity}"] * scale,
                **plot_args,
            )
        axis.axvline(0.0, linewidth=0.8, color="0.55")
        axis.set_ylabel(ylabel)
        axis.grid(axis="y", linewidth=0.6, alpha=0.22)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)

    xlabel = r"Normalized surface distance $s^*$: pressure side ($-$), suction side ($+$)"
    axes[1, 0].set_xlabel(xlabel)
    axes[1, 1].set_xlabel(xlabel)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    order = [labels.index("Coarse (14,657 cells)"), labels.index("Medium (23,781 cells)"), labels.index("Fine (44,760 cells)")]
    axes[0, 0].legend([handles[index] for index in order], [labels[index] for index in order], frameon=False)
    figure.savefig(FIGURE_DIR / "run145_three_grid_wall_profiles.svg", metadata={"Date": None})
    plt.close(figure)

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    reference = prepare_reference_surfaces()
    mapped: dict[str, pd.DataFrame] = {}
    for mesh in MESHES:
        mapped[mesh] = map_wall_export(read_wall_export(mesh), reference)
        mapped[mesh].to_csv(OUTPUT_DIR / f"run145_sst_{mesh}_wall_mapped.csv", index=False)

    common = make_common_profiles(mapped)
    common.to_csv(OUTPUT_DIR / "run145_three_grid_common_surface_profiles.csv", index=False)

    local_summary = summarize_local_profiles(common)
    local_summary.to_csv(OUTPUT_DIR / "run145_three_grid_local_profile_summary.csv", index=False)

    global_data = pd.read_csv(EXPORT_DIR / "mesh_global_monitors.csv")
    global_metrics = build_global_metrics(global_data)
    global_metrics.to_csv(OUTPUT_DIR / "run145_three_grid_global_metrics.csv", index=False)

    plot_global(global_data)
    plot_profiles(common)

    print("Three-grid wall exports")
    for mesh in MESHES:
        frame = mapped[mesh]
        heat_rate = float((frame["heat-flux"] * frame["face-area-magnitude"]).sum())
        wall_temperature = float(
            np.average(frame["wall_temperature_K"], weights=frame["face-area-magnitude"])
        )
        print(
            f"{mesh:>6}: {len(frame):4d} faces, "
            f"Twall={wall_temperature:.6f} K, "
            f"Q={heat_rate / 1000.0:.6f} kW/m, "
            f"y+max={frame['wall_yplus'].max():.6f}"
        )

    print("\nGlobal medium-to-fine changes")
    print(
        global_metrics[["quantity", "medium_to_fine_change_percent", "observed_order"]]
        .to_string(index=False, float_format=lambda value: f"{value:.6f}")
    )


if __name__ == "__main__":
    main()
