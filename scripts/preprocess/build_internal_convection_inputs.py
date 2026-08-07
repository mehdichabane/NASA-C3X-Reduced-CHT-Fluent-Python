"""Rebuild the ten reduced internal-convection boundary inputs.

The NASA Run 145 coolant temperatures and Reynolds numbers are combined with
the published passage diameters, source-informed correction factors, and
CoolProp 8.0.0 air properties. Use ``--check`` to compare a fresh rebuild
against the committed model-input table, or ``--write`` to regenerate it.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
COOLANT_PATH = ROOT / "references/experimental_data/run145_4512_coolant_flow.csv"
GEOMETRY_PATH = ROOT / "geometry/raw/c3x_cooling_passages_figure7_uv_cm.csv"
CR_PATH = ROOT / "references/model_inputs/c3x_internal_convection_correction_factors.csv"
OUTPUT_PATH = ROOT / "references/model_inputs/run145_4512_internal_convection.csv"

PROPERTY_PRESSURE_PA = 101325.0
CORRELATION = "Nu_D = Cr * 0.022 * Pr^0.5 * Re_D^0.8"
PROPERTY_MODEL = "CoolProp Air at T_coolant and 101325 Pa"
SOURCE = "NASA coolant data: NASA-CR-168015 Appendix A"
NOTES = (
    "NASA p. 180 supplies T_coolant and Re_D. "
    "scripts/preprocess/build_internal_convection_inputs.py combines them "
    "with passage diameter, C_r and CoolProp air properties."
)

AirPropertyProvider = Callable[
    [float, float], tuple[float, float, float, float, str]
]


def coolprop_air_properties(
    temperature_k: float, pressure_pa: float
) -> tuple[float, float, float, float, str]:
    """Return cp, viscosity, conductivity, Prandtl number, and version."""
    try:
        import CoolProp
        from CoolProp.CoolProp import PropsSI
    except ImportError as exc:  # pragma: no cover - exercised in full CI
        raise RuntimeError(
            "CoolProp is required for this preprocessing step. Install "
            "requirements-preprocess.txt."
        ) from exc

    cp = float(PropsSI("Cpmass", "T", temperature_k, "P", pressure_pa, "Air"))
    mu = float(
        PropsSI("viscosity", "T", temperature_k, "P", pressure_pa, "Air")
    )
    conductivity = float(
        PropsSI("conductivity", "T", temperature_k, "P", pressure_pa, "Air")
    )
    prandtl = float(
        PropsSI("Prandtl", "T", temperature_k, "P", pressure_pa, "Air")
    )
    version = str(getattr(CoolProp, "__version__", "unknown"))
    return cp, mu, conductivity, prandtl, version


def _require_holes(frame: pd.DataFrame, label: str) -> None:
    holes = frame["hole_no"].astype(int).tolist()
    if sorted(holes) != list(range(1, 11)) or len(set(holes)) != 10:
        raise ValueError(
            f"{label} must contain each hole number 1..10 exactly once; "
            f"got {holes}"
        )


def build_internal_convection_table(
    property_provider: AirPropertyProvider = coolprop_air_properties,
) -> pd.DataFrame:
    """Build the ten-passage property and convection-coefficient table."""
    coolant = pd.read_csv(COOLANT_PATH)
    geometry = pd.read_csv(GEOMETRY_PATH)
    correction = pd.read_csv(CR_PATH)
    for frame, label in (
        (coolant, "coolant table"),
        (geometry, "geometry table"),
        (correction, "C_r table"),
    ):
        _require_holes(frame, label)

    inputs = (
        coolant[
            [
                "run",
                "code",
                "hole_no",
                "average_temperature_K",
                "Re_x_1e_minus_4",
                "report_page",
            ]
        ]
        .merge(
            geometry[["hole_no", "diameter_cm"]],
            on="hole_no",
            validate="one_to_one",
        )
        .merge(
            correction[["hole_no", "Cr"]],
            on="hole_no",
            validate="one_to_one",
        )
        .sort_values("hole_no")
        .reset_index(drop=True)
    )

    rows: list[dict[str, object]] = []
    versions: set[str] = set()
    for row in inputs.itertuples(index=False):
        temperature_k = float(row.average_temperature_K)
        re_d = int(round(float(row.Re_x_1e_minus_4) * 1.0e4))
        diameter_m = float(row.diameter_cm) / 100.0
        cr = float(row.Cr)
        cp, mu, conductivity, prandtl, version = property_provider(
            temperature_k, PROPERTY_PRESSURE_PA
        )
        versions.add(version)
        nu_d = cr * 0.022 * prandtl**0.5 * re_d**0.8
        h = nu_d * conductivity / diameter_m
        rows.append(
            {
                "run": int(row.run),
                "code": int(row.code),
                "hole_no": int(row.hole_no),
                "boundary_name": f"cooling_hole_{int(row.hole_no):02d}",
                "T_coolant_K": temperature_k,
                "Re_D": re_d,
                "diameter_m": diameter_m,
                "Cr": cr,
                "cp_J_kgK": cp,
                "mu_Pa_s": mu,
                "k_air_W_mK": conductivity,
                "Pr": prandtl,
                "Nu_D": nu_d,
                "h_W_m2K": h,
                "correlation": CORRELATION,
                "property_model": PROPERTY_MODEL,
                "property_pressure_Pa": int(PROPERTY_PRESSURE_PA),
                "CoolProp_version": version,
                "source": SOURCE,
                "report_page": int(row.report_page),
                "notes": NOTES,
            }
        )
    if len(versions) != 1:
        raise RuntimeError(
            f"Inconsistent CoolProp versions returned: {sorted(versions)}"
        )
    return pd.DataFrame(rows)


def check_against_committed(
    generated: pd.DataFrame, committed: pd.DataFrame
) -> None:
    """Check that a fresh rebuild reproduces the committed numeric table."""
    if list(generated.columns) != list(committed.columns):
        raise AssertionError(
            "Column mismatch:\n"
            f"generated={list(generated.columns)}\n"
            f"committed={list(committed.columns)}"
        )
    if len(generated) != 10 or len(committed) != 10:
        raise AssertionError(
            "Both generated and committed tables must contain ten passages"
        )

    numeric = [
        "run",
        "code",
        "hole_no",
        "T_coolant_K",
        "Re_D",
        "diameter_m",
        "Cr",
        "cp_J_kgK",
        "mu_Pa_s",
        "k_air_W_mK",
        "Pr",
        "Nu_D",
        "h_W_m2K",
        "property_pressure_Pa",
        "report_page",
    ]
    np.testing.assert_allclose(
        generated[numeric].to_numpy(float),
        committed[numeric].to_numpy(float),
        rtol=5.0e-9,
        atol=5.0e-11,
    )
    exact = [
        column
        for column in generated.columns
        if column not in numeric and column != "notes"
    ]
    for column in exact:
        if (
            generated[column].astype(str).tolist()
            != committed[column].astype(str).tolist()
        ):
            raise AssertionError(f"Exact-value mismatch in column {column}")

    if not generated["notes"].str.contains(
        "build_internal_convection_inputs.py", regex=False
    ).all():
        raise AssertionError(
            "Generated notes must identify the preprocessing script"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--check",
        action="store_true",
        help="rebuild in memory and compare with the committed CSV",
    )
    mode.add_argument(
        "--write",
        action="store_true",
        help="regenerate the committed CSV",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generated = build_internal_convection_table()
    if args.write:
        generated.to_csv(OUTPUT_PATH, index=False, float_format="%.10g")
        print(
            f"Wrote {OUTPUT_PATH.relative_to(ROOT)} "
            f"({len(generated)} passages)"
        )
        return

    committed = pd.read_csv(OUTPUT_PATH)
    check_against_committed(generated, committed)
    max_h_abs = float(
        np.max(np.abs(generated["h_W_m2K"] - committed["h_W_m2K"]))
    )
    print(
        "PASS: internal-convection preprocessing reproduces all ten "
        "committed passages"
    )
    print(f"Maximum |Δh|: {max_h_abs:.3e} W/(m²·K)")


if __name__ == "__main__":
    main()
