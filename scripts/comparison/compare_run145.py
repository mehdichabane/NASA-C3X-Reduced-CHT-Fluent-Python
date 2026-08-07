"""Compare SST and Transition SST wall results with NASA C3X Run 145 measurements."""

from pathlib import Path

import matplotlib.pyplot as plt

plt.rcParams["svg.hashsalt"] = "nasa-c3x-run145"
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "results/processed/mesh_sensitivity"
NASA_DIR = ROOT / "references/experimental_data"
OUTPUT_DIR = ROOT / "results/processed/nasa_comparison"
FIGURE_DIR = ROOT / "results/figures/nasa_comparison"

NASA_PRESSURE = NASA_DIR / "run145_4512_pressure.csv"
NASA_THERMAL = NASA_DIR / "run145_4512_heat_transfer_temperature.csv"
NASA_UNCERTAINTY = NASA_DIR / "c3x_heat_transfer_uncertainty_table_VI.csv"
CFD_FILES = {
    "SST": DATA_DIR / "run145_sst_comparison_profile.csv",
    "Transition SST": DATA_DIR / "run145_transition_sst_comparison_profile.csv",
}

ENDPOINT_TOLERANCE = 1e-3
NASA_TREF_K = 811.0
NASA_HTC_REF_W_M2K = 1135.0

def read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path, skipinitialspace=True)
    frame.columns = frame.columns.astype(str).str.strip()
    aliases = {
        "wall_temperature_K": "wall-temperature",
        "heat_flux_W_m2": "heat-flux",
    }
    frame = frame.rename(columns={key: value for key, value in aliases.items() if key in frame.columns and value not in frame.columns})
    if "surface" in frame.columns:
        frame["surface"] = frame["surface"].astype(str).str.strip().str.lower()
    return frame


def require_columns(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = columns - set(frame.columns)
    if missing:
        raise ValueError(f"{label}: missing columns {sorted(missing)}")


def cfd_profile(frame: pd.DataFrame, surface: str) -> pd.DataFrame:
    require_columns(
        frame,
        {"surface", "x_over_c", "ps_over_pt", "wall-temperature", "heat-flux"},
        "CFD file",
    )
    group = frame.loc[frame["surface"] == surface].copy()
    if group.empty:
        raise ValueError(f"No CFD values found on the {surface} side.")

    numeric = ["x_over_c", "ps_over_pt", "wall-temperature", "heat-flux"]
    group[numeric] = group[numeric].apply(pd.to_numeric, errors="raise")
    group["x_key"] = group["x_over_c"].round(12)
    profile = (
        group.groupby("x_key", as_index=False)
        .agg(
            x_over_c=("x_over_c", "mean"),
            ps_over_pt=("ps_over_pt", "mean"),
            wall_temperature_K=("wall-temperature", "mean"),
            heat_flux_W_m2=("heat-flux", "mean"),
        )
        .sort_values("x_over_c")
        .reset_index(drop=True)
    )
    if np.any(np.diff(profile["x_over_c"].to_numpy(float)) <= 0):
        raise ValueError(f"Non-increasing x/Cx values on the {surface} side.")
    return profile


def interpolate(profile: pd.DataFrame, target: np.ndarray, column: str) -> np.ndarray:
    source = profile["x_over_c"].to_numpy(float)
    lower_gap = max(0.0, float(source.min() - target.min()))
    upper_gap = max(0.0, float(target.max() - source.max()))
    if lower_gap > ENDPOINT_TOLERANCE or upper_gap > ENDPOINT_TOLERANCE:
        raise ValueError(
            f"NASA stations fall outside the CFD x/Cx range for {column}: "
            f"NASA=[{target.min():.4f}, {target.max():.4f}], "
            f"CFD=[{source.min():.4f}, {source.max():.4f}]"
        )
    clipped = np.clip(target, source.min(), source.max())
    return np.interp(clipped, source, profile[column])


def error_metrics(experimental: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    error = predicted - experimental
    absolute = np.abs(error)
    return {
        "mean_bias": float(error.mean()),
        "mae": float(absolute.mean()),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "max_abs_error": float(absolute.max()),
        "mape_percent": float(
            np.mean(absolute / np.maximum(np.abs(experimental), 1e-30)) * 100
        ),
    }


def station_uncertainty(surface: str, s_over_arc: float, table: pd.DataFrame) -> float:
    group = table.loc[table["surface"] == surface].sort_values("arc_start_percent")
    position = 100.0 * float(s_over_arc)
    exact_start = group.loc[
        np.isclose(position, group["arc_start_percent"], atol=1e-12)
    ]
    if not exact_start.empty:
        return float(exact_start.iloc[0]["uncertainty_percent"])
    match = group.loc[
        (position >= group["arc_start_percent"])
        & (position <= group["arc_end_percent"] + 1e-12)
    ]
    if match.empty:
        raise ValueError(f"No uncertainty interval for {surface}, s/L={s_over_arc:.4f}")
    return float(match.iloc[0]["uncertainty_percent"])


def pressure_comparison(
    nasa: pd.DataFrame,
    profiles: dict[tuple[str, str], pd.DataFrame],
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    require_columns(
        nasa,
        {"surface", "x_over_axial_chord", "PS_over_PT"},
        "NASA pressure",
    )
    pointwise: list[pd.DataFrame] = []
    summary: list[dict[str, object]] = []

    for model in CFD_FILES:
        for surface in ("pressure", "suction"):
            experimental = (
                nasa.loc[nasa["surface"] == surface]
                .sort_values("x_over_axial_chord")
                .copy()
            )
            target = experimental["x_over_axial_chord"].to_numpy(float)
            predicted = interpolate(profiles[(model, surface)], target, "ps_over_pt")
            experimental["model"] = model
            experimental["cfd_ps_over_pt"] = predicted
            experimental["error"] = predicted - experimental["PS_over_PT"]
            pointwise.append(experimental)
            summary.append(
                {
                    "model": model,
                    "surface": surface,
                    "quantity": "pressure ratio",
                    "units": "-",
                    "points": len(experimental),
                    **error_metrics(
                        experimental["PS_over_PT"].to_numpy(float), predicted
                    ),
                    "inside_experimental_htc_interval_percent": np.nan,
                }
            )

    return pd.concat(pointwise, ignore_index=True), summary


def thermal_comparison(
    nasa: pd.DataFrame,
    uncertainty: pd.DataFrame,
    profiles: dict[tuple[str, str], pd.DataFrame],
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    require_columns(
        nasa,
        {
            "surface",
            "s_over_arc",
            "x_over_axial_chord",
            "T_norm",
            "T_wall_K",
            "h_norm",
            "h_W_m2K",
        },
        "NASA thermal",
    )
    require_columns(
        uncertainty,
        {"surface", "arc_start_percent", "arc_end_percent", "uncertainty_percent"},
        "NASA uncertainty",
    )

    reconstructed_temperature = nasa["T_norm"].to_numpy(float) * NASA_TREF_K
    reconstructed_htc = nasa["h_norm"].to_numpy(float) * NASA_HTC_REF_W_M2K
    if not np.allclose(reconstructed_temperature, nasa["T_wall_K"], atol=1.1e-3):
        raise ValueError("NASA wall-temperature dimensionalization is inconsistent.")
    if not np.allclose(reconstructed_htc, nasa["h_W_m2K"], atol=1.1e-3):
        raise ValueError("NASA HTC dimensionalization is inconsistent.")
    pointwise: list[pd.DataFrame] = []
    summary: list[dict[str, object]] = []

    for model in CFD_FILES:
        for surface in ("pressure", "suction"):
            experimental = (
                nasa.loc[nasa["surface"] == surface]
                .sort_values("x_over_axial_chord")
                .copy()
            )
            target = experimental["x_over_axial_chord"].to_numpy(float)
            profile = profiles[(model, surface)]
            wall_temperature = interpolate(profile, target, "wall_temperature_K")
            raw_heat_flux = interpolate(profile, target, "heat_flux_W_m2")
            htc = -raw_heat_flux / (NASA_TREF_K - wall_temperature)

            experimental["model"] = model
            experimental["cfd_wall_temperature_K"] = wall_temperature
            experimental["cfd_htc_W_m2K"] = htc
            experimental["wall_temperature_error_K"] = (
                wall_temperature - experimental["T_wall_K"]
            )
            experimental["htc_error_W_m2K"] = htc - experimental["h_W_m2K"]
            experimental["htc_uncertainty_percent"] = [
                station_uncertainty(surface, station, uncertainty)
                for station in experimental["s_over_arc"]
            ]
            lower = experimental["h_W_m2K"] * (
                1 - experimental["htc_uncertainty_percent"] / 100
            )
            upper = experimental["h_W_m2K"] * (
                1 + experimental["htc_uncertainty_percent"] / 100
            )
            experimental["htc_inside_experimental_interval"] = (
                (htc >= lower) & (htc <= upper)
            )
            pointwise.append(experimental)

            quantities = (
                (
                    "wall temperature",
                    "K",
                    experimental["T_wall_K"].to_numpy(float),
                    wall_temperature,
                ),
                (
                    "heat-transfer coefficient",
                    "W/m2/K",
                    experimental["h_W_m2K"].to_numpy(float),
                    htc,
                ),
            )
            for quantity, units, reference, prediction in quantities:
                row: dict[str, object] = {
                    "model": model,
                    "surface": surface,
                    "quantity": quantity,
                    "units": units,
                    "points": len(experimental),
                    **error_metrics(reference, prediction),
                    "inside_experimental_htc_interval_percent": np.nan,
                }
                if quantity == "heat-transfer coefficient":
                    row["inside_experimental_htc_interval_percent"] = float(
                        experimental["htc_inside_experimental_interval"].mean() * 100
                    )
                summary.append(row)

    return pd.concat(pointwise, ignore_index=True), summary


def signed_coordinate(values: pd.Series, surface: str) -> np.ndarray:
    sign = -1.0 if surface == "pressure" else 1.0
    return sign * values.to_numpy(float)


def profile_over_experimental_range(
    profile: pd.DataFrame, experimental_x: pd.Series
) -> pd.DataFrame:
    lower = float(experimental_x.min())
    upper = float(experimental_x.max())
    return profile.loc[
        (profile["x_over_c"] >= lower) & (profile["x_over_c"] <= upper)
    ].copy()


def ordered_legend(
    axis: plt.Axes,
    *,
    loc: str = "best",
    bbox_to_anchor: tuple[float, float] | None = None,
    ncol: int = 1,
) -> None:
    handles, labels = axis.get_legend_handles_labels()
    order = [labels.index(label) for label in ("NASA Run 145", "SST", "Transition SST")]
    axis.legend(
        [handles[index] for index in order],
        [labels[index] for index in order],
        frameon=False,
        loc=loc,
        bbox_to_anchor=bbox_to_anchor,
        ncol=ncol,
    )


def prepare_axis(axis: plt.Axes, ylabel: str) -> None:
    axis.set_xlabel(r"Signed axial coordinate $x/C_x$")
    axis.set_ylabel(ylabel)
    axis.axvline(0.0, linestyle=":", linewidth=0.9, color="0.55")
    axis.grid(axis="y", linewidth=0.6, alpha=0.22)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.margins(x=0.02)
    axis.text(
        0.25, 1.015, r"Pressure side  ($x/C_x<0$)",
        transform=axis.transAxes, ha="center", va="bottom",
        fontsize=8.5, color="0.25",
    )
    axis.text(
        0.75, 1.015, r"Suction side  ($x/C_x>0$)",
        transform=axis.transAxes, ha="center", va="bottom",
        fontsize=8.5, color="0.25",
    )


def save_figure(figure: plt.Figure, stem: str) -> None:
    figure.savefig(FIGURE_DIR / f"{stem}.svg", metadata={"Date": None})
    plt.close(figure)


def plot_pressure_ratio(
    nasa: pd.DataFrame,
    profiles: dict[tuple[str, str], pd.DataFrame],
) -> None:
    figure, axis = plt.subplots(figsize=(7.2, 4.4), layout="constrained")
    cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    for surface in ("pressure", "suction"):
        experimental = nasa.loc[nasa["surface"] == surface].sort_values(
            "x_over_axial_chord"
        )
        axis.scatter(
            signed_coordinate(experimental["x_over_axial_chord"], surface),
            experimental["PS_over_PT"],
            s=28,
            marker="o",
            facecolors="white",
            edgecolors=cycle[0],
            linewidths=1.2,
            label="NASA Run 145" if surface == "pressure" else None,
            zorder=3,
        )

    styles = {"SST": "-", "Transition SST": "--"}
    for model_index, model in enumerate(CFD_FILES, start=1):
        for surface in ("pressure", "suction"):
            experimental_x = nasa.loc[
                nasa["surface"] == surface, "x_over_axial_chord"
            ]
            profile = profile_over_experimental_range(
                profiles[(model, surface)], experimental_x
            )
            x = signed_coordinate(profile["x_over_c"], surface)
            order = np.argsort(x)
            axis.plot(
                x[order],
                profile["ps_over_pt"].to_numpy(float)[order],
                linestyle=styles[model],
                linewidth=1.8 if model == "SST" else 1.35,
                alpha=1.0 if model == "SST" else 0.82,
                color=cycle[model_index],
                label=model if surface == "pressure" else None,
            )

    prepare_axis(axis, r"Static-pressure ratio $p_s/p_{t,\mathrm{in}}$")
    axis.set_xlim(-1.02, 1.02)
    axis.set_ylim(0.48, 1.015)
    ordered_legend(axis)
    save_figure(figure, "pressure_ratio")


def plot_wall_temperature(
    nasa: pd.DataFrame,
    profiles: dict[tuple[str, str], pd.DataFrame],
) -> None:
    figure, axis = plt.subplots(figsize=(7.2, 4.4), layout="constrained")
    cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    for surface in ("pressure", "suction"):
        experimental = nasa.loc[nasa["surface"] == surface].sort_values(
            "x_over_axial_chord"
        )
        axis.scatter(
            signed_coordinate(experimental["x_over_axial_chord"], surface),
            experimental["T_wall_K"],
            s=28,
            marker="o",
            facecolors="white",
            edgecolors=cycle[0],
            linewidths=1.2,
            label="NASA Run 145" if surface == "pressure" else None,
            zorder=3,
        )

    styles = {"SST": "-", "Transition SST": "--"}
    for model_index, model in enumerate(CFD_FILES, start=1):
        for surface in ("pressure", "suction"):
            experimental_x = nasa.loc[
                nasa["surface"] == surface, "x_over_axial_chord"
            ]
            profile = profile_over_experimental_range(
                profiles[(model, surface)], experimental_x
            )
            x = signed_coordinate(profile["x_over_c"], surface)
            order = np.argsort(x)
            axis.plot(
                x[order],
                profile["wall_temperature_K"].to_numpy(float)[order],
                linestyle=styles[model],
                linewidth=1.8 if model == "SST" else 1.35,
                alpha=1.0 if model == "SST" else 0.82,
                color=cycle[model_index],
                label=model if surface == "pressure" else None,
            )

    prepare_axis(axis, r"Wall temperature $T_w$ [K]")
    axis.set_xlim(-1.02, 1.02)
    ordered_legend(
        axis,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
        ncol=3,
    )
    save_figure(figure, "wall_temperature")


def plot_heat_transfer_coefficient(
    nasa: pd.DataFrame,
    uncertainty: pd.DataFrame,
    profiles: dict[tuple[str, str], pd.DataFrame],
) -> None:
    figure, axis = plt.subplots(figsize=(7.2, 4.4), layout="constrained")
    cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for surface in ("pressure", "suction"):
        experimental = nasa.loc[nasa["surface"] == surface].sort_values(
            "x_over_axial_chord"
        )
        uncertainty_percent = np.array(
            [
                station_uncertainty(surface, station, uncertainty)
                for station in experimental["s_over_arc"]
            ]
        )
        y = experimental["h_W_m2K"].to_numpy(float)
        axis.errorbar(
            signed_coordinate(experimental["x_over_axial_chord"], surface),
            y,
            yerr=y * uncertainty_percent / 100.0,
            fmt="o",
            markersize=4.8,
            markerfacecolor="white",
            markeredgecolor=cycle[0],
            markeredgewidth=1.1,
            ecolor=cycle[0],
            elinewidth=0.7,
            capsize=1.8,
            label="NASA Run 145" if surface == "pressure" else None,
            zorder=3,
        )

    styles = {"SST": "-", "Transition SST": "--"}
    for model_index, model in enumerate(CFD_FILES, start=1):
        for surface in ("pressure", "suction"):
            experimental_x = nasa.loc[
                nasa["surface"] == surface, "x_over_axial_chord"
            ]
            profile = profile_over_experimental_range(
                profiles[(model, surface)], experimental_x
            )
            wall_temperature = profile["wall_temperature_K"].to_numpy(float)
            htc = -profile["heat_flux_W_m2"].to_numpy(float) / (
                NASA_TREF_K - wall_temperature
            )
            x = signed_coordinate(profile["x_over_c"], surface)
            order = np.argsort(x)
            axis.plot(
                x[order],
                htc[order],
                linestyle=styles[model],
                linewidth=1.8 if model == "SST" else 1.35,
                alpha=1.0 if model == "SST" else 0.82,
                color=cycle[model_index],
                label=model if surface == "pressure" else None,
            )

    prepare_axis(axis, r"Heat-transfer coefficient $h$ [W m$^{-2}$ K$^{-1}$]")
    axis.set_xlim(-1.02, 1.02)
    axis.set_ylim(bottom=0.0)
    ordered_legend(axis)
    save_figure(figure, "heat_transfer_coefficient")



def main() -> None:
    nasa_pressure = read_csv(NASA_PRESSURE)
    nasa_thermal = read_csv(NASA_THERMAL)
    uncertainty = read_csv(NASA_UNCERTAINTY)
    profiles: dict[tuple[str, str], pd.DataFrame] = {}

    for model, path in CFD_FILES.items():
        cfd = read_csv(path)
        for surface in ("pressure", "suction"):
            profiles[(model, surface)] = cfd_profile(cfd, surface)

    pressure, pressure_summary = pressure_comparison(nasa_pressure, profiles)
    thermal, thermal_summary = thermal_comparison(nasa_thermal, uncertainty, profiles)
    summary = pd.DataFrame(pressure_summary + thermal_summary)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    pressure.to_csv(OUTPUT_DIR / "run145_pressure_pointwise.csv", index=False)
    thermal.to_csv(OUTPUT_DIR / "run145_thermal_pointwise.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "run145_comparison_summary.csv", index=False)

    for old_figure in FIGURE_DIR.glob("*.png"):
        old_figure.unlink()
    for old_figure in FIGURE_DIR.glob("*.svg"):
        old_figure.unlink()

    plot_pressure_ratio(nasa_pressure, profiles)
    plot_wall_temperature(nasa_thermal, profiles)
    plot_heat_transfer_coefficient(nasa_thermal, uncertainty, profiles)

    compact = summary[["model", "surface", "quantity", "mae", "mape_percent"]]
    print(compact.to_string(index=False, float_format=lambda value: f"{value:.5g}"))


if __name__ == "__main__":
    main()
