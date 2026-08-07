from pathlib import Path

import matplotlib.pyplot as plt

plt.rcParams["svg.hashsalt"] = "nasa-c3x-run145"
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    ROOT
    / "results/processed/mesh_sensitivity"
    / "run145_sst_fine_wall_mapped.csv"
)
FIGURE_DIR = ROOT / "results/figures/verification"
SUMMARY_SOURCE = ROOT / "data/fluent_exports/run145_sst_global_checks.csv"


def report_value(frame: pd.DataFrame, name: str) -> float:
    rows = frame.loc[
        (frame["report"] == "wall_yplus")
        & (frame["boundary_or_statistic"] == name),
        "value",
    ]
    if len(rows) != 1:
        raise ValueError(f"Missing wall-y-plus statistic: {name}")
    return float(rows.iloc[0])


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    if not SUMMARY_SOURCE.is_file():
        raise FileNotFoundError(SUMMARY_SOURCE)

    wall = pd.read_csv(SOURCE)
    required = {"surface", "s_over_l", "y-plus"}
    missing = required - set(wall.columns)
    if missing:
        raise ValueError(f"Missing wall-data columns: {sorted(missing)}")

    summary = pd.read_csv(SUMMARY_SOURCE)
    yplus_min = report_value(summary, "minimum")
    yplus_mean = report_value(summary, "area_weighted_average")
    yplus_max = report_value(summary, "maximum")

    figure, axes = plt.subplots(1, 2, figsize=(8.6, 3.6), sharey=True, layout="constrained")
    for axis, surface, title in zip(
        axes,
        ("pressure", "suction"),
        ("Pressure side", "Suction side"),
    ):
        data = wall.loc[wall["surface"] == surface].sort_values("s_over_l")
        if data.empty:
            raise ValueError(f"No data found for the {surface} side.")
        axis.plot(data["s_over_l"], data["y-plus"], linewidth=1.5)
        axis.axhline(1.0, linestyle="--", linewidth=1.0, alpha=0.65, label=r"$y^+=1$")
        axis.set_title(title, fontsize=11)
        axis.set_xlabel(r"Normalized surface distance $s/L$")
        axis.set_xlim(0.0, 1.0)
        axis.set_ylim(0.0, 1.05)
        axis.grid(axis="y", linewidth=0.6, alpha=0.22)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)

    axes[0].set_ylabel(r"Wall $y^+$")
    axes[1].legend(frameon=False, loc="upper right")
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    output = FIGURE_DIR / "run145_sst_wall_yplus.svg"
    figure.savefig(output, metadata={"Date": None})
    plt.close(figure)

    print(f"Fluent statistics: min={yplus_min:.5f}, mean={yplus_mean:.5f}, max={yplus_max:.5f}")


if __name__ == "__main__":
    main()
