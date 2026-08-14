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

`requirements-fluent.txt` pins `ansys-fluent-core==0.40.2`. The helper requests
Fluent `26.1.0` explicitly in **2D double precision with `ui_mode="no_gui"`**,
checks the reported running Fluent version, and records the
version/dimension/precision/UI mode in its JSON/stdout audit payload. This
prevents a machine with a newer Fluent installation from silently auditing the
release with that newer version and keeps the audit headless.

The helper also requires the conventionally matching `.dat.h5` file beside the
case file before it launches Fluent. The JSON records SHA-256 hashes of both
input files so a retained audit can be matched directly to
[`restart_manifest.csv`](restart_manifest.csv).

The default report names are `fine_external_heat_rate`,
`fine_wall_temperature_avg` and `fine_mach_outlet`; use `--report` to override
them for another saved case. To retain local audit artifacts explicitly, the
recommended fine-grid commands are:

```text
python scripts/verification/replay_saved_state_reports.py c3x_run145_nasa_exact_fine_SST_final_iter236.cas.h5 --output run145_sst_fine_saved_state_audit.json
python scripts/verification/replay_saved_state_reports.py c3x_run145_transition_sst_fine_final_iter556.cas.h5 --output run145_transition_sst_fine_saved_state_audit.json
```

Run those commands from a directory where each matching `.dat.h5` file remains
beside its `.cas.h5` file, or provide the corresponding full case-file path.

The launch configuration and local hash helpers are unit-tested in CI with a
fake PyFluent launcher. Until JSON from an actual licensed Fluent 26.1 execution
is committed, the repository does not claim that this optional live audit has
already been run and archived.

This helper requires a locally installed, licensed Fluent 26.1 environment and
is not executed in GitHub Actions. It is a saved-state audit only: it does not
regenerate the mesh, initialize the solver, replay iterations, export the full
wall data set, or establish final-state equivalence from initialization.

## Transition SST restart

The fine-grid Transition SST case starts from the accepted fine SST state at
iteration 236. The retained Fluent transcript records the solver chronology
rather than leaving it to filename inference:

- Transition SST (4 eqn) is enabled from the iteration-236 fine SST state;
- the Transition SST warm-start case/data pair is written before the deliberate
  stabilization change;
- `k`, `omega`, intermittency and transition momentum-thickness Reynolds number
  are then changed to Fluent scheme index `0` (First Order Upwind) and retained
  at first order through iteration 386;
- after writing the first-order iteration-386 checkpoint, those same four
  equations are changed to scheme index `1` (Second Order Upwind);
- the iteration-386 state is written again before any further iteration, then
  continued with those second-order settings to iteration 556;
- iteration 536 is retained as a converged candidate and iterations 537-556 form
  the final unchanged confirmation window.

The [Fluent 2026 R1 discretization-scheme index table](https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/flu_tcl/x1-1000010.html)
identifies index `0` as First Order Upwind, index `1` as Second Order Upwind and
index `12` as Second Order. These labels are therefore tied to the retained
scheme indices rather than inferred from the filenames.

Pressure interpolation and the density, momentum and energy convective schemes
remain at their existing second-order settings throughout the retained
Transition SST chronology. The saved `fine_mach_outlet` report definition is a
`surface-massavg` of Mach number on the outlet.

Only the fine grid was run with Transition SST. The transcript, monitor file and
direct wall export are included in the restart bundle; the CSV exports used by
the Python workflow are under `data/fluent_exports/transition_sst/`. The
original Workbench/Ansys Meshing construction history is not in the bundle, but
the realized Fluent CFF mesh and final solver state are preserved.
