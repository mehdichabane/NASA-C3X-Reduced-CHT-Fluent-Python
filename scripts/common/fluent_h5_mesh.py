"""Read a 2-D Fluent CFF case mesh and reproduce core mesh-quality metrics.

The formulas follow Fluent's documented equiangle-skewness, orthogonality and
Fluent-aspect-ratio definitions. The implementation was cross-checked against
the fine-grid values reported directly by Fluent 26.1.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict
import math
import re
import h5py
import numpy as np


@dataclass(frozen=True)
class CellZone:
    zone_id: int
    first_cell: int  # zero-based inclusive
    last_cell: int   # zero-based inclusive
    name: str


@dataclass
class Mesh2D:
    coordinates: np.ndarray
    face_nodes: list[np.ndarray]
    face_c0: np.ndarray
    face_c1: np.ndarray
    zones: list[CellZone]

    @property
    def number_of_cells(self) -> int:
        return int(max(self.face_c0.max(), self.face_c1.max()) + 1)


def _parse_zone_names(raw: str, count: int) -> list[str]:
    quoted = re.findall(r'"([^"]+)"', raw)
    if len(quoted) == count:
        return quoted
    split = [item.strip() for item in raw.split(";") if item.strip()]
    if len(split) == count:
        return split
    return [f"zone_{index + 1}" for index in range(count)]


def read_case_mesh(path: Path) -> Mesh2D:
    with h5py.File(path, "r") as handle:
        coordinates = np.asarray(handle["meshes/1/nodes/coords/6"][:], dtype=float)
        face_group = handle["meshes/1/faces/nodes/1"]
        node_counts = np.asarray(face_group["nnodes"][:], dtype=int)
        flattened = np.asarray(face_group["nodes"][:], dtype=int) - 1
        face_nodes: list[np.ndarray] = []
        position = 0
        for count in node_counts:
            face_nodes.append(flattened[position : position + count])
            position += int(count)

        face_c0 = np.asarray(handle["meshes/1/faces/c0/1"][:], dtype=int) - 1
        raw_c1 = np.asarray(handle["meshes/1/faces/c1/1"][:], dtype=int) - 1
        face_c1 = np.full(len(face_nodes), -1, dtype=int)
        face_c1[: len(raw_c1)] = raw_c1

        topology = handle["meshes/1/cells/zoneTopology"]
        zone_ids = np.asarray(topology["id"][:], dtype=int)
        first = np.asarray(topology["minId"][:], dtype=int) - 1
        last = np.asarray(topology["maxId"][:], dtype=int) - 1
        raw_names = topology["name"][0]
        if isinstance(raw_names, bytes):
            raw_names = raw_names.decode()
        names = _parse_zone_names(str(raw_names), len(zone_ids))
        zones = [
            CellZone(int(zone_id), int(start), int(stop), name)
            for zone_id, start, stop, name in zip(zone_ids, first, last, names)
        ]
    return Mesh2D(coordinates, face_nodes, face_c0, face_c1, zones)


def order_polygon(points: np.ndarray) -> np.ndarray:
    centre = points.mean(axis=0)
    angle = np.arctan2(points[:, 1] - centre[1], points[:, 0] - centre[0])
    return points[np.argsort(angle)]


def polygon_centroid(polygon: np.ndarray) -> tuple[float, np.ndarray]:
    x = polygon[:, 0]
    y = polygon[:, 1]
    x_next = np.roll(x, -1)
    y_next = np.roll(y, -1)
    cross = x * y_next - x_next * y
    signed_area = 0.5 * float(cross.sum())
    if abs(signed_area) < 1e-30:
        return abs(signed_area), polygon.mean(axis=0)
    centroid = np.array(
        [((x + x_next) * cross).sum(), ((y + y_next) * cross).sum()]
    ) / (6.0 * signed_area)
    return abs(signed_area), centroid


def polygon_angles_degrees(polygon: np.ndarray) -> np.ndarray:
    values: list[float] = []
    for index in range(len(polygon)):
        previous = polygon[(index - 1) % len(polygon)] - polygon[index]
        following = polygon[(index + 1) % len(polygon)] - polygon[index]
        cosine = np.dot(previous, following) / (
            np.linalg.norm(previous) * np.linalg.norm(following)
        )
        values.append(math.degrees(math.acos(float(np.clip(cosine, -1.0, 1.0)))))
    return np.asarray(values)


def equiangle_skewness(polygon: np.ndarray) -> float:
    angles = polygon_angles_degrees(polygon)
    ideal = 180.0 * (len(polygon) - 2) / len(polygon)
    return float(
        max(
            (float(angles.max()) - ideal) / (180.0 - ideal),
            (ideal - float(angles.min())) / ideal,
        )
    )


def build_cell_connectivity(mesh: Mesh2D):
    cell_faces: dict[int, list[int]] = defaultdict(list)
    cell_nodes: dict[int, set[int]] = defaultdict(set)
    for face_index, nodes in enumerate(mesh.face_nodes):
        for cell in (mesh.face_c0[face_index], mesh.face_c1[face_index]):
            if cell >= 0:
                cell_faces[int(cell)].append(face_index)
                cell_nodes[int(cell)].update(int(node) for node in nodes)
    return cell_faces, cell_nodes


def compute_quality(mesh: Mesh2D) -> dict[str, np.ndarray]:
    number_of_cells = mesh.number_of_cells
    cell_faces, cell_nodes = build_cell_connectivity(mesh)
    centroids = np.empty((number_of_cells, 2))
    areas = np.empty(number_of_cells)
    skewness = np.empty(number_of_cells)

    for cell in range(number_of_cells):
        polygon = order_polygon(mesh.coordinates[list(cell_nodes[cell])])
        area, centroid = polygon_centroid(polygon)
        areas[cell] = area
        centroids[cell] = centroid
        skewness[cell] = equiangle_skewness(polygon)

    orthogonal_quality = np.ones(number_of_cells)
    aspect_ratio = np.ones(number_of_cells)
    for cell in range(number_of_cells):
        orthogonality: list[float] = []
        distances: list[float] = []
        for face_index in cell_faces[cell]:
            nodes = mesh.face_nodes[face_index]
            p0, p1 = mesh.coordinates[nodes[0]], mesh.coordinates[nodes[1]]
            face_centre = 0.5 * (p0 + p1)
            edge = p1 - p0
            normal = np.array([edge[1], -edge[0]])
            normal_norm = np.linalg.norm(normal)
            if normal_norm == 0.0:
                continue
            centre_to_face = face_centre - centroids[cell]
            if np.linalg.norm(centre_to_face) > 0.0:
                orthogonality.append(
                    abs(np.dot(normal, centre_to_face))
                    / (normal_norm * np.linalg.norm(centre_to_face))
                )
                distances.append(abs(np.dot(normal, centre_to_face)) / normal_norm)
            other = (
                mesh.face_c1[face_index]
                if mesh.face_c0[face_index] == cell
                else mesh.face_c0[face_index]
            )
            if other >= 0:
                centre_to_centre = centroids[other] - centroids[cell]
                if np.linalg.norm(centre_to_centre) > 0.0:
                    orthogonality.append(
                        abs(np.dot(normal, centre_to_centre))
                        / (normal_norm * np.linalg.norm(centre_to_centre))
                    )
            distances.extend(
                np.linalg.norm(mesh.coordinates[node] - centroids[cell]) for node in nodes
            )
        orthogonal_quality[cell] = min(orthogonality) if orthogonality else np.nan
        positive = [value for value in distances if value > 0.0]
        aspect_ratio[cell] = max(positive) / min(positive) if positive else np.nan

    return {
        "cell_centroid": centroids,
        "cell_area": areas,
        "equiangle_skewness": skewness,
        "orthogonal_quality": orthogonal_quality,
        "fluent_aspect_ratio": aspect_ratio,
    }


def cell_adjacency(mesh: Mesh2D, zone: CellZone) -> list[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()
    for c0, c1 in zip(mesh.face_c0, mesh.face_c1):
        if c0 < 0 or c1 < 0:
            continue
        if zone.first_cell <= c0 <= zone.last_cell and zone.first_cell <= c1 <= zone.last_cell:
            local0 = int(c0 - zone.first_cell + 1)
            local1 = int(c1 - zone.first_cell + 1)
            pairs.add((local0, local1))
            pairs.add((local1, local0))
    return sorted(pairs)
