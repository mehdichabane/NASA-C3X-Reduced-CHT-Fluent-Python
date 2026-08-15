# Modeling notes

These are the five modeling choices I would expect to defend in a technical
interview. I have kept this page deliberately short; the detailed setup,
provenance, convergence checks and validation plots are in the linked project
documents.

This is still a reduced NASA C3X benchmark, not a full-vane or complete ASME
V&V 20 validation.

## Why I kept the model 2D

The calculation is a steady 2D midspan RANS/CHT model. That was a deliberate
scope choice rather than an attempt to represent the whole vane.

I wanted to keep the gas-side aerodynamics, the solid vane and the conjugate
thermal coupling, because pressure, wall temperature and HTC are the quantities
I compare with the NASA experiment. A full 3D vane would add endwalls,
secondary flows and spanwise redistribution, but it would also turn this into a
much larger problem and move it away from the reduced benchmark I could qualify
properly with Fluent Student.

The consequence is straightforward: I do not use the midspan agreement to make
claims about endwall flow or full-vane performance. If the quantity of interest
became genuinely three-dimensional, I would treat a 3D model as a new study with
its own mesh and validation work rather than as a simple extension of these
error metrics.

The retained assumptions and exclusions are listed in
[`docs/model_setup.md`](docs/model_setup.md).

## Internal cooling: `h/Tbulk` instead of solved coolant passages

The ten cooling passages are present in the solid geometry, but I do not solve
the coolant flow inside them. Each passage wall uses its own convection
condition based on the NASA passage data:

```text
q'' = h (Tbulk - Twall)
Nu_D = Cr * 0.022 * Pr^0.5 * Re_D^0.8
h = Nu_D * k_air / D
```

I preferred this to one uniform internal HTC because the experiment already
provides passage-specific Reynolds numbers, coolant temperatures and thermal
entry information. It preserves the main spatial variation in the internal
thermal forcing without pretending that the model predicts coolant pressure
loss or passage development.

This choice matters when interpreting wall temperature. The external thermal
result is not only a turbulence-model response; it also depends on solid
conduction and the prescribed internal cooling. That is why I ran the separate
`h` and `Tbulk` sensitivity study instead of treating the internal boundary as
exact. For example, the existing common-mode `h` sweep shows that reducing all
internal HTCs by 10% raises the mean external wall temperature by about 6.1 K.
NASA's reported ±3% magnitude for the internal-HTC calculation was later mapped
onto that same family as a sensitivity envelope, not as a formal probabilistic
uncertainty.

The generated passage inputs and the sensitivity results are in
[`docs/model_setup.md`](docs/model_setup.md) and
[`studies/internal_cooling_sensitivity/`](studies/internal_cooling_sensitivity/).

## Why SST stayed the baseline

I kept SST `k-omega` as the primary result after comparing it with Transition
SST on the fine grid. Transition SST did not simply give a different transition
location; it changed the thermal result substantially while leaving the pressure
comparison fairly similar.

For the retained fine solutions, SST gives wall-temperature MAPE of about
`1.45%` on the pressure side and `2.00%` on the suction side, with HTC MAPE of
about `7.80%` and `11.54%`. Transition SST keeps pressure-ratio errors in roughly
the same range but gives much larger thermal errors: wall-temperature MAPE is
about `6.35-6.41%`, and HTC MAPE rises to roughly `32-47%`.

I did not take that as proof that transition physics are unimportant. I checked
the inlet turbulence inputs because the transition model depends on how the
freestream turbulence decays between the inlet and the vane. Changing the inlet
turbulent-viscosity ratio from 10 to 1 moved the transition-like suction-side
response strongly and reduced the external heat rate by about 20%, whereas
changing inlet turbulence intensity from 6.5% to 8.3% at the baseline viscosity
ratio barely moved the global result.

There is also a mesh caveat. The retained wall resolution is low-`y+`, but the
inflation growth is about `1.20`, which is looser than the Fluent guidance I
would use for a transition-focused mesh. For that reason I treat Transition SST
as a model-sensitivity case, not as a calibrated or disproved model.

I would revisit the baseline only after rebuilding a transition-qualified mesh
and running at least a medium/fine Transition SST comparison with better control
of inlet-to-leading-edge turbulence. The detailed numbers are in
[`docs/nasa_comparison.md`](docs/nasa_comparison.md) and
[`studies/transition_sst_sensitivity/README.md`](studies/transition_sst_sensitivity/README.md).

## Matching the Run 145 operating point

NASA defines Run 145 with an exit Mach of about `0.90`, but I did not have a
directly tabulated Run 145 exit static pressure that I could simply impose at
the CFD boundary.

My provisional pressure outlet was `241200 Pa`; that gave a Fluent
mass-weighted outlet Mach of `0.88064076`. I used a local isentropic estimate to
move the back pressure to `236228.236 Pa`, rounded the applied value to
`236200 Pa`, and obtained an outlet Mach close to the target. The retained fine
SST state reports `0.901294`.

I do **not** count that agreement as an independent validation result. The NASA
`M2` value is pressure-derived, while my Fluent report is a mass-flux-weighted
average of the local computed Mach field, and I used the NASA value to set the
operating point in the first place. The independent experimental comparisons
remain surface pressure, wall temperature and external HTC.

The adjustment sequence is preserved in
[`docs/outlet_pressure_selection.md`](docs/outlet_pressure_selection.md).

## What the mesh study actually tells me

The fine SST mesh has `44,760` cells, a `1 micrometre` first layer and 30
inflation layers. The retained external-wall `y+` has a maximum of about
`0.452`, so the first-cell height achieved the wall-resolved SST target I was
aiming for.

That does not mean the complete solution is mesh-independent. I solved coarse,
medium and fine SST meshes with `14,657`, `23,781` and `44,760` cells. The
medium-to-fine changes in global quantities such as outlet Mach, mean wall
temperature and external heat rate are below `0.1%`, but the local
trailing-edge profiles remain noticeably more sensitive.

I therefore report this as a **three-grid sensitivity study**, not a formal GCI
result. The original Workbench/Ansys Meshing history was not preserved well
enough to prove that the three retained meshes form a systematically similar
refinement family. Running a Richardson/GCI formula on three solutions does not
repair that missing evidence.

If I redid this part of the project, the first thing I would preserve is the
actual meshing recipe and generate the grid family systematically from it. That
would let the discretization study support a stronger claim than the current
screening diagnostics.

Mesh dimensions, local profile changes and the limits of the retained record are
in [`docs/meshing_recipe.md`](docs/meshing_recipe.md).

## Where the rest of the evidence lives

For the full setup and source chain, see [`docs/model_setup.md`](docs/model_setup.md).
Convergence and balance checks are in
[`docs/convergence_acceptance.md`](docs/convergence_acceptance.md), the NASA
comparison is in [`docs/nasa_comparison.md`](docs/nasa_comparison.md), and the
reproducibility boundary is described in
[`docs/reproducibility.md`](docs/reproducibility.md).

The point of this page is only to record the modeling choices I would want to be
able to explain without reading from the repository.