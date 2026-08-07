from pathlib import Path

import matplotlib.pyplot as plt

plt.rcParams["svg.hashsalt"] = "nasa-c3x-run145"
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/fluent_exports/run145_sst_residuals_final_window.csv"
FULL_SOURCE = ROOT / "data/fluent_exports/run145_sst_residuals_full.csv"
FIGURE_DIR = ROOT / "results/figures/convergence"
EXPECTED_FIRST_ITERATION = 156
EXPECTED_LAST_ITERATION = 236
EXPECTED_ENDPOINT = {
    "continuity": 6.6568e-4,
    "x_velocity": 6.4634e-8,
    "y_velocity": 1.6208e-7,
    "energy": 3.1298e-7,
    "k": 3.8531e-6,
    "omega": 6.8366e-6,
}


def read_residuals(path: Path, first: int, last: int) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    required = {"iteration", *EXPECTED_ENDPOINT}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if frame.empty or int(frame.iloc[0]["iteration"]) != first or int(frame.iloc[-1]["iteration"]) != last:
        raise ValueError(f"Residual history must cover iterations {first}-{last}.")
    if not frame["iteration"].is_monotonic_increasing:
        raise ValueError("Residual iterations are not ordered.")
    if (frame[list(EXPECTED_ENDPOINT)] <= 0).any().any():
        raise ValueError("Residual values must be positive for logarithmic plotting.")
    return frame


def check_endpoint(frame: pd.DataFrame) -> None:
    endpoint = frame.iloc[-1]
    for column, expected in EXPECTED_ENDPOINT.items():
        if not abs(float(endpoint[column]) - expected) <= max(abs(expected) * 5e-5, 5e-12):
            raise ValueError(f"Unexpected endpoint for {column}: {endpoint[column]}")


def plot_residuals(frame: pd.DataFrame, path: Path, xlim: tuple[int, int] | None = None) -> None:
    labels = {"continuity": "Continuity", "x_velocity": "x-momentum", "y_velocity": "y-momentum", "energy": "Energy", "k": r"$k$", "omega": r"$\omega$"}
    figure, axis = plt.subplots(figsize=(7.2, 4.5), layout="constrained")
    for column, label in labels.items():
        axis.semilogy(frame["iteration"], frame[column], linewidth=1.45, label=label)
    axis.set_xlabel("Iteration")
    axis.set_ylabel("Scaled residual")
    axis.set_xlim(*(xlim or (int(frame["iteration"].min()), int(frame["iteration"].max()))))
    axis.grid(axis="y", linewidth=0.6, alpha=0.22)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.legend(ncol=2, frameon=False, loc="best", fontsize=9)
    figure.savefig(path.with_suffix(".svg"), metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    frame = read_residuals(SOURCE, EXPECTED_FIRST_ITERATION, EXPECTED_LAST_ITERATION)
    full = read_residuals(FULL_SOURCE, 1, EXPECTED_LAST_ITERATION)
    check_endpoint(frame)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plot_residuals(frame, FIGURE_DIR / "run145_sst_residuals_final_window.svg")
    endpoint = frame.iloc[-1]
    print(f"Residual window: iterations {EXPECTED_FIRST_ITERATION}-{EXPECTED_LAST_ITERATION}")
    for column in EXPECTED_ENDPOINT:
        print(f"{column}: {endpoint[column]:.4e}")


if __name__ == "__main__":
    main()
