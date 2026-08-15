# Model definition and implementation

## Scope

The case represents the midspan section of NASA C3X Run 145 (code 4512). It is
a steady two-dimensional RANS/CHT model sized for Ansys Fluent Student. Fluent
solves the CFD case; the repository provides the setup record, preprocessing and
post-processing workflow.

The gas passage and solid vane are solved. The ten cooling passages are present
in the solid geometry, but each internal wall uses a prescribed convection
condition instead of resolved coolant flow.

## Geometry and reporting conventions

| Item | Value | Status / source |
|---|---:|---|
| Cascade pitch | `117.730 mm` | NASA-CR-168015 Table IV (`11.773 cm`) |
| Gas-solid interface | conformal | Fluent model implementation |
| Periodicity | translational | Fluent model implementation using the NASA pitch |
| Internal passages | `10` | NASA C3X geometry / Figure 7 |
| Reference depth | `1.00 m` | 2D Fluent reporting convention |

## Run 145 external operating point and Fluent boundary inputs

The `Role` and `Provenance` columns distinguish NASA reference quantities,
imposed Fluent inputs, operating-point adjustments and computed results. A
machine-readable record is stored in
[`run145_4512_external_boundary_provenance.csv`](../references/model_inputs/run145_4512_external_boundary_provenance.csv).

| Quantity | Value used / reported | Role | Provenance |
|---|---:|---|---|
| Inlet total pressure | `403800 Pa` | imposed pressure-inlet input | Rounded NASA Table IX `PTI = 58.57 psia` (`403825.9 Pa`) |
| Inlet total temperature | `792 K` | imposed pressure-inlet input | NASA Table IX Run 145 (code 4512) |
| Experimental inlet Mach | `0.16` | reference only | NASA Table IX operating-point reference |
| Inlet turbulence intensity | `6.5%` | imposed turbulence input | NASA Table IX average inlet `Tu` |
| Inlet turbulent viscosity ratio | `10` | imposed turbulence-model input | Released Fluent setup; Fluent modelling input |
| Outlet static pressure | `236200 Pa` | imposed pressure-outlet input | Operating-point adjustment to nominal NASA Run 145 `M2 = 0.90`; see `outlet_pressure_selection.md` |
| NASA exit Mach | `0.90` | nominal operating-point anchor | NASA Table IX; pressure-derived from measured inlet total pressure and average measured exit-plane static pressure |
| Fine SST outlet Mach | `0.901294` | Fluent operating-point consistency result | `surface-massavg` of local Mach on the outlet with the retained `236200 Pa` setting |

NASA Table IX reports Run 145 (code 4512) as `PTI = 58.57 psia`,
`TTI = 792 K`, `M1 = 0.16`, `M2 = 0.90` and `Tu = 6.5%`. The Fluent pressure-
inlet total pressure of `403800 Pa` is a `0.0064%` rounding of the NASA value
`403825.9 Pa`.

With Fluent operating pressure set to `0 Pa`, the pressure outlet was set to
`236200 Pa` from the nominal Run 145 exit-Mach target. NASA `M2` is pressure-
derived, whereas the Fluent report is a mass-weighted average of local outlet
Mach, so this value is used as an operating-point check. The independent NASA
comparison uses surface pressure, wall temperature and external HTC. The
pressure-adjustment history is in
[`outlet_pressure_selection.md`](outlet_pressure_selection.md).

The inlet turbulent-viscosity ratio `10` is a retained Fluent modelling input.
Fluent's intensity/viscosity-ratio specification uses `10` as the default value;
its influence is examined in the Transition SST sensitivity study.

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
k_s(T) = 6.811 + 0.020176 T  W/(m·K)
```

The same conductivity law is reported in Table 2 of Prapamonthon et al.,
*Energies* 11(4), 1000 (2018),
[doi:10.3390/en11041000](https://doi.org/10.3390/en11041000).

The conformal gas-solid interface shares temperature and uses opposite heat
fluxes on its two sides. Each cooling-passage wall uses:

```text
q'' = h (T_bulk - T_wall)
Nu_D = C_r x 0.022 x Pr^0.5 x Re_D^0.8
h = Nu_D x k_air / D
```

The source chain for this reduced internal-convection closure is direct in
NASA-CR-168015. The heat-transfer measurement section gives the Nusselt
correlation above, defines `C_r` as the thermal-entry correction to the
fully-developed smooth-pipe expression, and states that its experimental range
is approximately `1.03–1.12`. NASA attributes that correction to Ref. 22,
Crawford and Kays, *Convective Heat and Mass Transfer* (1980).

NASA Figure 7 (report p. 16) tabulates the C3X passage geometry and per-hole
`C_r` values. The repository transcribes `C_r = 1.118` for holes 1–7, `1.056`
for holes 8–9 and `1.025` for hole 10 directly from that primary source.

NASA Appendix A, report p. 181, supplies each Run 145 coolant bulk temperature
and passage Reynolds number. CoolProp 8.0.0 supplies air properties at the bulk
temperature and `101325 Pa` for preprocessing. The NASA Reynolds numbers are
imposed independently; `101325 Pa` is used only for the property evaluation.
Sensitivity to this preprocessing pressure is not assessed. The generated
inputs are stored in
`references/model_inputs/run145_4512_internal_convection.csv`.

## Material values

| Domain | Property | Fluent definition |
|---|---|---:|
| Solid | Density | `8030 kg/m³` |
| Solid | Specific heat | `473 J/(kg·K)` |
| Solid | Conductivity | `6.811 + 0.020176 T` W/(m·K) |
| Hot gas | Density | ideal gas |
| Hot gas | Molecular weight | `28.96 kg/kmol` |
| Hot gas | Specific heat | `1075 J/(kg·K)` |
| Hot gas | Dynamic viscosity | `3.33e-05 Pa·s` |
| Hot gas | Thermal conductivity | `0.05234 W/(m·K)` |

The values above reproduce the material definitions in the released Fluent
state. Independent C3X and prior-C3X literature matches for several constants
are summarised in
[`references/model_inputs/README.md`](../references/model_inputs/README.md).
These are consistency checks on the archived setup. The hot-gas specific heat,
molecular viscosity and thermal conductivity remain constant baseline inputs;
their sensitivity is not evaluated here.

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

All-grid quality distributions, realised-mesh diagnostics and the missing GUI
generation settings are in [`meshing_recipe.md`](meshing_recipe.md).

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
| Final density, momentum and energy convection | second-order upwind |

The SST calculation used first-order schemes to establish a stable field, then
continued with second-order settings to iteration 236. Transition SST (4 eqn)
was then enabled from that accepted state. The retained Fluent transcript shows
that the Transition SST warm-start state was written before the four
`turbulence/transition` transport-equation schemes were deliberately changed.
Immediately afterward, `k`, `omega`, intermittency and transition
momentum-thickness Reynolds number were set to Fluent scheme index `0` (First
Order Upwind) for stabilisation and retained at first order through iteration
386. After the first-order iteration-386 checkpoint was written, those same four
equations were changed to scheme index `1` (Second Order Upwind). The
iteration-386 solution was written again before further iteration and then
continued with the second-order settings to iteration 556. Pressure, density,
momentum and energy retained their existing second-order settings throughout
this Transition SST chronology.

The saved Transition SST inlet uses `6.5%` turbulence intensity, a turbulent
viscosity ratio of `10` and intermittency `1.0`. NASA supplies the `6.5%`
average inlet turbulence level; viscosity ratio `10` and intermittency `1.0` are
retained Fluent model settings. Fluent derives the inlet transition-onset
momentum-thickness Reynolds number from its empirical correlation based on inlet
turbulence intensity. The extracted record is in
[`transition_sst_settings.csv`](../references/model_inputs/transition_sst_settings.csv).

In the archived baseline, the imposed `6.5%` inlet turbulence intensity decays
to a median `Tu = 1.2473%` with `mu_t/mu = 7.851` in the `2–5 mm` bin immediately
upstream of the geometric leading edge. NASA reports `6.5%` as the average C3X
cascade inlet level. The decay and its sensitivity to inlet turbulent-viscosity
ratio are documented in
[`studies/transition_sst_sensitivity/README.md`](../studies/transition_sst_sensitivity/README.md),
where the extracted response locations are treated as fine-grid model
diagnostics.

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

NASA thermal values are dimensionalised with `T_ref = 811 K` and
`HTC_ref = 1135 W/(m²·K)`. The CFD comparison uses the fluid-side heat flux:

```text
q_into_vane = -q_fluent,fluid-side
h_CFD = q_into_vane / (811 K - T_wall,CFD)
```

`811 K` is the NASA table reference temperature; the Fluent inlet total
temperature is `792 K`.

## Model limits

The model does not predict coolant pressure drop, coolant temperature rise,
internal-passage development, film cooling, endwall flow, radiation, structural
response or unsteady wake passing. The reduced internal-convection closure also
does not quantify passage-specific uncertainty in the adopted `C_r`, `h` or
`T_bulk` inputs.
