from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "references" / "experimental_data" / "c3x_experimental_uncertainty_summary.csv"
HTC_TABLE = ROOT / "references" / "experimental_data" / "c3x_heat_transfer_uncertainty_table_VI.csv"


def _summary_by_quantity():
    df = pd.read_csv(SUMMARY)
    assert df["quantity"].is_unique
    return df.set_index("quantity")


def test_nasa_component_and_table_vii_uncertainties_are_transcribed():
    df = _summary_by_quantity()

    expected = {
        "external_vane_surface_temperature": (1.0, "degC", 24),
        "free_stream_gas_temperature": (11.0, "degC", 24),
        "external_airfoil_profile": (0.008, "cm", 24),
        "cooling_hole_location": (0.013, "cm", 24),
        "cooling_hole_diameter": (0.005, "cm", 24),
        "internal_cooling_htc_calculation": (3.0, "percent", 24),
        "vane_material_thermal_conductivity": (3.0, "percent", 24),
        "pressure_measurement": (0.7, "kPa", 27),
        "reynolds_number": (3.1, "percent", 28),
        "mach_number": (0.9, "percent", 28),
        "wall_to_gas_temperature_ratio": (2.0, "percent", 28),
        "inlet_turbulence_intensity": (10.0, "percent", 28),
    }

    assert set(df.index) == set(expected)
    for quantity, (value, unit, page) in expected.items():
        row = df.loc[quantity]
        assert abs(float(row["uncertainty_value"]) - value) < 1e-12
        assert row["uncertainty_unit"] == unit
        assert int(row["report_page"]) == page


def test_table_vii_scope_and_turbulence_method_are_not_overstated():
    df = _summary_by_quantity()
    table_vii = {
        "reynolds_number",
        "mach_number",
        "wall_to_gas_temperature_ratio",
        "inlet_turbulence_intensity",
    }

    assert set(df.index[df["qualifier"] == "table_VII"]) == table_vii
    assert df.loc["inlet_turbulence_intensity", "method_context"] == "LDA experience"
    assert "Kline and McClintock" in df.loc["reynolds_number", "method_context"]


def test_regional_external_htc_uncertainty_remains_a_separate_table():
    summary = pd.read_csv(SUMMARY)
    htc = pd.read_csv(HTC_TABLE)

    assert "external_heat_transfer_coefficient" not in set(summary["quantity"])
    assert len(htc) == 19
    assert set(htc["surface"]) == {"pressure", "suction"}
    assert htc["uncertainty_percent"].min() == 6.2
    assert htc["uncertainty_percent"].max() == 23.5
