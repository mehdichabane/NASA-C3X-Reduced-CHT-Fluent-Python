import numpy as np
import pandas as pd

from scripts.verification.check_sensitivity_studies import (
    INTERNAL,
    TRANSITION,
    check_internal_cooling,
    check_transition_sst,
)


def test_internal_cooling_study_consistency() -> None:
    check_internal_cooling()


def test_transition_sst_study_consistency() -> None:
    check_transition_sst()


def test_sensitivity_headline_regression_values() -> None:
    h_family = pd.read_csv(INTERNAL / "h_family_summary.csv")
    b1 = pd.read_csv(TRANSITION / "b1_three_point_summary.csv")
    b2 = pd.read_csv(TRANSITION / "b2_two_point_summary.csv")

    h_m10 = h_family.loc[h_family["case"] == "h_m10"].iloc[0]
    h_base = h_family.loc[h_family["case"] == "baseline"].iloc[0]
    assert np.isclose(
        float(h_m10["wall_temperature_mean_K"] - h_base["wall_temperature_mean_K"]),
        6.104306924,
        rtol=0.0,
        atol=1e-9,
    )
    assert np.isclose(
        100.0
        * float(h_m10["external_heat_rate_W_per_m"] - h_base["external_heat_rate_W_per_m"])
        / float(h_base["external_heat_rate_W_per_m"]),
        -5.3925157134,
        rtol=0.0,
        atol=1e-9,
    )

    vr10 = b1.loc[b1["case_id"] == "baseline_tu065_vr10"].iloc[0]
    vr01 = b1.loc[b1["case_id"] == "tu065_vr01"].iloc[0]
    assert np.isclose(float(vr10["Tu_2_to_5mm_percent"]), 1.24732612165, rtol=0.0, atol=1e-12)
    assert np.isclose(float(vr01["Tu_2_to_5mm_percent"]), 0.363710121929, rtol=0.0, atol=1e-12)
    assert np.isclose(float(vr10["suction_max_dgamma_x_over_Cx"]), 0.653383547974, rtol=0.0, atol=1e-12)
    assert np.isclose(float(vr01["suction_max_dgamma_x_over_Cx"]), 0.966688346641, rtol=0.0, atol=1e-12)

    b2_base = b2.loc[b2["case_id"] == "baseline_tu065_vr10"].iloc[0]
    tu083 = b2.loc[b2["case_id"] == "tu083_vr10"].iloc[0]
    tw_change_percent = 100.0 * (
        float(tu083["mean_external_wall_temperature_K"])
        - float(b2_base["mean_external_wall_temperature_K"])
    ) / float(b2_base["mean_external_wall_temperature_K"])
    assert np.isclose(tw_change_percent, -0.03306776978, rtol=0.0, atol=1e-10)
