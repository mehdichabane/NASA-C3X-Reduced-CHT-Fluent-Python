# Scripts

| Script | Inputs | Main outputs |
|---|---|---|
| `preprocess/build_internal_convection_inputs.py` | NASA coolant table + passage diameters + `C_r` + CoolProp 8.0.0 | reproducible ten-passage `Nu_D` and `h` model-input table |
| `geometry/build_periodic_passage.py` | raw NASA geometry CSVs | SpaceClaim periodic-passage import |
| `postprocess/analyze_convergence.py` | physical-monitor history | convergence CSV and figures |
| `postprocess/analyze_residuals.py` | full SST residual history | SST residual summaries and figures |
| `postprocess/analyze_transition_sst.py` | direct Transition SST wall, monitor, residual and global-check exports | Transition convergence, wall-export and `y+` checks, convergence figures |
| `postprocess/reconstruct_temperature_gradient.py` | solid temperatures + CFF-derived adjacency | topology-based `∇T`, fit diagnostics and figure |
| `postprocess/analyze_mesh_sensitivity.py` | three wall exports | mapped profiles, local/global sensitivity tables and figures |
| `postprocess/plot_mesh_quality_distribution.py` | committed CFF threshold audit | threshold/worst-cell mesh-quality figure |
| `postprocess/crop_flow_field_figures.py` | unannotated direct Fluent contour PNGs | tightly cropped, labelled pressure and Mach figures |
| `postprocess/build_comparison_profiles.py` | direct SST and Transition SST wall exports + coordinate reference | both processed comparison profiles |
| `verification/extract_restart_mesh_quality.py` | release-bundle `.cas.h5` files | all-grid extrema, threshold distributions, worst-cell coordinates + solid adjacency |
| `verification/check_mesh_summary.py` | committed mesh-quality/sensitivity tables | consistency checks |
| `verification/check_global_balances.py` | final Fluent reports | mass/interface/solid-energy verification |
| `verification/check_sensitivity_studies.py` | committed internal-cooling and Transition SST case matrices/summary tables | cross-study baseline, case-coverage and response-consistency checks |
| `verification/replay_saved_state_reports.py` | released `.cas.h5/.dat.h5` pair + local Fluent 26.1 + pinned PyFluent | optional 2D double-precision recomputation of existing scalar report definitions to stdout/JSON |
| `verification/plot_wall_yplus.py` | fine wall export | wall-resolution figure and statistics |
| `comparison/compare_run145.py` | rebuilt CFD profiles + NASA tables | pointwise comparison, error metrics and figures |

`python scripts/run_all.py` executes the Git-contained analysis. `pytest -q`
tests coordinate mapping, manufactured-field gradients, mesh-quality formulas,
profile rebuilding, direct Transition SST export consistency, convergence, NASA
comparison metrics, the saved-state audit launch configuration and the committed
sensitivity-study headline relationships.

The sensitivity-study consistency check does not rerun Fluent. It protects the
committed campaign matrices and summaries against accidental cross-case or
headline-result inconsistencies.

The optional `replay_saved_state_reports.py` helper is deliberately not part of
`run_all.py` or CI because it requires a locally installed, licensed Fluent
26.1 session. Its separate dependency is pinned in `requirements-fluent.txt` as
`ansys-fluent-core==0.40.2`. The helper requests Fluent `26.1.0` explicitly in
2D double precision and checks the running version before reading the saved
state. It does not replay the solve from initialization.

The restart binaries are not stored in Git, so CFF mesh extraction is run
after the bundle has been downloaded and extracted:

```text
python scripts/verification/extract_restart_mesh_quality.py PATH_TO_EXTRACTED_RESTART_DIRECTORY
```

## Optional preprocessing dependency

Install `requirements-preprocess.txt` to rebuild or check the internal-convection
inputs:

```text
python scripts/preprocess/build_internal_convection_inputs.py --check
```

`requirements.txt` covers the main workflow. The CI installs both requirement
files so the CoolProp check also runs.

## Optional Fluent dependency

Install the pinned PyFluent dependency separately when using the saved-state
audit helper:

```text
python -m pip install -r requirements-fluent.txt
```

This dependency is intentionally not installed in CI because the CI environment
does not provide a licensed Fluent executable.
