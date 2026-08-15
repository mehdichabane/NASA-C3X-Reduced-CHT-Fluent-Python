from pathlib import Path

import numpy as np
import pandas as pd

from scripts.postprocess.build_nasa_informed_cooling_envelope import (
    build_envelope,
    nasa_internal_htc_uncertainty_percent,
)

ROOT = Path(__file__).resolve().parents[1]
UNCERTAINTY_FILE = ROOT / "references" / "experimental_data" / "c3x_experimental_uncertainty_summary.csv"
H_FAMILY_FILE = ROOT / "studies/internal_cooling_sensitivity/h_family_summary.csv"
ENVELOPE_FILE = (
    ROOT
    / "studies/internal_cooling_sensitivity/nasa_informed_internal_htc_envelope.csv"
)


def test_nasa_internal_htc_uncertainty_drives_committed_envelope():
    uncertainty = pd.read_csv(UNCERTAINTY_FILE, skipinitialspace=True)
    h_family = pd.read_csv(H_FAMILY_FILE, skipinitialspace=True)
    committed = pd.read_csv(ENVELOPE_FILE, skipinitialspace=True)

    uncertainty_percent = nasa_internal_htc_uncertainty_percent(uncertainty)
    assert uncertainty_percent == 3.0

    rebuilt = build_envelope(h_family, uncertainty_percent)
    assert committed["quantity"].tolist() == rebuilt["quantity"].tolist()

    numeric_columns = [
        "baseline_value",
        "sensitivity_per_plus_1pct_h",
        "nasa_reported_internal_htc_uncertainty_percent",
        "value_at_h_minus_uncertainty",
        "value_at_h_plus_uncertainty",
        "envelope_min",
        "envelope_max",
        "half_width",
    ]
    assert np.allclose(
        committed[numeric_columns].to_numpy(float),
        rebuilt[numeric_columns].to_numpy(float),
        rtol=0.0,
        atol=2e-8,
    )


def test_reported_internal_htc_envelope_does_not_remove_wall_temperature_bias():
    envelope = pd.read_csv(ENVELOPE_FILE, skipinitialspace=True).set_index("quantity")

    for quantity in (
        "wall_temperature_bias_pressure",
        "wall_temperature_bias_suction",
    ):
        assert float(envelope.loc[quantity, "envelope_min"]) > 0.0
