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


def test_run145_external_boundary_values_and_sources() -> None:
    boundary = pd.read_csv(MODEL_INPUTS / "run145_4512_external_boundary_provenance.csv")
    rows = boundary.set_index("quantity")

    assert float(rows.loc["operating_pressure", "model_value"]) == 0.0
    assert float(rows.loc["inlet_total_pressure", "model_value"]) == 403800.0
    assert float(rows.loc["inlet_total_temperature", "model_value"]) == 792.0
    assert float(rows.loc["experimental_inlet_mach", "model_value"]) == 0.16
    assert float(rows.loc["inlet_turbulence_intensity", "model_value"]) == 6.5
    assert float(rows.loc["inlet_turbulent_viscosity_ratio", "model_value"]) == 10.0
    assert float(rows.loc["outlet_static_pressure", "model_value"]) == 236200.0
    assert float(rows.loc["experimental_exit_mach", "model_value"]) == 0.90
    assert float(rows.loc["fine_sst_exit_mach", "model_value"]) == 0.901294

    for quantity in (
        "inlet_total_pressure",
        "inlet_total_temperature",
        "experimental_inlet_mach",
        "inlet_turbulence_intensity",
        "experimental_exit_mach",
    ):
        assert "NASA-CR-168015" in rows.loc[quantity, "primary_source"]

    assert "Ansys Fluent 26.1" in rows.loc[
        "inlet_turbulent_viscosity_ratio", "primary_source"
    ]
    assert "surface-massavg" in rows.loc["fine_sst_exit_mach", "source_detail"]


def test_run145_outlet_pressure_selection_history() -> None:
    history = pd.read_csv(MODEL_INPUTS / "run145_outlet_pressure_selection.csv")
    rows = history.set_index("stage")

    assert "nominal_nasa_M2" in history.columns
    assert "target_exit_mach" not in history.columns

    p_old = float(rows.loc["provisional_second_order", "outlet_static_pressure_Pa"])
    m_old = float(rows.loc["provisional_second_order", "outlet_mach_mass_weighted"])
    m_target = float(rows.loc["provisional_second_order", "nominal_nasa_M2"])
    gamma = float(rows.loc["provisional_second_order", "gamma"])

    ratio = (
        (1.0 + (gamma - 1.0) / 2.0 * m_target**2)
        / (1.0 + (gamma - 1.0) / 2.0 * m_old**2)
    )
    inferred_pressure = p_old * ratio ** (-gamma / (gamma - 1.0))

    recorded_estimate = float(
        rows.loc["isentropic_update_estimate", "outlet_static_pressure_Pa"]
    )
    np.testing.assert_allclose(inferred_pressure, recorded_estimate, rtol=0.0, atol=1e-9)
    assert round(recorded_estimate, -2) == 236200.0

    assert float(rows.loc["accepted_operating_point", "outlet_static_pressure_Pa"]) == 236200.0
    assert np.isclose(
        float(rows.loc["accepted_operating_point", "outlet_mach_mass_weighted"]),
        0.89951531,
    )
    assert float(rows.loc["current_fine_sst", "outlet_static_pressure_Pa"]) == 236200.0
    assert np.isclose(
        float(rows.loc["current_fine_sst", "outlet_mach_mass_weighted"]),
        0.901294441,
    )


def test_transition_sst_turbulence_inputs() -> None:
    settings = pd.read_csv(MODEL_INPUTS / "transition_sst_settings.csv")
    rows = settings.set_index("setting")

    assert float(rows.loc["inlet_intensity", "value"]) == 6.5
    assert "NASA-CR-168015 Table IX" in rows.loc["inlet_intensity", "source"]

    assert float(rows.loc["inlet_viscosity_ratio", "value"]) == 10.0
    assert "Ansys Fluent 26.1" in rows.loc["inlet_viscosity_ratio", "source"]

    assert float(rows.loc["inlet_intermittency", "value"]) == 1.0
    assert rows.loc["inlet_retheta", "value"] == "Fluent correlation from inlet turbulence intensity"


def test_transition_sst_discretization_provenance() -> None:
    settings = pd.read_csv(MODEL_INPUTS / "transition_sst_settings.csv")
    rows = settings.set_index("setting")

    mean_flow = rows.loc["mean_flow_transition_run", "value"].lower()
    assert "pressure: second order" in mean_flow
    assert "density/momentum/energy: second order upwind" in mean_flow

    stabilization = rows.loc["transition_equations_stabilization"]
    assert stabilization["value"] == "k, omega, intermittency, Re_theta_t: First Order Upwind"
    assert "iteration 386" in stabilization["notes"].lower()

    final = rows.loc["transition_equations_final"]
    assert final["value"] == "k, omega, intermittency, Re_theta_t: Second Order Upwind"
    assert "iteration 386" in final["notes"].lower()
