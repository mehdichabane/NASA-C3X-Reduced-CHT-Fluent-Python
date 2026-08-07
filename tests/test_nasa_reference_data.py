from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "references/experimental_data"


def test_nasa_station_counts_and_surface_labels() -> None:
    pressure = pd.read_csv(DATA / "run145_4512_pressure.csv")
    thermal = pd.read_csv(DATA / "run145_4512_heat_transfer_temperature.csv")

    assert pressure.groupby("surface").size().to_dict() == {
        "pressure": 14,
        "suction": 14,
    }
    assert thermal.groupby("surface").size().to_dict() == {
        "pressure": 31,
        "suction": 44,
    }
    assert not pressure.duplicated(["surface", "s_over_arc"]).any()
    assert not thermal.duplicated(["surface", "s_over_arc"]).any()


def test_nasa_dimensionalized_thermal_values() -> None:
    thermal = pd.read_csv(DATA / "run145_4512_heat_transfer_temperature.csv")
    np.testing.assert_allclose(
        thermal["T_wall_K"], thermal["T_norm"] * 811.0, rtol=0.0, atol=1.1e-3
    )
    np.testing.assert_allclose(
        thermal["h_W_m2K"], thermal["h_norm"] * 1135.0, rtol=0.0, atol=1.1e-3
    )
