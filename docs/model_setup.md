# Model definition and implementation

## Scope

The case represents the midspan section of NASA C3X Run 145, configuration
4512. It is a steady two-dimensional RANS/CHT model sized for Ansys Fluent
Student. The repository applies Fluent and post-processes its exports; it does
not implement a CFD solver.

The gas passage and solid vane are solved. The ten cooling passages are present
in the solid geometry, but each internal wall uses a prescribed convection
condition instead of resolved coolant flow.

## Geometry and operating point

| Item | Value |
|---|---:|
| Cascade pitch | `117.730 mm` |
| Gas-solid interface | conformal |
| Periodicity | translational |
| Internal passages | `10` |
| Reference depth | `1.00 m` |
| Inlet total pressure | `403800 Pa` |
| Inlet total temperature | `792 K` |
| Inlet turbulence intensity | `6.5%` |
| Inlet turbulent viscosity ratio | `10` |
| Outlet static pressure | `236200 Pa` |
| Experimental exit Mach number | about `0.90` |
| Fine SST outlet Mach number | `0.901294` |

The direct fine-grid contour reaches about Mach `1.04` locally. Ideal-gas
density and the energy equation are therefore retained. Integrated mass and
heat reports are interpreted per unit span because the reference depth is
`1.00 m`.

The source curves are under `geometry/raw/`. The periodic-passage import is
rebuilt by:

```bash
python scripts/geometry/build_periodic_passage.py
```

## Governing model and boundary conditions

The gas domain solves steady conservation of mass, momentum and total energy
with SST `k-omega` closure. The solid solves steady conduction with the
archived temperature-dependent conductivity:

```text
nabla . (k_s(T) nabla T) = 0
k_s(T) = 6.811 + 0.020176 T  W/(m K)
```

The same C3X ASTM 310 correlation is reported in Table 2 of Prapamonthon et al.,
*Energies* 11(4), 1000 (2018),
[doi:10.3390/en11041000](https://doi.org/10.3390/en11041000).

The conformal gas-solid interface shares temperature and uses opposite heat
fluxes on its two sides. Each cooling-passage wall uses:

```text
q'' = h (T_bulk - T_wall)
Nu_D = C_r x 0.022 x Pr^0.5 x Re_D^0.8
h = Nu_D x k_air / D
```

NASA Appendix A, page 180 supplies each coolant bulk temperature and Reynolds
number. Passage diameters come from the retained geometry. Trompoukis et al.
(2021), Section 5,
[doi:10.3390/ijtpp6020020](https://doi.org/10.3390/ijtpp6020020), documents this
reduced 2D Nusselt correlation and states that `C_r` accounts for thermal
entrance-region effects, with values spanning approximately `1.03-1.12` across
the ten channels; that paper attributes `C_r` to Hylton et al. (1983). It does
not tabulate the ten individual per-hole assignments. The authoritative per-hole
values used by this repository are therefore the archived assignments in
`references/model_inputs/c3x_internal_convection_correction_factors.csv`. They
are not presented as a direct transcription of a table in Trompoukis et al.;
the publication supports the correlation, physical role and approximate range.
The values are kept unchanged to remain consistent with the released Fluent
states. Passage-specific uncertainty in `C_r` is not quantified.

CoolProp 8.0.0 supplies air properties at the bulk temperature and a fixed
`101325 Pa` property-evaluation pressure. This pressure is a preprocessing
convention for evaluating `cp`, viscosity, conductivity and Prandtl number; it
is not presented as a measured Run 145 coolant pressure or as a coolant-flow
boundary condition. The NASA Reynolds numbers are imposed independently of this
property-evaluation pressure, and sensitivity to the pressure choice is not
assessed. The generated inputs are stored in
`references/model_inputs/run145_4512_internal_convection.csv`.

## Material values

| Domain | Property | Fluent definition |
|---|---|---:|
| Solid | Density | `8030 kg/m3` |
| Solid | Specific heat | `473 J/(kg K)` |
| Solid | Conductivity | `6.811 + 0.020176 T` W/(m K) |
| Hot gas | Density | ideal gas |
| Hot gas | Molecular weight | `28.96 kg/kmol` |
| Hot gas | Specific heat | `1075 J/(kg K)` |
| Hot gas | Dynamic viscosity | `3.33e-05 Pa s` |
| Hot gas | Thermal conductivity | `0.05234 W/(m K)` |

The released Fluent state is the authoritative baseline-definition record for
these constants. Independent literature citations are asserted only where they
can be documented directly; the conductivity law, for example, independently
matches the published C3X ASTM 310 relation cited above. The machine-readable
baseline-definition and citation status is in
[`references/model_inputs/README.md`](../references/model_inputs/README.md).

The hot-gas specific heat, molecular viscosity and thermal conductivity are
retained as constant baseline inputs in the saved model. Their sensitivity is
not evaluated here, so the reported comparison should not be interpreted as
including uncertainty associated with those property choices.

## Mesh and near-wall resolution

| Mesh | Nodes | Cells | External wall faces |
|---|---:|---:|---:|
| Coarse | `15,186` | `14,657` | `311` |
| Medium | `24,548` | `23,781` | `473` |
| Fine | `45,999` | `44,760` | `819` |

The fine mesh uses a `1 micrometre` first layer and `30` inflation layers. Its
minimum orthogonal quality is `0.128589`, maximum equiangle skewness is
`0.802574`, maximum Fluent aspect ratio is `418.787`, and external-wall `y+`
min / mean / max is `0.01044 / 0.30441 / 0.45189`.

All-grid quality distributions and the missing GUI settings are in
[`meshing_recipe.md`](meshing_recipe.md).

## Fluent settings and run decisions

| Setting | Choice |
|---|---|
| Solver | steady, pressure based, coupled, 2D double precision |
| Operating pressure | `0 Pa` gauge |
| Energy equation | enabled |
| Pseudo-transient formulation | enabled |
| Coupled Courant number | `200` |
| Primary model | SST `k-omega` |
| Sensitivity model | Transition SST |
| Gradient | least-squares cell based |
| Pressure | second order |
| Density, momentum, energy and turbulence | second-order upwind |

The SST calculation used first-order schemes to establish a stable field, then
continued with second-order settings to iteration 236. The Transition SST case
started from that field. Its transition equations changed to bounded second
order at iteration 386, and the final state is iteration 556.

The saved Transition SST inlet uses `6.5%` turbulence intensity, a turbulent
viscosity ratio of `10` and intermittency `1.0`. Fluent derives the inlet
transition-onset momentum-thickness Reynolds number from its empirical
correlation based on inlet turbulence intensity. The extracted record is in
[`transition_sst_settings.csv`](../references/model_inputs/transition_sst_settings.csv).

The imposed `6.5%` inlet turbulence intensity is not preserved to the vane in
the archived baseline. The fine-grid freestream diagnostic gives a median
`Tu = 1.2473%` and `mu_t/mu = 7.851` in the `2-5 mm` bin immediately upstream
of the geometric leading edge. NASA documents `6.5%` as an average cascade
inlet turbulence level, not as a leading-edge target for this reduced domain.
The decay and its strong sensitivity to inlet turbulent-viscosity ratio are
documented in
[`studies/transition_sst_sensitivity/README.md`](../studies/transition_sst_sensitivity/README.md).
These diagnostics characterize model behavior; they do not establish an
experimentally verified transition location or a calibrated inlet state.

For these inlet settings and the present fine grid, Transition SST produced
similar pressure errors but larger wall-temperature and HTC errors. No coarse
or medium Transition SST cases were run.

## Theory-to-file map

| Calculation | Code | Input and output |
|---|---|---|
| Internal convection coefficients | `scripts/preprocess/build_internal_convection_inputs.py` | NASA coolant CSVs and geometry to `run145_4512_internal_convection.csv` |
| Pressure/suction wall labels | `scripts/common/surface_mapping.py` | wall coordinates and `run145_wall_surface_coordinate_reference.csv` |
| NASA interpolation and error metrics | `scripts/comparison/compare_run145.py` | rebuilt wall profiles to `results/processed/nasa_comparison/` |
| Mass and heat balances | `scripts/verification/check_global_balances.py` | Fluent reports to `results/processed/verification/` |
| Mesh-quality metrics | `scripts/verification/extract_restart_mesh_quality.py` | extracted Fluent CFF cases to mesh-quality CSVs |
| Solid temperature gradient | `scripts/postprocess/reconstruct_temperature_gradient.py` | solid temperatures and CFF adjacency to gradient CSV and figure |

## Thermal comparison convention

NASA thermal values are dimensionalized with `T_ref = 811 K` and
`HTC_ref = 1135 W/(m2 K)`. The CFD comparison uses the fluid-side heat flux:

```text
q_into_vane = -q_fluent,fluid-side
h_CFD = q_into_vane / (811 K - T_wall,CFD)
```

`811 K` is the NASA table reference temperature, not the Fluent inlet total
temperature of `792 K`.

## Model limits

The model does not predict coolant pressure drop, coolant temperature rise,
internal-passage development, film cooling, endwall flow, radiation, structural
response or unsteady wake passing. The reduced internal-convection closure also
does not quantify passage-specific uncertainty in the adopted `C_r`, `h` or
`T_bulk` inputs.
