"""Apply NASA's reported internal-HTC magnitude to the existing h sensitivity."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
UNCERTAINTY_FILE = (
    ROOT / "references/experimental_data/c3x_experimental_uncertainty_summary.csv"
)
H_FAMILY_FILE = ROOT / "studies/internal_cooling_sensitivity/h_family_summary.csv"
OUTPUT_FILE = (
    ROOT
    / "studies/internal_cooling_sensitivity/nasa_informed_internal_htc_envelope.csv"
)

NASA_HTC_UNCERTAINTY_QUANTITY = "internal_cooling_htc_calculation"
CENTRAL_MINUS_CASE = "h_m05"
BASELINE_CASE = "baseline"
CENTRAL_PLUS_CASE = "h_p05"

QUANTITIES = {
    "wall_temperature_mean_K": (
        "mean_external_wall_temperature",
        "K",
        "CFD integral",
    ),
    "external_heat_rate_W_per_m": (
        "external_heat_transfer_rate",
        "W/m",
        "CFD integral",
    ),
    "wall_temperature_bias_pressure_K": (
        "wall_temperature_bias_pressure",
        "K",
        "NASA wall temperature",
    ),
    "wall_temperature_bias_suction_K": (
        "wall_temperature_bias_suction",
        "K",
        "NASA wall temperature",
    ),
    "wall_temperature_mape_pressure_percent": (
        "wall_temperature_mape_pressure",
        "percent",
        "NASA wall temperature",
    ),
    "wall_temperature_mape_suction_percent": (
        "wall_temperature_mape_suction",
        "percent",
        "NASA wall temperature",
    ),
    "htc_mape_pressure_percent": (
        "external_htc_mape_pressure",
        "percent",
        "NASA external HTC",
    ),
    "htc_mape_suction_percent": (
        "external_htc_mape_suction",
        "percent",
        "NASA external HTC",
    ),
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(path)
    return pd.read_csv(path, skipinitialspace=True)


def nasa_internal_htc_uncertainty_percent(uncertainties: pd.DataFrame) -> float:
    matches = uncertainties.loc[
        uncertainties["quantity"].astype(str).eq(NASA_HTC_UNCERTAINTY_QUANTITY)
    ]
    if len(matches) != 1:
        raise ValueError(
            "Expected exactly one NASA internal-cooling HTC uncertainty record."
        )
    row = matches.iloc[0]
    if str(row["uncertainty_unit"]).strip().lower() != "percent":
        raise ValueError("NASA internal-cooling HTC uncertainty is not stored in percent.")
    value = float(row["uncertainty_value"])
    if value <= 0.0:
        raise ValueError("NASA internal-cooling HTC uncertainty must be positive.")
    return value


def required_case(frame: pd.DataFrame, case_id: str) -> pd.Series:
    matches = frame.loc[frame["case"].astype(str).eq(case_id)]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {case_id!r} row in h-family summary.")
    return matches.iloc[0]


def build_envelope(
    h_family: pd.DataFrame, uncertainty_percent: float
) -> pd.DataFrame:
    minus = required_case(h_family, CENTRAL_MINUS_CASE)
    baseline = required_case(h_family, BASELINE_CASE)
    plus = required_case(h_family, CENTRAL_PLUS_CASE)

    h_minus = float(minus["h_scale"])
    h_base = float(baseline["h_scale"])
    h_plus = float(plus["h_scale"])
    if (
        abs(h_minus - 0.95) > 1e-12
        or abs(h_base - 1.0) > 1e-12
        or abs(h_plus - 1.05) > 1e-12
    ):
        raise ValueError(
            "Expected the retained central h family at 0.95, 1.00 and 1.05."
        )

    delta_h_scale = uncertainty_percent / 100.0
    rows: list[dict[str, float | str]] = []

    for column, (label, unit, scope) in QUANTITIES.items():
        derivative_per_h_scale = (
            float(plus[column]) - float(minus[column])
        ) / (h_plus - h_minus)
        derivative_per_plus_1pct_h = derivative_per_h_scale * 0.01
        baseline_value = float(baseline[column])
        value_minus = baseline_value - derivative_per_h_scale * delta_h_scale
        value_plus = baseline_value + derivative_per_h_scale * delta_h_scale

        rows.append(
            {
                "quantity": label,
                "unit": unit,
                "comparison_scope": scope,
                "baseline_value": baseline_value,
                "sensitivity_per_plus_1pct_h": derivative_per_plus_1pct_h,
                "nasa_reported_internal_htc_uncertainty_percent": uncertainty_percent,
                "value_at_h_minus_uncertainty": value_minus,
                "value_at_h_plus_uncertainty": value_plus,
                "envelope_min": min(value_minus, value_plus),
                "envelope_max": max(value_minus, value_plus),
                "half_width": abs(value_plus - baseline_value),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    uncertainties = read_csv(UNCERTAINTY_FILE)
    h_family = read_csv(H_FAMILY_FILE)
    uncertainty_percent = nasa_internal_htc_uncertainty_percent(uncertainties)

    envelope = build_envelope(h_family, uncertainty_percent)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    envelope.to_csv(OUTPUT_FILE, index=False, float_format="%.12g")
    print(
        "Wrote internal-HTC sensitivity envelope "
        f"using +/-{uncertainty_percent:g}% to {OUTPUT_FILE.relative_to(ROOT)}."
    )


if __name__ == "__main__":
    main()
