from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INTERNAL = ROOT / "studies/internal_cooling_sensitivity"
TRANSITION = ROOT / "studies/transition_sst_sensitivity"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(path)
    return pd.read_csv(path, skipinitialspace=True)


def require_cases(frame: pd.DataFrame, column: str, expected: set[str], label: str) -> None:
    found = set(frame[column].astype(str))
    if found != expected:
        raise AssertionError(f"{label}: expected cases {sorted(expected)}, found {sorted(found)}")


def check_internal_cooling() -> None:
    h_family = read_csv(INTERNAL / "h_family_summary.csv").sort_values("h_scale")
    t_family = read_csv(INTERNAL / "t_family_summary.csv").sort_values("T_shift_K")
    interaction = read_csv(INTERNAL / "interaction_factorial_coefficients.csv")
    pilot = read_csv(INTERNAL / "h_m10_integral_summary.csv")

    require_cases(
        h_family,
        "case",
        {"h_m10", "h_m05", "baseline", "h_p05", "h_p10"},
        "internal HTC family",
    )
    require_cases(
        t_family,
        "case",
        {"t_m10", "t_m05", "baseline", "t_p05", "t_p10"},
        "internal Tbulk family",
    )

    baseline_columns = [
        "wall_temperature_mean_K",
        "external_heat_rate_W_per_m",
        "outlet_mach",
        "solid_temperature_min_K",
        "solid_temperature_mean_K",
        "solid_temperature_max_K",
        "wall_yplus_max",
    ]
    h_baseline = h_family.loc[h_family["case"] == "baseline", baseline_columns].iloc[0]
    t_baseline = t_family.loc[t_family["case"] == "baseline", baseline_columns].iloc[0]
    if not np.allclose(h_baseline.to_numpy(float), t_baseline.to_numpy(float), rtol=0.0, atol=1e-12):
        raise AssertionError("Internal-cooling families do not share the same baseline values.")

    if not np.all(np.diff(h_family["wall_temperature_mean_K"].to_numpy(float)) < 0):
        raise AssertionError("Mean wall temperature must decrease across increasing h_scale.")
    if not np.all(np.diff(h_family["external_heat_rate_W_per_m"].to_numpy(float)) > 0):
        raise AssertionError("External heat rate must increase across increasing h_scale.")
    if not np.all(np.diff(t_family["wall_temperature_mean_K"].to_numpy(float)) > 0):
        raise AssertionError("Mean wall temperature must increase across increasing Tbulk shift.")
    if not np.all(np.diff(t_family["external_heat_rate_W_per_m"].to_numpy(float)) < 0):
        raise AssertionError("External heat rate must decrease across increasing Tbulk shift.")

    if float(h_family["outlet_mach"].max() - h_family["outlet_mach"].min()) >= 5e-5:
        raise AssertionError("HTC-family outlet Mach response is larger than the documented screening scale.")
    if float(t_family["outlet_mach"].max() - t_family["outlet_mach"].min()) >= 5e-5:
        raise AssertionError("Tbulk-family outlet Mach response is larger than the documented screening scale.")

    principal = interaction.loc[
        interaction["quantity"].isin(
            [
                "mean external wall temperature",
                "external heat-transfer rate",
                "solid mean temperature",
            ]
        )
    ]
    if len(principal) != 3:
        raise AssertionError("Interaction summary is missing a principal thermal response.")
    if not (
        (principal["interaction_to_h_percent"].abs() < 3.0)
        & (principal["interaction_to_T_percent"].abs() < 3.0)
    ).all():
        raise AssertionError("Cooling interaction is no longer small relative to both main effects.")

    pilot_map = pilot.set_index("quantity")
    h_m10 = h_family.loc[h_family["case"] == "h_m10"].iloc[0]
    checks = {
        "mean external wall temperature": ("wall_temperature_mean_K", "h_m10"),
        "external heat-transfer rate": ("external_heat_rate_W_per_m", "h_m10"),
        "outlet Mach number": ("outlet_mach", "h_m10"),
    }
    for quantity, (family_column, pilot_column) in checks.items():
        expected = float(pilot_map.loc[quantity, pilot_column])
        actual = float(h_m10[family_column])
        if not np.isclose(actual, expected, rtol=0.0, atol=1e-10):
            raise AssertionError(f"{quantity}: h-family and pilot summaries disagree.")


def check_transition_sst() -> None:
    matrix = read_csv(TRANSITION / "case_matrix.csv")
    b1 = read_csv(TRANSITION / "b1_three_point_summary.csv")
    b2 = read_csv(TRANSITION / "b2_two_point_summary.csv")

    expected = {"baseline_tu065_vr10", "tu065_vr05", "tu065_vr01", "tu083_vr10"}
    require_cases(matrix, "case_id", expected, "Transition SST case matrix")
    if not (matrix["status"].astype(str).str.lower() == "complete").all():
        raise AssertionError("Transition SST case matrix contains an incomplete case.")

    common_columns = [
        "Tu_in_percent",
        "inlet_viscosity_ratio",
        "Tu_2_to_5mm_percent",
        "mut_over_mu_2_to_5mm",
        "retheta_2_to_5mm",
        "k_2_to_5mm_m2_s2",
        "suction_max_dgamma_x_over_Cx",
        "mean_external_wall_temperature_K",
        "external_heat_transfer_rate_W_per_m",
        "outlet_Mach",
    ]
    b1_base = b1.loc[b1["case_id"] == "baseline_tu065_vr10", common_columns].iloc[0]
    b2_base = b2.loc[b2["case_id"] == "baseline_tu065_vr10", common_columns].iloc[0]
    if not np.allclose(b1_base.to_numpy(float), b2_base.to_numpy(float), rtol=0.0, atol=1e-12):
        raise AssertionError("B1 and B2 do not share the same Transition SST baseline.")

    fixed_tu = b1.sort_values("inlet_viscosity_ratio", ascending=False)
    if fixed_tu["Tu_in_percent"].nunique() != 1:
        raise AssertionError("B1 does not hold Tu_in fixed.")
    if not np.all(np.diff(fixed_tu["Tu_2_to_5mm_percent"].to_numpy(float)) < 0):
        raise AssertionError("Near-vane Tu must decrease from vr10 to vr5 to vr1 in B1.")
    if not np.all(np.diff(fixed_tu["external_heat_transfer_rate_W_per_m"].to_numpy(float)) < 0):
        raise AssertionError("External heat rate must decrease from vr10 to vr5 to vr1 in B1.")
    if not np.all(np.diff(fixed_tu["suction_max_dgamma_x_over_Cx"].to_numpy(float)) > 0):
        raise AssertionError("The B1 transition-like response must move downstream as viscosity ratio decreases.")

    b2_base_row = b2.loc[b2["case_id"] == "baseline_tu065_vr10"].iloc[0]
    b2_high_tu = b2.loc[b2["case_id"] == "tu083_vr10"].iloc[0]
    if float(b2_base_row["inlet_viscosity_ratio"]) != float(b2_high_tu["inlet_viscosity_ratio"]):
        raise AssertionError("B2 does not hold inlet viscosity ratio fixed.")

    def relative_percent(column: str) -> float:
        base = float(b2_base_row[column])
        changed = float(b2_high_tu[column])
        return 100.0 * (changed - base) / base

    if abs(relative_percent("Tu_2_to_5mm_percent")) >= 2.0:
        raise AssertionError("B2 near-vane Tu response exceeds the documented small-response range.")
    if abs(relative_percent("mean_external_wall_temperature_K")) >= 0.1:
        raise AssertionError("B2 mean wall-temperature response exceeds the documented small-response range.")
    if abs(relative_percent("external_heat_transfer_rate_W_per_m")) >= 0.5:
        raise AssertionError("B2 heat-rate response exceeds the documented small-response range.")
    if abs(relative_percent("outlet_Mach")) >= 0.01:
        raise AssertionError("B2 outlet-Mach response exceeds the documented small-response range.")


def main() -> None:
    check_internal_cooling()
    check_transition_sst()
    print("Sensitivity-study consistency checks passed.")


if __name__ == "__main__":
    main()
