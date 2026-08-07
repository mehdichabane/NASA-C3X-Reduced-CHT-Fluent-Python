"""Verify and plot the fully archived fine-grid Transition SST sensitivity run."""

from pathlib import Path
import sys

import matplotlib.pyplot as plt

plt.rcParams["svg.hashsalt"] = "nasa-c3x-run145"
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TRANSITION_DIR = ROOT / "data/fluent_exports/transition_sst"
MONITORS_SOURCE = TRANSITION_DIR / "run145_transition_sst_convergence_monitors.csv"
RESIDUALS_SOURCE = TRANSITION_DIR / "run145_transition_sst_residuals_full.csv"
WALL_SOURCE = TRANSITION_DIR / "run145_transition_sst_fine_wall_direct_fluent_iter556.csv"
CHECKS_SOURCE = TRANSITION_DIR / "run145_transition_sst_global_checks.csv"
PROCESSED_CONVERGENCE = ROOT / "results/processed/convergence"
PROCESSED_VERIFICATION = ROOT / "results/processed/verification"
FIGURE_CONVERGENCE = ROOT / "results/figures/convergence"

FINAL_ITERATION = 556
SECOND_ORDER_START = 386
FINAL_WINDOW_START = 537
FINAL_WINDOW_SIZE = 20
RELATIVE_SPAN_LIMIT_PERCENT = 0.02
EXPECTED_ENDPOINT = {
    "external_heat_rate_W_per_m": 28548.27415186194,
    "outlet_mach": 0.9033510682539843,
    "mean_wall_temperature_K": 608.8789970992104,
}
EXPECTED_RESIDUAL_ENDPOINT = {
    "continuity": 5.4279e-05,
    "x_velocity": 5.2467e-09,
    "y_velocity": 1.2948e-08,
    "energy": 2.2610e-08,
    "k": 1.0629e-06,
    "omega": 6.7167e-07,
    "intermittency": 1.8519e-07,
    "retheta": 2.0994e-06,
}


def require_columns(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = columns - set(frame.columns)
    if missing:
        raise ValueError(f"{label}: missing columns {sorted(missing)}")


def metric_value(frame: pd.DataFrame, name: str) -> float:
    rows = frame.loc[frame["metric"] == name, "value"]
    if len(rows) != 1:
        raise ValueError(f"Expected one global-check value for {name}, found {len(rows)}")
    return float(rows.iloc[0])


def relative_span_percent(values: pd.Series) -> float:
    values = values.astype(float)
    return float((values.max() - values.min()) / abs(values.mean()) * 100.0)


def save_figure(figure: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path.with_suffix(".svg"), metadata={"Date": None})
    plt.close(figure)


def verify_monitors(monitors: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        monitors,
        {
            "iteration",
            "external_heat_rate_W_per_m",
            "outlet_mach",
            "mean_wall_temperature_K",
        },
        "Transition SST monitors",
    )
    monitors = monitors.sort_values("iteration").drop_duplicates("iteration", keep="last")
    if int(monitors.iloc[0]["iteration"]) != 236 or int(monitors.iloc[-1]["iteration"]) != FINAL_ITERATION:
        raise ValueError("Transition SST monitors must span iterations 236 through 556")
    if len(monitors) != 321:
        raise ValueError(f"Expected 321 monitor rows, found {len(monitors)}")
    endpoint = monitors.iloc[-1]
    tolerances = {
        "external_heat_rate_W_per_m": 1e-6,
        "outlet_mach": 1e-12,
        "mean_wall_temperature_K": 1e-9,
    }
    for column, expected in EXPECTED_ENDPOINT.items():
        if abs(float(endpoint[column]) - expected) > tolerances[column]:
            raise ValueError(f"Unexpected Transition SST endpoint for {column}")
    final_window = monitors.loc[monitors["iteration"].between(FINAL_WINDOW_START, FINAL_ITERATION)]
    if len(final_window) != FINAL_WINDOW_SIZE:
        raise ValueError("Transition SST final confirmation window must contain 20 iterations")
    summary_rows = []
    for column, label, unit in (
        ("external_heat_rate_W_per_m", "External heat-transfer rate", "W/m"),
        ("outlet_mach", "Outlet Mach", "-"),
        ("mean_wall_temperature_K", "Mean external wall temperature", "K"),
    ):
        span = float(final_window[column].max() - final_window[column].min())
        relative = relative_span_percent(final_window[column])
        if relative >= RELATIVE_SPAN_LIMIT_PERCENT:
            raise ValueError(f"Final-window span failed for {column}: {relative:.6f}%")
        summary_rows.append(
            {
                "quantity": label,
                "unit": unit,
                "final_value": float(endpoint[column]),
                "window_start": FINAL_WINDOW_START,
                "window_end": FINAL_ITERATION,
                "span": span,
                "relative_span_percent": relative,
                "acceptance_limit_percent": RELATIVE_SPAN_LIMIT_PERCENT,
                "status": True,
            }
        )
    return pd.DataFrame(summary_rows)


def verify_residuals(residuals: pd.DataFrame) -> None:
    required = {"iteration", *EXPECTED_RESIDUAL_ENDPOINT}
    require_columns(residuals, required, "Transition SST residuals")
    residuals = residuals.sort_values("iteration").drop_duplicates("iteration", keep="last")
    if int(residuals.iloc[0]["iteration"]) != 236 or int(residuals.iloc[-1]["iteration"]) != FINAL_ITERATION:
        raise ValueError("Transition SST residuals must span iterations 236 through 556")
    endpoint = residuals.iloc[-1]
    for column, expected in EXPECTED_RESIDUAL_ENDPOINT.items():
        if not np.isclose(float(endpoint[column]), expected, rtol=5e-5, atol=1e-12):
            raise ValueError(f"Unexpected final residual for {column}: {endpoint[column]}")


def verify_global_checks(checks: pd.DataFrame) -> pd.DataFrame:
    require_columns(checks, {"metric", "units", "value"}, "Transition SST global checks")
    mass = metric_value(checks, "mass_imbalance_percent")
    interface = metric_value(checks, "interface_mismatch_percent")
    solid = metric_value(checks, "solid_heat_imbalance_percent")
    y_min = metric_value(checks, "wall_yplus_min")
    y_mean = metric_value(checks, "wall_yplus_area_average")
    y_max = metric_value(checks, "wall_yplus_max")
    rows = [
        ("Mass imbalance", mass, "%", 0.01),
        ("Fluid-solid interface mismatch", interface, "%", 0.01),
        ("Solid heat imbalance", solid, "%", 0.05),
        ("Minimum wall y+", y_min, "-", 1.0),
        ("Mean wall y+", y_mean, "-", 1.0),
        ("Maximum wall y+", y_max, "-", 1.0),
    ]
    summary = pd.DataFrame(rows, columns=["check", "value", "unit", "acceptance_limit"])
    summary["status"] = summary["value"] <= summary["acceptance_limit"]
    if not summary["status"].all():
        raise ValueError("Transition SST global checks failed")
    return summary


def verify_wall_export(wall: pd.DataFrame, monitors: pd.DataFrame, checks: pd.DataFrame) -> pd.DataFrame:
    required = {
        "cellnumber",
        "x-coordinate",
        "y-coordinate",
        "pressure",
        "temperature",
        "intermittency",
        "momentum-thickness-re",
        "y-plus",
        "heat-flux",
        "face-area-magnitude",
    }
    require_columns(wall, required, "Transition SST direct wall export")
    if len(wall) != 819 or wall[list(required)].isna().any().any():
        raise ValueError("Transition SST direct wall export must contain 819 complete faces")
    if wall["cellnumber"].duplicated().any():
        raise ValueError("Duplicate Transition SST wall cell numbers")

    area = wall["face-area-magnitude"].astype(float)
    integrated_heat = float((wall["heat-flux"].astype(float) * area).sum())
    area_temperature = float((wall["temperature"].astype(float) * area).sum() / area.sum())
    area_yplus = float((wall["y-plus"].astype(float) * area).sum() / area.sum())
    final = monitors.iloc[-1]
    wall_report = metric_value(checks, "heat_rate_wall_vane_shadow")
    yplus_report = metric_value(checks, "wall_yplus_area_average")

    comparisons = pd.DataFrame(
        [
            (
                "Integrated wall heat rate",
                integrated_heat,
                wall_report,
                "W/m",
                abs(integrated_heat - wall_report),
                0.01,
            ),
            (
                "Area-averaged wall temperature",
                area_temperature,
                float(final["mean_wall_temperature_K"]),
                "K",
                abs(area_temperature - float(final["mean_wall_temperature_K"])),
                1e-3,
            ),
            (
                "Area-averaged wall y+",
                area_yplus,
                yplus_report,
                "-",
                abs(area_yplus - yplus_report),
                1e-6,
            ),
        ],
        columns=["check", "export_value", "reference_value", "unit", "absolute_difference", "acceptance_limit"],
    )
    comparisons["status"] = comparisons["absolute_difference"] <= comparisons["acceptance_limit"]
    if not comparisons["status"].all():
        raise ValueError("Transition SST direct wall-export checks failed")
    return comparisons


def plot_monitors(monitors: pd.DataFrame) -> None:
    figure, axes = plt.subplots(3, 1, figsize=(8.2, 6.8), sharex=True, layout="constrained")
    series = (
        (monitors["outlet_mach"], "Outlet Mach"),
        (monitors["mean_wall_temperature_K"], "Mean wall temperature [K]"),
        (monitors["external_heat_rate_W_per_m"] / 1000.0, r"Heat-rate magnitude [kW m$^{-1}$]"),
    )
    for axis, (values, label) in zip(axes, series):
        axis.plot(monitors["iteration"], values, linewidth=1.5)
        axis.axvline(SECOND_ORDER_START, linewidth=0.9, linestyle="--")
        axis.axvline(536, linewidth=0.9, linestyle=":")
        axis.set_ylabel(label)
        axis.grid(axis="y", linewidth=0.6, alpha=0.22)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
    axes[0].text(SECOND_ORDER_START, 0.04, "bounded second order", rotation=90, va="bottom", ha="right", transform=axes[0].get_xaxis_transform())
    axes[0].text(536, 0.04, "candidate + 20 confirmation", rotation=90, va="bottom", ha="right", transform=axes[0].get_xaxis_transform())
    axes[-1].set_xlabel("Iteration")
    save_figure(figure, FIGURE_CONVERGENCE / "run145_transition_sst_monitors.png")


def plot_residuals(residuals: pd.DataFrame, start: int, stem: str) -> None:
    subset = residuals.loc[residuals["iteration"] >= start].copy()
    figure, axis = plt.subplots(figsize=(8.2, 4.8), layout="constrained")
    labels = {
        "continuity": "Continuity",
        "x_velocity": "x-momentum",
        "y_velocity": "y-momentum",
        "energy": "Energy",
        "k": r"$k$",
        "omega": r"$\omega$",
        "intermittency": "Intermittency",
        "retheta": r"$Re_{\theta t}$",
    }
    for column, label in labels.items():
        values = subset[column].astype(float).where(subset[column].astype(float) > 0.0)
        axis.semilogy(subset["iteration"], values, linewidth=1.15, label=label)
    axis.axvline(SECOND_ORDER_START, linewidth=0.9, linestyle="--")
    axis.set_xlabel("Iteration")
    axis.set_ylabel("Scaled residual")
    axis.grid(axis="y", which="both", linewidth=0.6, alpha=0.22)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.legend(frameon=False, ncol=2)
    save_figure(figure, FIGURE_CONVERGENCE / f"{stem}.png")


def main() -> None:
    monitors = pd.read_csv(MONITORS_SOURCE)
    residuals = pd.read_csv(RESIDUALS_SOURCE)
    wall = pd.read_csv(WALL_SOURCE, skipinitialspace=True)
    wall.columns = wall.columns.astype(str).str.strip()
    checks = pd.read_csv(CHECKS_SOURCE)

    final_window_summary = verify_monitors(monitors)
    verify_residuals(residuals)
    global_summary = verify_global_checks(checks)
    wall_comparisons = verify_wall_export(wall, monitors, checks)

    PROCESSED_CONVERGENCE.mkdir(parents=True, exist_ok=True)
    PROCESSED_VERIFICATION.mkdir(parents=True, exist_ok=True)
    final_window_summary.to_csv(PROCESSED_CONVERGENCE / "run145_transition_sst_final_window_summary.csv", index=False)
    global_summary.to_csv(PROCESSED_VERIFICATION / "run145_transition_sst_global_checks_summary.csv", index=False)
    wall_comparisons.to_csv(PROCESSED_VERIFICATION / "run145_transition_sst_wall_export_checks.csv", index=False)

    plot_monitors(monitors)
    plot_residuals(residuals, SECOND_ORDER_START, "run145_transition_sst_residuals_second_order_window")

    endpoint = monitors.iloc[-1]
    print(f"Transition SST final iteration: {FINAL_ITERATION}")
    print(f"Outlet Mach: {endpoint['outlet_mach']:.9f}")
    print(f"Mean external wall temperature: {endpoint['mean_wall_temperature_K']:.6f} K")
    print(f"External heat-transfer rate: {endpoint['external_heat_rate_W_per_m'] / 1000.0:.6f} kW/m")
    for row in final_window_summary.itertuples(index=False):
        print(f"{row.quantity}: final-20 relative span={row.relative_span_percent:.6f}%")
    print("Transition SST convergence, conservation, wall export and y+ checks: PASS")


if __name__ == "__main__":
    main()
