"""Rebuild the SST and Transition SST wall profiles used for the NASA comparison."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.common.surface_mapping import (
    map_by_coordinates,
    normalized_axial_coordinate,
    read_coordinate_reference,
)

REFERENCE = ROOT / "references/model_inputs/run145_wall_surface_coordinate_reference.csv"
PT_INLET_PA = 403800.0
NASA_REFERENCE_TEMPERATURE_K = 811.0
SOURCES = {
    "sst": ROOT / "data/fluent_exports/mesh_sensitivity/run145_sst_fine_wall.csv",
    "transition_sst": ROOT / "data/fluent_exports/transition_sst/run145_transition_sst_fine_wall_direct_fluent_iter556.csv",
}
OUTPUTS = {
    "sst": ROOT / "results/processed/mesh_sensitivity/run145_sst_comparison_profile.csv",
    "transition_sst": ROOT / "results/processed/mesh_sensitivity/run145_transition_sst_comparison_profile.csv",
}
REQUIRED_RAW = {
    "cellnumber", "x-coordinate", "y-coordinate", "pressure", "temperature",
    "y-plus", "heat-flux",
}


def rebuild(source: Path, reference: pd.DataFrame) -> pd.DataFrame:
    raw = pd.read_csv(source, skipinitialspace=True)
    raw.columns = raw.columns.astype(str).str.strip()
    missing = REQUIRED_RAW - set(raw.columns)
    if missing:
        raise ValueError(f"{source.name}: missing columns {sorted(missing)}")
    if raw["cellnumber"].duplicated().any():
        raise ValueError(f"{source.name}: duplicate cell numbers")
    out = map_by_coordinates(raw, reference)
    out["wall-temperature"] = out["temperature"]
    out["ps_over_pt"] = out["pressure"] / PT_INLET_PA
    out["x_over_c"] = normalized_axial_coordinate(out)
    out["q_into_vane_W_m2"] = -out["heat-flux"]
    out["h_signed_W_m2K"] = out["q_into_vane_W_m2"] / (
        NASA_REFERENCE_TEMPERATURE_K - out["wall-temperature"]
    )
    numeric = [
        "pressure", "temperature", "heat-flux", "x_over_c", "ps_over_pt",
        "coordinate_mapping_distance_m",
    ]
    if not np.isfinite(out[numeric].to_numpy(float)).all():
        raise ValueError(f"{source.name}: non-finite rebuilt value")
    return out


def main() -> None:
    reference = read_coordinate_reference(REFERENCE)
    for label, source in SOURCES.items():
        output = OUTPUTS[label]
        rebuilt = rebuild(source, reference)
        output.parent.mkdir(parents=True, exist_ok=True)
        rebuilt.to_csv(output, index=False)
        print(
            f"Rebuilt {output.relative_to(ROOT)} from {len(rebuilt)} wall cells; "
            f"max coordinate distance={rebuilt['coordinate_mapping_distance_m'].max():.3e} m"
        )


if __name__ == "__main__":
    main()
