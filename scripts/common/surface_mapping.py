"""Coordinate-based wall-surface mapping utilities.

The primary final-mesh mapping is intentionally independent of Fluent cell IDs.
A coordinate reference is used only to preserve the documented pressure/suction
convention at the geometrically ambiguous leading- and trailing-edge points.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

COORDINATE_TOLERANCE_M = 2.0e-7


def read_coordinate_reference(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"reference_x_m", "reference_y_m", "raw_side", "surface"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name}: missing columns {sorted(missing)}")
    if frame.duplicated(["reference_x_m", "reference_y_m"]).any():
        raise ValueError(f"{path.name}: duplicate reference coordinates")
    return frame.reset_index(drop=True)


def map_by_coordinates(
    wall: pd.DataFrame,
    reference: pd.DataFrame,
    tolerance_m: float = COORDINATE_TOLERANCE_M,
) -> pd.DataFrame:
    """Attach pressure/suction labels by a one-to-one coordinate match.

    Cell numbers are deliberately ignored. This remains stable when Fluent
    renumbers or the rows are shuffled, while retaining the exact final-mesh
    leading/trailing-edge convention used by the NASA comparison tables.
    """
    required = {"x-coordinate", "y-coordinate"}
    missing = required - set(wall.columns)
    if missing:
        raise ValueError(f"wall export: missing columns {sorted(missing)}")
    if len(wall) != len(reference):
        raise ValueError(
            f"wall/reference row mismatch: {len(wall)} versus {len(reference)}"
        )

    target = wall[["x-coordinate", "y-coordinate"]].to_numpy(float)
    source = reference[["reference_x_m", "reference_y_m"]].to_numpy(float)
    distance, index = cKDTree(source).query(target, k=1)
    if float(np.max(distance)) > tolerance_m:
        raise ValueError(
            f"maximum coordinate mapping distance {float(np.max(distance)):.3e} m "
            f"exceeds {tolerance_m:.3e} m"
        )
    if len(np.unique(index)) != len(index):
        raise ValueError("coordinate mapping is not one-to-one")

    labels = reference.iloc[index][["raw_side", "surface"]].reset_index(drop=True)
    result = wall.reset_index(drop=True).copy()
    result[["raw_side", "surface"]] = labels
    result["coordinate_mapping_distance_m"] = distance
    return result


def normalized_axial_coordinate(frame: pd.DataFrame) -> np.ndarray:
    x = frame["x-coordinate"].to_numpy(float)
    span = float(x.max() - x.min())
    if span <= 0.0:
        raise ValueError("non-positive wall axial span")
    return (x - float(x.min())) / span
