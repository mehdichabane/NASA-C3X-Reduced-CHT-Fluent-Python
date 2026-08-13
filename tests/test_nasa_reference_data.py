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
    assert "experimental anchor" in rows.loc[
        "inlet_turbulence_intensity", "qualification"
    ].lower()

    assert float(rows.loc["inlet_turbulent_viscosity_ratio", "model_value"]) == 10.0
    assert rows.loc["inlet_turbulent_viscosity_ratio", "classification"] == "Fluent modeling choice"
    vr_qualification = rows.loc["inlet_turbulent_viscosity_ratio", "qualification"].lower()
    assert "not a nasa measurement" in vr_qualification
    assert "not inferred from nasa tu" in vr_qualification
    assert "not calibrated" in vr_qualification
    assert "10, 5 and 1" in rows.loc[
        "inlet_turbulent_viscosity_ratio", "qualification"
    ]

    assert float(rows.loc["outlet_static_pressure", "model_value"]) == 236200.0
    assert rows.loc[
        "outlet_static_pressure", "classification"
    ] == "operating-point adjustment to NASA exit Mach"
    outlet_qualification = rows.loc["outlet_static_pressure", "qualification"].lower()
    assert "not a direct nasa exit-pressure transcription" in outlet_qualification
    assert "operating-point consistency check" in outlet_qualification
    assert "not an independent validation metric" in outlet_qualification

    assert float(rows.loc["experimental_exit_mach", "model_value"]) == 0.90
    assert "operating-point target" in rows.loc[
        "experimental_exit_mach", "qualification"
    ].lower()
    assert "not an independent validation metric" in rows.loc[
        "fine_sst_exit_mach", "qualification"
    ].lower()


def test_run145_outlet_pressure_selection_history() -> None:
    history = pd.read_csv(MODEL_INPUTS / "run145_outlet_pressure_selection.csv")
    rows = history.set_index("stage")

    p_old = float(rows.loc["provisional_second_order", "outlet_static_pressure_Pa"])
    m_old = float(rows.loc["provisional_second_order", "outlet_mach_mass_weighted"])
    m_target = float(rows.loc["provisional_second_order", "target_exit_mach"])
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
    assert "not an independent validation metric" in rows.loc[
        "current_fine_sst", "qualification"
    ].lower()


def test_transition_sst_turbulence_inputs_keep_experiment_and_model_separate() -> None:
    settings = pd.read_csv(MODEL_INPUTS / "transition_sst_settings.csv")
    rows = settings.set_index("setting")

    assert float(rows.loc["inlet_intensity", "value"]) == 6.5
    assert "NASA-CR-168015 Table IX" in rows.loc["inlet_intensity", "source"]
    assert "experimental anchor" in rows.loc["inlet_intensity", "notes"].lower()

    assert float(rows.loc["inlet_viscosity_ratio", "value"]) == 10.0
    vr_source = rows.loc["inlet_viscosity_ratio", "source"].lower()
    vr_notes = rows.loc["inlet_viscosity_ratio", "notes"].lower()
    assert "nasa" not in vr_source
    assert "ansys fluent 26.1" in vr_source
    assert "modeling input" in vr_notes
    assert "not a nasa measurement" in vr_notes
    assert "not inferred from nasa tu uncertainty" in vr_notes
    assert "1-10" in vr_notes

    assert float(rows.loc["inlet_intermittency", "value"]) == 1.0
    assert "not a nasa measurement" in rows.loc[
        "inlet_intermittency", "notes"
    ].lower()
    assert "model-generated transition input" in rows.loc["inlet_retheta", "notes"].lower()
