from pathlib import Path

import matplotlib.pyplot as plt

plt.rcParams["svg.hashsalt"] = "nasa-c3x-run145"
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/fluent_exports/run145_sst_convergence_monitors.csv"
FIGURE_DIR = ROOT / "results/figures/convergence"

FINAL_ITERATION = 236
FINAL_WINDOW = 20
EXPECTED_ENDPOINT = {
    "heat_rate_magnitude_W_per_m": 35819.60242176458,
    "wall_temperature_K": 655.6192166102478,
    "mach_outlet": 0.9012944409738727,
}
TOLERANCE = {
    "heat_rate_magnitude_W_per_m": 1e-6,
    "wall_temperature_K": 1e-9,
    "mach_outlet": 1e-12,
}


def read_monitors(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    required = {"iteration", *EXPECTED_ENDPOINT}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing monitor columns: {sorted(missing)}")
    frame = frame.sort_values("iteration").drop_duplicates("iteration", keep="last")
    if frame.empty or int(frame.iloc[-1]["iteration"]) != FINAL_ITERATION:
        raise ValueError(f"Expected iteration {FINAL_ITERATION} at the end of the monitor file.")
    if not frame["iteration"].is_monotonic_increasing:
        raise ValueError("Monitor iterations are not ordered.")
    return frame.reset_index(drop=True)


def check_endpoint(frame: pd.DataFrame) -> None:
    endpoint = frame.iloc[-1]
    for column, expected in EXPECTED_ENDPOINT.items():
        error = abs(float(endpoint[column]) - expected)
        if error > TOLERANCE[column]:
            raise ValueError(f"Unexpected endpoint for {column}: error={error:.3e}")


def plot_monitors(frame: pd.DataFrame, path: Path) -> None:
    figure, axes = plt.subplots(3, 1, figsize=(8.2, 6.8), sharex=True, layout="constrained")
    series = (
        (frame["mach_outlet"], "Outlet Mach"),
        (frame["wall_temperature_K"], "Mean wall temperature [K]"),
        (frame["heat_rate_magnitude_W_per_m"] / 1000.0, r"Heat-rate magnitude [kW m$^{-1}$]"),
    )
    for axis, (values, label) in zip(axes, series):
        axis.plot(frame["iteration"], values, linewidth=1.6)
        axis.axvline(67, color="0.55", linewidth=0.9)
        axis.axvline(216, color="0.65", linewidth=0.9, linestyle="--")
        axis.set_ylabel(label)
        axis.grid(axis="y", linewidth=0.6, alpha=0.22)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
    axes[0].text(67, 0.04, "second-order schemes", rotation=90, va="bottom", ha="right", color="0.4", transform=axes[0].get_xaxis_transform())
    axes[0].text(216, 0.04, "residual criterion met", rotation=90, va="bottom", ha="right", color="0.45", transform=axes[0].get_xaxis_transform())
    axes[-1].set_xlabel("Iteration")
    figure.savefig(path.with_suffix(".svg"), metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    frame = read_monitors(SOURCE)
    check_endpoint(frame)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plot_monitors(frame, FIGURE_DIR / "run145_sst_monitors.svg")

    endpoint = frame.iloc[-1]
    window = frame.tail(FINAL_WINDOW)
    cols = ["heat_rate_magnitude_W_per_m", "wall_temperature_K", "mach_outlet"]
    spans = window[cols].max() - window[cols].min()
    relative_spans = spans / window[cols].mean().abs() * 100.0
    print(f"Final iteration: {FINAL_ITERATION}")
    print(f"Outlet Mach: {endpoint['mach_outlet']:.9f}")
    print(f"Area-averaged external wall temperature: {endpoint['wall_temperature_K']:.3f} K")
    print(f"External heat-transfer-rate magnitude: {endpoint['heat_rate_magnitude_W_per_m'] / 1000:.3f} kW/m")
    print(
        "Final-20 spans: "
        f"Mach={spans['mach_outlet']:.3e} ({relative_spans['mach_outlet']:.6f}%), "
        f"Twall={spans['wall_temperature_K']:.3e} K ({relative_spans['wall_temperature_K']:.6f}%), "
        f"heat rate={spans['heat_rate_magnitude_W_per_m']:.3e} W/m "
        f"({relative_spans['heat_rate_magnitude_W_per_m']:.6f}%)"
    )


if __name__ == "__main__":
    main()
