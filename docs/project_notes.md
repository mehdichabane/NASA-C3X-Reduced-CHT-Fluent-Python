# Project notes

This page keeps the modeling decisions and development sequence that are useful
for understanding the project. Detailed setup, convergence, mesh and comparison
results stay in their dedicated documents.

The model was already substantially complete when the repository was first made
public, so the public Git history starts later than the CFD work. The retained
Fluent states and transcripts preserve several engineering steps, but not
reliable calendar dates for the pre-public simulations.

## Main modeling decisions

### 1. Reduced 2D CHT model

I kept the benchmark as a steady 2D midspan RANS/CHT calculation rather than
trying to represent the whole vane. The gas passage, solid conduction and the
fluid-solid interface are solved because pressure, wall temperature and
external HTC are the quantities compared with NASA Run 145.

A full 3D vane would add endwall flow, secondary-flow structures and spanwise
redistribution, but it would also be a different and much larger validation
problem. The present results therefore apply to the reduced midspan model and
are not used to make claims about full-vane performance.

The complete boundary-condition and material definition is in
[`model_setup.md`](model_setup.md).

### 2. Internal cooling as passage-specific convection

The ten cooling passages are present in the solid geometry, but coolant flow is
not solved. Each passage wall instead uses its own convection condition:

```text
q'' = h (Tbulk - Twall)
Nu_D = Cr * 0.022 * Pr^0.5 * Re_D^0.8
h = Nu_D * k_air / D
```

NASA supplies the passage Reynolds numbers, coolant bulk temperatures, geometry
and thermal-entry correction factors used to build these inputs. I preferred
this to one uniform internal HTC because it keeps the main passage-to-passage
variation without pretending that the reduced model predicts coolant pressure
loss or streamwise coolant development.

Because external wall temperature depends on this prescribed cooling as well as
on the gas-side model, I ran separate common-mode `h` and `Tbulk` sensitivity
families. Reducing all internal HTCs by 10% raises the mean external wall
temperature by about `6.1 K`. NASA's reported `+/-3%` internal-HTC magnitude was
later applied to the existing `h` sweep, giving about `+/-1.735 K` on mean wall
temperature.

The generated inputs and sensitivity results are under
[`../studies/internal_cooling_sensitivity/`](../studies/internal_cooling_sensitivity/).

### 3. SST as the baseline, Transition SST as a sensitivity case

SST `k-omega` remained the primary result after I compared it with Transition
SST on the fine grid. The two models give similar pressure-ratio errors, but the
thermal comparison changes substantially.

For SST, wall-temperature MAPE is about `1.45%` on the pressure side and
`2.00%` on the suction side, while HTC MAPE is about `7.80%` and `11.54%`.
Transition SST raises wall-temperature MAPE to about `6.35-6.41%` and HTC MAPE
to roughly `32-47%` on the same fine grid.

I then checked the inlet turbulence inputs because the transition response
depends strongly on how freestream turbulence decays before the vane. Changing
the inlet turbulent-viscosity ratio from `10` to `1` moved the suction-side
transition-like response and reduced external heat rate by about 20%. Changing
inlet turbulence intensity from `6.5%` to `8.3%` at viscosity ratio `10` had a
much smaller effect.

The retained Transition SST mesh is wall-resolved, but its wall-normal expansion
is about `1.20`, looser than I would choose for a transition-focused mesh. No
coarse or medium Transition SST cases were run. I therefore keep Transition SST
as a sensitivity result rather than treating its transition location as a
validated prediction.

The comparison is in [`nasa_comparison.md`](nasa_comparison.md), with the inlet
study under
[`../studies/transition_sst_sensitivity/`](../studies/transition_sst_sensitivity/).

### 4. Outlet-pressure adjustment

NASA Run 145 gives a nominal exit Mach of `0.90`, but I did not have a directly
tabulated Run 145 exit static pressure to impose at the CFD outlet.

My provisional second-order solution used `241200 Pa` and settled at a Fluent
mass-weighted outlet Mach of `0.88064076`. A local isentropic estimate gave
`236228.236 Pa`; I rounded the applied value to `236200 Pa` and continued the
solution. The next saved result gave `0.89951531`, and the retained fine SST
state with the same pressure reports `0.90129444`.

| Stage | Outlet pressure | Fluent outlet Mach |
|---|---:|---:|
| provisional state | `241200 Pa` | `0.88064076` |
| isentropic estimate | `236228.236 Pa` | — |
| applied setting | `236200 Pa` | `0.89951531` |
| retained fine SST state | `236200 Pa` | `0.90129444` |

I use the NASA exit Mach to set the operating point; the independent comparison
quantities remain surface pressure, wall temperature and external HTC. The
calculation is recorded in
[`outlet_pressure_selection.md`](outlet_pressure_selection.md).

### 5. What the three-grid study supports

The SST meshes contain `14,657`, `23,781` and `44,760` cells. On the fine grid,
maximum external-wall `y+` is about `0.452`; the first layer is `1 micrometre`
and there are 30 inflation layers.

Medium-to-fine changes in outlet Mach, mean wall temperature and external heat
rate are below `0.1%`, while the local trailing-edge profiles remain more
sensitive. I therefore report the three solutions as a mesh-sensitivity study,
not as a formal GCI result. The original meshing history was not preserved well
enough to establish a systematically similar refinement family.

If I repeated this part of the work, I would preserve one parameterized meshing
recipe and generate the full grid family from it before running the solutions.
Mesh dimensions, quality statistics and local profile changes are in
[`meshing_recipe.md`](meshing_recipe.md).

## Solver path preserved by the retained files

The restart release keeps four Fluent 26.1 states:

| Model / grid | Cells | Final iteration |
|---|---:|---:|
| coarse SST | `14,657` | `156` |
| medium SST | `23,781` | `161` |
| fine SST | `44,760` | `236` |
| fine Transition SST | `44,760` | `556` |

The case/data hashes are in
[`../fluent/restart_manifest.csv`](../fluent/restart_manifest.csv). The fine SST
state at iteration `236` is the baseline used for the reported NASA comparison.
Its last 20 iterations are the unchanged second-order confirmation window shown
in [`convergence_acceptance.md`](convergence_acceptance.md).

The Transition SST transcript preserves a clearer sequence. I started from the
accepted fine SST state, enabled Transition SST and used first-order convection
for `k`, `omega`, intermittency and `Re_theta_t` while the added equations
settled. A checkpoint was saved at iteration `386`; those four equations were
then changed to Second Order Upwind and the run continued to iteration `556`.
Iterations `537-556` form the final unchanged confirmation window.

The restart bundle also contains the Transition SST transcript, monitor history
and direct wall export. See [`../fluent/README.md`](../fluent/README.md) and the
raw exports under [`../data/fluent_exports/`](../data/fluent_exports/).

## Public repository timeline

The first public commit was `12a311d`, **“Publish NASA C3X Run 145 benchmark,”**
on 7 August 2026. That snapshot already contained the reduced RANS/CHT model,
three SST grids, fine Transition SST result, NASA comparisons, convergence and
conservation checks, Fluent exports, Python analysis and tests. The initial
restart release followed with the retained case/data states and checksums.

The main follow-up work after publication was the internal-cooling sensitivity
study, tighter mesh and Transition SST qualification, recovery of the outlet
pressure sequence and Transition SST scheme sequence, saved-state PyFluent
checks, and simplification of the documentation.

I do not assign dates or a coarse-to-medium-to-fine execution order to the
pre-public solves because the retained files do not support that chronology.
For future CFD extensions, I would preserve the branch, solver transcript,
checkpoints and raw exports while the work is being done instead of reconstructing
those details afterwards.

The current reproducibility boundary is described in
[`reproducibility.md`](reproducibility.md): the Python analysis is rebuilt in CI,
and the released Fluent states can be reopened and queried, but they are not a
full initialization-to-final solver replay.
