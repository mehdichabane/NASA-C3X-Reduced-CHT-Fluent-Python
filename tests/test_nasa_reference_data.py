from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "references/experimental_data"
MODEL_INPUTS = ROOT / "references/model_inputs"


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


def test_run145_coolant_table_source_page() -> None:
    coolant = pd.read_csv(DATA / "run145_4512_coolant_flow.csv")
    assert coolant["hole_no"].tolist() == list(range(1, 11))
    assert set(coolant["report_page"]) == {181}
    assert coolant["average_temperature_K"].iloc[0] == 395.38
    assert coolant["average_temperature_K"].iloc[-1] == 506.46


def test_run145_external_boundary_provenance() -> None:
    boundary = pd.read_csv(MODEL_INPUTS / "run145_4512_external_boundary_provenance.csv")
    rows = boundary.set_index("quantity")

    assert float(rows.loc["inlet_total_pressure", "model_value"]) == 403800.0
    assert "rounded NASA" in rows.loc["inlet_total_pressure", "classification"]
    assert float(rows.loc["inlet_total_temperature", "model_value"]) == 792.0
    assert "direct NASA" in rows.loc["inlet_total_temperature", "classification"]
    assert float(rows.loc["inlet_turbulence_intensity", "model_value"]) == 6.5
    assert "direct NASA" in rows.loc["inlet_turbulence_intensity", "classification"]

    assert float(rows.loc["inlet_turbulent_viscosity_ratio", "model_value"]) == 10.0
    assert rows.loc["inlet_turbulent_viscosity_ratio", "classification"] == "Fluent modeling choice"
    assert "not a nasa measurement" in rows.loc[
        "inlet_turbulent_viscosity_ratio", "qualification"
    ].lower()

    assert float(rows.loc["outlet_static_pressure", "model_value"]) == 236200.0
    assert rows.loc["outlet_static_pressure", "classification"] == "archived Fluent boundary input"
    assert "not as a direct nasa transcription" in rows.loc[
        "outlet_static_pressure", "qualification"
    ].lower()
