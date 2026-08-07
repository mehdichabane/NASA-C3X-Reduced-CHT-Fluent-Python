from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/fluent_exports/run145_sst_global_checks.csv"
OUTPUT_DIR = ROOT / "results/processed/verification"

MASS_LIMIT_PERCENT = 0.01
INTERFACE_LIMIT_PERCENT = 0.01
SOLID_ENERGY_LIMIT_PERCENT = 0.05
YPLUS_LIMIT = 1.0


def value(frame: pd.DataFrame, report: str, name: str) -> float:
    match = frame.loc[
        (frame["report"] == report)
        & (frame["boundary_or_statistic"] == name),
        "value",
    ]
    if len(match) != 1:
        raise ValueError(f"Expected one value for {report}/{name}, found {len(match)}.")
    return float(match.iloc[0])


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)

    frame = pd.read_csv(SOURCE)
    required = {"report", "boundary_or_statistic", "value", "fluent_unit", "reference_depth_m", "unit_per_span"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    depth_values = frame.loc[
        frame["report"].isin(["mass_flow", "heat_transfer"]), "reference_depth_m"
    ].astype(float)
    if not (depth_values == 1.0).all():
        raise ValueError("Expected a 1.0 m reference depth for all integrated reports.")

    inlet = value(frame, "mass_flow", "inlet")
    outlet = value(frame, "mass_flow", "outlet")
    mass_net = value(frame, "mass_flow", "net")
    wall_solid = value(frame, "heat_transfer", "wall_vane_solid_side")
    wall_fluid = value(frame, "heat_transfer", "wall_vane_fluid_side")
    cooling_total = value(frame, "heat_transfer", "cooling_holes_total")
    yplus_min = value(frame, "wall_yplus", "minimum")
    yplus_mean = value(frame, "wall_yplus", "area_weighted_average")
    yplus_max = value(frame, "wall_yplus", "maximum")

    mass_imbalance = abs(mass_net) / max(abs(inlet), abs(outlet)) * 100.0
    interface_mismatch = abs(wall_solid + wall_fluid) / max(
        abs(wall_solid), abs(wall_fluid)
    ) * 100.0
    solid_heat_net = wall_solid + cooling_total
    solid_energy_imbalance = abs(solid_heat_net) / abs(wall_solid) * 100.0

    checks = pd.DataFrame(
        [
            ("Mass imbalance", mass_imbalance, "%", MASS_LIMIT_PERCENT),
            ("Fluid-solid interface mismatch", interface_mismatch, "%", INTERFACE_LIMIT_PERCENT),
            ("Solid heat imbalance", solid_energy_imbalance, "%", SOLID_ENERGY_LIMIT_PERCENT),
            ("Minimum wall y+", yplus_min, "-", YPLUS_LIMIT),
            ("Mean wall y+", yplus_mean, "-", YPLUS_LIMIT),
            ("Maximum wall y+", yplus_max, "-", YPLUS_LIMIT),
        ],
        columns=["check", "value", "unit", "acceptance_limit"],
    )
    checks["status"] = checks["value"] <= checks["acceptance_limit"]

    if not checks["status"].all():
        failed = checks.loc[~checks["status"]]
        raise ValueError("Global checks failed:\n" + failed.to_string(index=False))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    checks.to_csv(OUTPUT_DIR / "run145_sst_global_checks_summary.csv", index=False)

    print(f"Mass imbalance: {mass_imbalance:.6f}%")
    print(f"Fluid-solid interface mismatch: {interface_mismatch:.8f}%")
    print(f"Solid heat imbalance: {solid_energy_imbalance:.6f}% ({solid_heat_net:.3f} W/m net)")
    print(f"Reference depth: {depth_values.iloc[0]:.2f} m")
    print(f"Mass flow per unit span: inlet={inlet:.6f}, outlet={abs(outlet):.6f} kg/(s*m)")
    print(f"External heat-transfer rate: {wall_solid / 1000.0:.6f} kW/m")
    print(f"Wall y+: min={yplus_min:.5f}, mean={yplus_mean:.5f}, max={yplus_max:.5f}")


if __name__ == "__main__":
    main()
