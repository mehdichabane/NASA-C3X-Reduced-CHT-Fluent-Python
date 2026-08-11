# Fluent restart files

The separate archive `NASA-C3X-Fluent-restart-files.zip` contains matching
Fluent 26.1 case/data pairs for:

- coarse SST, iteration 156;
- medium SST, iteration 161;
- fine SST, iteration 236;
- fine Transition SST, iteration 556.

It also contains `SHA256SUMS.txt`, the Transition SST transcript, monitor file
and direct wall export. Exact filenames, cell counts and hashes are listed in
[`restart_manifest.csv`](restart_manifest.csv).

## Reopen a saved state

1. Extract the archive completely.
2. Keep each case/data pair in the same directory with filenames unchanged.
3. Start Fluent 26.1 in 2D, double precision.
4. Select `File > Read > Case & Data`.
5. Check the cell count and final iteration against the manifest.

The word `ACCEPTED` remains in the coarse and medium filenames because the data
files refer to those case names.

The bundle supports reopening the saved states and auditing the SST CFF meshes.
It does not reproduce the original interactive meshing sequence or demonstrate
that a new initialization converges to the saved fine SST state.

## Optional PyFluent saved-state report audit

A small optional helper can reopen a saved case/data pair through PyFluent and
recompute report definitions that already exist in the saved case. Install the
separate pinned solver-side dependency first:

```text
python -m pip install -r requirements-fluent.txt
python scripts/verification/replay_saved_state_reports.py PATH_TO_FINE_CASE.cas.h5
```

`requirements-fluent.txt` pins `ansys-fluent-core==0.40.2`. The helper then
requests Fluent `26.1.0` explicitly in **2D double precision**, checks the
reported running Fluent version, and records the version/dimension/precision in
its JSON/stdout audit payload. This prevents a machine with a newer Fluent
installation from silently auditing the release with that newer version.

The default report names are `fine_external_heat_rate`,
`fine_wall_temperature_avg` and `fine_mach_outlet`; use `--report` to override
them for another saved case. `--output result.json` writes the returned values
to JSON as well as stdout.

This helper requires a locally installed, licensed Fluent 26.1 environment and
is not executed in GitHub Actions. It is a saved-state audit only: it does not
regenerate the mesh, initialize the solver, replay iterations, export the full
wall data set, or establish final-state equivalence from initialization.

## Transition SST restart

The fine-grid Transition SST case starts from the fine SST state at iteration
236. The transition equations use first-order upwind during stabilization and
bounded second order from iteration 386. Iterations 537-556 form the final
unchanged window. Only the fine grid was run with Transition SST. The transcript,
monitor file and direct wall export are included in the restart bundle; the CSV
exports used by the Python workflow are under
`data/fluent_exports/transition_sst/`.
