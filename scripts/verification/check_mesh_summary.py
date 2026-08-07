from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "results/processed/mesh_sensitivity"
EXPORT_DIR = ROOT / "data/fluent_exports/mesh_sensitivity"

MESH_FILE = EXPORT_DIR / "mesh_summary.csv"
GLOBAL_FILE = DATA_DIR / "run145_three_grid_global_metrics.csv"
LOCAL_FILE = DATA_DIR / "run145_three_grid_local_profile_summary.csv"
COMMON_FILE = DATA_DIR / "run145_three_grid_common_surface_profiles.csv"
QUALITY_FILE = EXPORT_DIR / "mesh_quality_all_grids.csv"
DISTRIBUTION_FILE = EXPORT_DIR / "mesh_quality_distribution_all_grids.csv"

EXPECTED_CELLS = {"coarse": 14657, "medium": 23781, "fine": 44760}
EXPECTED_FACES = {"coarse": 311, "medium": 473, "fine": 819}
GLOBAL_MEDIUM_FINE_LIMIT_PERCENT = 0.10
EXPECTED_CASES = {
    "coarse": ("c3x_run145_nasa_exact_coarse_second_order_ACCEPTED_iter156_yplus_verified", 156),
    "medium": ("c3x_run145_nasa_exact_medium_second_order_ACCEPTED_iter161_yplus_verified", 161),
    "fine": ("c3x_run145_nasa_exact_fine_SST_final_iter236", 236),
}


def read_csv(path: Path, required: set[str]) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path, skipinitialspace=True)
    frame.columns = [column.strip() for column in frame.columns]
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name}: missing columns {sorted(missing)}")
    return frame


def main() -> None:
    mesh = read_csv(MESH_FILE, {"mesh", "source_case", "final_iteration", "fluent_nodes", "fluent_cells", "max_wall_yplus"})
    global_metrics = read_csv(
        GLOBAL_FILE,
        {
            "quantity",
            "medium_to_fine_change_percent",
            "observed_order",
            "gci_status",
        },
    )
    local = read_csv(
        LOCAL_FILE,
        {"comparison", "quantity", "surface", "region", "normalized_mae_percent"},
    )
    common = read_csv(COMMON_FILE, {"surface", "s_over_l", "fine_wall_temperature_K"})
    quality = read_csv(
        QUALITY_FILE,
        {"mesh", "scope", "cells", "maximum_equiangle_skewness", "minimum_orthogonal_quality", "maximum_fluent_aspect_ratio"},
    )
    distribution = read_csv(
        DISTRIBUTION_FILE,
        {
            "mesh", "cells",
            "orthogonal_quality_below_0p1_count", "orthogonal_quality_below_0p1_percent",
            "skewness_above_0p75_count", "skewness_above_0p75_percent",
            "aspect_ratio_above_100_count", "aspect_ratio_above_100_percent",
            "aspect_ratio_above_500_count", "aspect_ratio_above_500_percent",
            "aspect_ratio_above_1000_count", "aspect_ratio_above_1000_percent",
            "minimum_orthogonal_quality_cell", "minimum_orthogonal_quality_x_m",
            "minimum_orthogonal_quality_y_m", "minimum_orthogonal_quality_zone",
            "maximum_equiangle_skewness_cell", "maximum_equiangle_skewness_x_m",
            "maximum_equiangle_skewness_y_m", "maximum_equiangle_skewness_zone",
            "maximum_fluent_aspect_ratio_cell", "maximum_fluent_aspect_ratio_x_m",
            "maximum_fluent_aspect_ratio_y_m", "maximum_fluent_aspect_ratio_zone",
        },
    ).set_index("mesh")

    global_quality = quality.loc[quality["scope"] == "global"].set_index("mesh")
    for row in mesh.itertuples(index=False):
        expected = EXPECTED_CELLS[str(row.mesh)]
        if int(row.fluent_cells) != expected:
            raise ValueError(f"{row.mesh}: expected {expected} cells, found {row.fluent_cells}")
        expected_case, expected_iteration = EXPECTED_CASES[str(row.mesh)]
        if str(row.source_case) != expected_case or int(row.final_iteration) != expected_iteration:
            raise ValueError(f"{row.mesh}: source case or final iteration does not match the record")
        if float(row.max_wall_yplus) >= 1.0:
            raise ValueError(f"{row.mesh}: wall y+ maximum is not below one")
        recorded = global_quality.loc[str(row.mesh)]
        if int(recorded["cells"]) != expected:
            raise ValueError(f"{row.mesh}: mesh-quality cell count mismatch")
        if not 0.0 < float(recorded["minimum_orthogonal_quality"]) <= 1.0:
            raise ValueError(f"{row.mesh}: invalid orthogonal quality")
        if not 0.0 <= float(recorded["maximum_equiangle_skewness"]) < 1.0:
            raise ValueError(f"{row.mesh}: invalid equiangle skewness")
        if abs(float(row.min_orthogonal_quality) - float(recorded["minimum_orthogonal_quality"])) > 5e-7:
            raise ValueError(f"{row.mesh}: mesh-summary orthogonal quality mismatch")
        if abs(float(row.max_skewness) - float(recorded["maximum_equiangle_skewness"])) > 5e-7:
            raise ValueError(f"{row.mesh}: mesh-summary skewness mismatch")
        if str(row.mesh) not in distribution.index:
            raise ValueError(f"{row.mesh}: missing mesh-quality distribution row")
        audit = distribution.loc[str(row.mesh)]
        if int(audit["cells"]) != expected:
            raise ValueError(f"{row.mesh}: distribution cell count mismatch")
        for prefix in (
            "orthogonal_quality_below_0p1",
            "skewness_above_0p75",
            "aspect_ratio_above_100",
            "aspect_ratio_above_500",
            "aspect_ratio_above_1000",
        ):
            count = int(audit[f"{prefix}_count"])
            percent = float(audit[f"{prefix}_percent"])
            expected_percent = 100.0 * count / expected
            if abs(percent - expected_percent) > 1e-10:
                raise ValueError(f"{row.mesh}: inconsistent percentage for {prefix}")
        for prefix in (
            "minimum_orthogonal_quality",
            "maximum_equiangle_skewness",
            "maximum_fluent_aspect_ratio",
        ):
            cell = int(audit[f"{prefix}_cell"])
            if not 1 <= cell <= expected:
                raise ValueError(f"{row.mesh}: invalid worst-cell index for {prefix}")
            if not str(audit[f"{prefix}_zone"]).strip():
                raise ValueError(f"{row.mesh}: missing worst-cell zone for {prefix}")

    for mesh_name, expected_rows in EXPECTED_FACES.items():
        raw = read_csv(
            EXPORT_DIR / f"run145_sst_{mesh_name}_wall.csv",
            {"cellnumber", "x-coordinate", "y-coordinate", "temperature", "heat-flux"},
        )
        if len(raw) != expected_rows:
            raise ValueError(f"{mesh_name}: expected {expected_rows} wall faces, found {len(raw)}")

    if len(common) != 2 * 501:
        raise ValueError(f"Expected 1002 common-profile rows, found {len(common)}")

    largest_global_change = float(global_metrics["medium_to_fine_change_percent"].max())
    if largest_global_change > GLOBAL_MEDIUM_FINE_LIMIT_PERCENT:
        raise ValueError(
            f"Largest medium/fine global change is {largest_global_change:.4f}%, "
            f"above {GLOBAL_MEDIUM_FINE_LIMIT_PERCENT:.4f}%"
        )

    core = local.loc[
        (local["comparison"] == "medium_vs_fine")
        & (local["region"] == "core_1_to_99_percent")
    ].sort_values(["quantity", "surface"])
    if len(core) != 10:
        raise ValueError(f"Expected 10 medium/fine core-profile rows, found {len(core)}")

    print("Three-grid mesh quality")
    print(
        global_quality[["cells", "minimum_orthogonal_quality", "maximum_equiangle_skewness", "maximum_fluent_aspect_ratio"]]
        .to_string(float_format=lambda value: f"{value:.6f}")
    )
    print("\nMesh-quality threshold distribution")
    print(
        distribution[[
            "orthogonal_quality_below_0p1_percent",
            "skewness_above_0p75_percent",
            "aspect_ratio_above_100_percent",
            "aspect_ratio_above_500_percent",
            "aspect_ratio_above_1000_percent",
        ]].to_string(float_format=lambda value: f"{value:.6f}%")
    )
    print("\nThree-grid global mesh sensitivity")
    print(
        global_metrics[
            ["quantity", "medium_to_fine_change_percent", "observed_order", "gci_status"]
        ].to_string(index=False, float_format=lambda value: f"{value:.6f}")
    )
    print("\nMedium/fine core-profile normalized MAE")
    print(
        core[["quantity", "surface", "normalized_mae_percent"]]
        .to_string(index=False, float_format=lambda value: f"{value:.3f}%")
    )


if __name__ == "__main__":
    main()
