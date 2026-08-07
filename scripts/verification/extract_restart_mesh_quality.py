"""Extract auditable mesh quality and solid adjacency from Fluent CFF cases."""
from __future__ import annotations
from pathlib import Path
import argparse
import sys
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.common.fluent_h5_mesh import read_case_mesh, compute_quality, cell_adjacency

DEFAULT_CASES = {
    "coarse": "c3x_run145_nasa_exact_coarse_second_order_ACCEPTED_iter156_yplus_verified.cas.h5",
    "medium": "c3x_run145_nasa_exact_medium_second_order_ACCEPTED_iter161_yplus_verified.cas.h5",
    "fine": "c3x_run145_nasa_exact_fine_SST_final_iter236.cas.h5",
}


def _zone_name(mesh, cell_index: int) -> str:
    for zone in mesh.zones:
        if zone.first_cell <= cell_index <= zone.last_cell:
            return zone.name
    return "unknown"


def _extreme_record(mesh, quality: dict[str, np.ndarray], field: str, mode: str) -> dict[str, object]:
    values = quality[field]
    cell_index = int(np.argmin(values) if mode == "min" else np.argmax(values))
    x, y = quality["cell_centroid"][cell_index]
    return {
        "value": float(values[cell_index]),
        "cell_one_based": cell_index + 1,
        "x_m": float(x),
        "y_m": float(y),
        "zone": _zone_name(mesh, cell_index),
    }


def extract(
    restart_dir: Path,
    output: Path,
    adjacency_output: Path | None,
    distribution_output: Path | None,
) -> None:
    rows: list[dict[str, object]] = []
    distribution_rows: list[dict[str, object]] = []
    for mesh_name, filename in DEFAULT_CASES.items():
        case = restart_dir / filename
        if not case.is_file():
            raise FileNotFoundError(case)
        mesh = read_case_mesh(case)
        quality = compute_quality(mesh)
        for scope, start, stop in [
            ("global", 0, mesh.number_of_cells - 1),
            *[(zone.name, zone.first_cell, zone.last_cell) for zone in mesh.zones],
        ]:
            selection = slice(start, stop + 1)
            skew = quality["equiangle_skewness"][selection]
            orthogonal = quality["orthogonal_quality"][selection]
            aspect = quality["fluent_aspect_ratio"][selection]
            rows.append({
                "mesh": mesh_name,
                "scope": scope,
                "cells": stop - start + 1,
                "maximum_equiangle_skewness": float(skew.max()),
                "minimum_orthogonal_quality": float(orthogonal.min()),
                "maximum_fluent_aspect_ratio": float(aspect.max()),
            })

        orthogonal = quality["orthogonal_quality"]
        skew = quality["equiangle_skewness"]
        aspect = quality["fluent_aspect_ratio"]
        minimum_oq = _extreme_record(mesh, quality, "orthogonal_quality", "min")
        maximum_skew = _extreme_record(mesh, quality, "equiangle_skewness", "max")
        maximum_ar = _extreme_record(mesh, quality, "fluent_aspect_ratio", "max")
        distribution_rows.append({
            "mesh": mesh_name,
            "cells": mesh.number_of_cells,
            "orthogonal_quality_below_0p1_count": int(np.count_nonzero(orthogonal < 0.1)),
            "orthogonal_quality_below_0p1_percent": float(np.mean(orthogonal < 0.1) * 100.0),
            "skewness_above_0p75_count": int(np.count_nonzero(skew > 0.75)),
            "skewness_above_0p75_percent": float(np.mean(skew > 0.75) * 100.0),
            "aspect_ratio_above_100_count": int(np.count_nonzero(aspect > 100.0)),
            "aspect_ratio_above_100_percent": float(np.mean(aspect > 100.0) * 100.0),
            "aspect_ratio_above_500_count": int(np.count_nonzero(aspect > 500.0)),
            "aspect_ratio_above_500_percent": float(np.mean(aspect > 500.0) * 100.0),
            "aspect_ratio_above_1000_count": int(np.count_nonzero(aspect > 1000.0)),
            "aspect_ratio_above_1000_percent": float(np.mean(aspect > 1000.0) * 100.0),
            "minimum_orthogonal_quality": minimum_oq["value"],
            "minimum_orthogonal_quality_cell": minimum_oq["cell_one_based"],
            "minimum_orthogonal_quality_x_m": minimum_oq["x_m"],
            "minimum_orthogonal_quality_y_m": minimum_oq["y_m"],
            "minimum_orthogonal_quality_zone": minimum_oq["zone"],
            "maximum_equiangle_skewness": maximum_skew["value"],
            "maximum_equiangle_skewness_cell": maximum_skew["cell_one_based"],
            "maximum_equiangle_skewness_x_m": maximum_skew["x_m"],
            "maximum_equiangle_skewness_y_m": maximum_skew["y_m"],
            "maximum_equiangle_skewness_zone": maximum_skew["zone"],
            "maximum_fluent_aspect_ratio": maximum_ar["value"],
            "maximum_fluent_aspect_ratio_cell": maximum_ar["cell_one_based"],
            "maximum_fluent_aspect_ratio_x_m": maximum_ar["x_m"],
            "maximum_fluent_aspect_ratio_y_m": maximum_ar["y_m"],
            "maximum_fluent_aspect_ratio_zone": maximum_ar["zone"],
        })

        if mesh_name == "fine" and adjacency_output is not None:
            solid = next(zone for zone in mesh.zones if "solid_vane" in zone.name)
            pairs = cell_adjacency(mesh, solid)
            # Fluent ASCII "cellnumber" values are export-row identifiers, not
            # guaranteed CFF global cell IDs. Match by cell-centre coordinates.
            exported = pd.read_csv(
                ROOT / "data/fluent_exports/run145_sst_solid_cell_temperature.csv",
                skipinitialspace=True,
            )
            exported.columns = exported.columns.astype(str).str.strip()
            export_xy = exported[["x-coordinate", "y-coordinate"]].to_numpy(float)
            cff_xy = quality["cell_centroid"][solid.first_cell : solid.last_cell + 1]
            distance, nearest = cKDTree(export_xy).query(cff_xy, k=1)
            if len(np.unique(nearest)) != len(nearest) or float(distance.max()) > 1.0e-4:
                raise ValueError("CFF-to-export solid cell-centre mapping is not one-to-one")
            export_ids = exported.iloc[nearest]["cellnumber"].to_numpy(int)
            mapped_pairs = [
                (int(export_ids[first - 1]), int(export_ids[second - 1]))
                for first, second in pairs
            ]
            pd.DataFrame(
                mapped_pairs, columns=["cellnumber", "neighbor_cellnumber"]
            ).sort_values(["cellnumber", "neighbor_cellnumber"]).to_csv(
                adjacency_output, index=False
            )
            print(
                f"Wrote {len(mapped_pairs)} directed solid-cell adjacencies; "
                f"max CFF/export centre distance={float(distance.max()):.3e} m"
            )
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)
    print(f"Wrote {output}")
    if distribution_output is not None:
        distribution_output.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(distribution_rows).to_csv(distribution_output, index=False)
        print(f"Wrote {distribution_output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("restart_dir", type=Path)
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "data/fluent_exports/mesh_sensitivity/mesh_quality_all_grids.csv",
    )
    parser.add_argument(
        "--adjacency-output", type=Path,
        default=ROOT / "data/fluent_exports/run145_sst_solid_cell_adjacency.csv",
    )
    parser.add_argument(
        "--distribution-output", type=Path,
        default=ROOT / "data/fluent_exports/mesh_sensitivity/mesh_quality_distribution_all_grids.csv",
    )
    args = parser.parse_args()
    extract(args.restart_dir, args.output, args.adjacency_output, args.distribution_output)


if __name__ == "__main__":
    main()
