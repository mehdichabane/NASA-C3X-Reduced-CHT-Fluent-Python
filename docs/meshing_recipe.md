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

For the local comparison, both meshes are interpolated onto the same `s/L`
coordinate. The reported range-normalized MAE is

`100 x MAE / (max(phi_fine) - min(phi_fine))`

evaluated over the same surface and region. It is a profile-shape diagnostic,
not a pointwise relative error and not a percentage error in the physical
quantity itself. All trailing-edge ranges listed below are non-zero, so the
zero-range fallback implemented in the post-processing is not used here.

| Surface | Quantity | Medium-to-fine MAE | MAE / local fine-grid range |
|---|---|---:|---:|
| Pressure | `p_s/p_t,in` | `0.00764` | `8.76%` |
| Pressure | Wall temperature | `0.927 K` | `4.84%` |
| Pressure | Heat flux | `4.199 kW/m2` | `4.06%` |
| Pressure | HTC | `42.99 W/(m2 K)` | `3.87%` |
| Suction | `p_s/p_t,in` | `0.00258` | `4.56%` |
| Suction | Wall temperature | `0.943 K` | `3.77%` |
| Suction | Heat flux | `1.053 kW/m2` | `1.65%` |
| Suction | HTC | `13.06 W/(m2 K)` | `2.74%` |

For example, the pressure-side `8.76%` value means that the medium-to-fine
pressure-ratio MAE is `0.00764`, which is `8.76%` of the fine-grid
pressure-ratio range within the last `5%` of that surface. It does **not** mean
that the medium-grid pressure is locally `8.76%` different from the fine-grid
pressure.

The full local summary is
`results/processed/mesh_sensitivity/run145_three_grid_local_profile_summary.csv`.
The global results therefore do not imply uniform local grid insensitivity.

The post-processing also computes Richardson/GCI screening diagnostics for the
three global quantities using an effective two-dimensional spacing proportional
to `1/sqrt(N_cells)`. The machine-readable output therefore contains observed
order, Richardson-extrapolated value, fine/medium GCI and asymptotic-ratio
fields. These values are retained as exploratory diagnostics only; they are not
accepted or reported here as formal discretization uncertainties. The retained
meshing record cannot establish that the three meshes form a systematically
similar refinement family with the same generation parameters and controlled
reference-spacing ratios. The missing sizing, bias, inflation-growth and
meshing-method records listed below are precisely why the project reports a
three-grid sensitivity rather than a formal asymptotic GCI assessment.

## Transition SST mesh qualification

The fine mesh satisfies the usual near-wall criterion for the Transition SST
model with `y+_max = 0.45189`. Fluent 26.1 also recommends a wall-normal
expansion ratio below `1.1` and, for a turbine blade, roughly `100-150`
streamwise cells on each side as best-practice guidance for transition
prediction. See the Fluent Theory Guide section on
[Transition SST mesh requirements](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/flu_th/flu_th_sec_turb_sst_grid.html).

The original inflation growth rate, edge-division counts, bias factors and other
mesh-generation settings were not retained, so this repository cannot
demonstrate that the accepted fine mesh satisfies all of those
Transition-SST-specific recommendations. No coarse or medium Transition SST
solutions were run either. Consequently, the extracted transition-like response
locations are treated as fine-grid model-response diagnostics, not as
Transition-SST grid-converged locations.

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
