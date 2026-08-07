"""Topology-based weighted least-squares gradient reconstruction."""
from __future__ import annotations
from collections import defaultdict
import numpy as np
import pandas as pd


def adjacency_dict(frame: pd.DataFrame) -> dict[int, set[int]]:
    required = {"cellnumber", "neighbor_cellnumber"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"adjacency: missing columns {sorted(missing)}")
    result: dict[int, set[int]] = defaultdict(set)
    for row in frame.itertuples(index=False):
        result[int(row.cellnumber)].add(int(row.neighbor_cellnumber))
    return result


def topology_stencil(
    cell: int,
    adjacency: dict[int, set[int]],
    minimum_neighbours: int = 8,
    maximum_ring: int = 4,
) -> tuple[list[int], int]:
    visited = {cell}
    frontier = {cell}
    neighbours: set[int] = set()
    ring = 0
    while frontier and len(neighbours) < minimum_neighbours and ring < maximum_ring:
        ring += 1
        next_frontier: set[int] = set()
        for current in frontier:
            for candidate in adjacency.get(current, set()):
                if candidate not in visited:
                    visited.add(candidate)
                    neighbours.add(candidate)
                    next_frontier.add(candidate)
        frontier = next_frontier
    if len(neighbours) < 2:
        raise ValueError(f"cell {cell}: insufficient connected neighbours")
    return sorted(neighbours), ring


def reconstruct_gradient(
    cell_ids: np.ndarray,
    coordinates: np.ndarray,
    values: np.ndarray,
    adjacency: dict[int, set[int]],
    minimum_neighbours: int = 8,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    index_of = {int(cell): index for index, cell in enumerate(cell_ids)}
    gradient = np.empty((len(cell_ids), 2))
    condition = np.empty(len(cell_ids))
    residual_rmse = np.empty(len(cell_ids))
    counts = np.empty(len(cell_ids), dtype=int)
    rings = np.empty(len(cell_ids), dtype=int)

    for index, cell in enumerate(cell_ids):
        neighbour_ids, ring = topology_stencil(
            int(cell), adjacency, minimum_neighbours=minimum_neighbours
        )
        try:
            neighbour_index = np.asarray([index_of[item] for item in neighbour_ids], dtype=int)
        except KeyError as error:
            raise ValueError(f"adjacency refers to absent cell {error.args[0]}") from error
        delta_xy = coordinates[neighbour_index] - coordinates[index]
        delta_value = values[neighbour_index] - values[index]
        radius = np.linalg.norm(delta_xy, axis=1)
        weights = 1.0 / np.maximum(radius, 1e-14) ** 2
        matrix = delta_xy * np.sqrt(weights)[:, None]
        rhs = delta_value * np.sqrt(weights)
        solution, *_ = np.linalg.lstsq(matrix, rhs, rcond=None)
        gradient[index] = solution
        condition[index] = np.linalg.cond(matrix)
        residual = delta_value - delta_xy @ solution
        residual_rmse[index] = float(np.sqrt(np.mean(residual**2)))
        counts[index] = len(neighbour_ids)
        rings[index] = ring
    return gradient, condition, residual_rmse, counts, rings
