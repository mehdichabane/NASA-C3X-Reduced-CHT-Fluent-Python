# Three-grid mesh record

## Retained geometry and meshes

The repository contains:

- NASA C3X profile coordinates;
- ten internal-passage centre and diameter definitions;
- a translational pitch of `0.117730 m`;
- SpaceClaim point-curve imports;
- the accepted Fluent CFF meshes in the separate restart bundle.

The passage boundary can be regenerated with:

```bash
python scripts/geometry/build_periodic_passage.py
```

| Mesh | Nodes | Cells | External wall faces | Final SST iteration |
|---|---:|---:|---:|---:|
| Coarse | `15,186` | `14,657` | `311` | `156` |
| Medium | `24,548` | `23,781` | `473` | `161` |
| Fine | `45,999` | `44,760` | `819` | `236` |

The fine mesh uses a `1 micrometre` first layer and `30` inflation layers. Its
external-wall `y+` minimum, area-weighted mean and maximum are
`0.01044 / 0.30441 / 0.45189`.

## Quality data

`scripts/verification/extract_restart_mesh_quality.py` reads the CFF cases and
calculates equiangle skewness, orthogonal quality and Fluent aspect ratio.

| Mesh | OQ `< 0.10` | Skewness `> 0.75` | AR `> 100` | AR `> 500` | AR `> 1000` |
|---|---:|---:|---:|---:|---:|
| Coarse | `19 (0.130%)` | `0` | `4,198 (28.642%)` | `1,403 (9.572%)` | `243 (1.658%)` |
| Medium | `14 (0.059%)` | `0` | `5,177 (21.769%)` | `927 (3.898%)` | `0` |
| Fine | `0` | `1 (0.002%)` | `6,552 (14.638%)` | `0` | `0` |

The high aspect ratios occur mainly in anisotropic hot-gas cells. Mesh quality
is considered together with positive volumes, periodicity, wall resolution,
convergence, conservation and three-grid solution sensitivity.

![Mesh-quality distributions](../results/figures/mesh/run145_mesh_quality_distribution.svg)

The machine-readable table is
`data/fluent_exports/mesh_sensitivity/mesh_quality_distribution_all_grids.csv`.

## Global and trailing-edge sensitivity

Medium-to-fine changes in outlet Mach number, mean wall temperature and
external heat rate are below `0.1%`. Local profiles remain more sensitive in
the last `5%` of surface distance near the trailing edge.

| Surface | Quantity | Medium-to-fine normalized MAE |
|---|---|---:|
| Pressure | `p/p_t` | `8.76%` |
| Pressure | Wall temperature | `4.84%` |
| Pressure | Heat flux | `4.06%` |
| Pressure | HTC | `3.87%` |
| Suction | `p/p_t` | `4.56%` |
| Suction | Wall temperature | `3.77%` |
| Suction | HTC | `2.74%` |

The full local summary is
`results/processed/mesh_sensitivity/run145_three_grid_local_profile_summary.csv`.
The global results therefore do not imply uniform local grid insensitivity.

## Missing setup information

These original GUI settings were not saved:

- inflation growth rate;
- global and local element sizes;
- edge-division counts and bias factors;
- curvature and proximity controls;
- meshing method and smoothing settings;
- operation order in SpaceClaim and Ansys Meshing;
- the original Workbench project history.

The saved meshes can be reopened and inspected, but they cannot be recreated
bit-for-bit from the source curves alone.
