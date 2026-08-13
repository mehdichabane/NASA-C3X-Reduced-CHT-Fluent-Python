from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "results/processed/mesh_sensitivity/run145_three_grid_global_metrics.csv"


def test_three_grid_gci_diagnostics_are_screening_only() -> None:
    metrics = pd.read_csv(METRICS)

    assert set(metrics["quantity"]) == {
        "outlet_mach",
        "mean_wall_temperature_K",
        "external_heat_rate_W_per_m",
    }
    assert set(metrics["gci_status"]) == {"screening"}
