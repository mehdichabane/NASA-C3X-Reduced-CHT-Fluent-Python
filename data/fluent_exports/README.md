# Fluent exports

The Git tree contains compact Fluent exports used by the Python workflow. Case
and data binaries are distributed separately in the restart bundle.

| Group | Main files | Purpose |
|---|---|---|
| Fine SST convergence | `run145_sst_convergence_monitors.csv`, residual CSVs | monitor and residual figures |
| Fine SST checks | `run145_sst_global_checks.csv`, mesh audit files | mass, heat, `y+` and topology checks |
| Solid field | `run145_sst_solid_cell_temperature.csv`, adjacency CSV | temperature-gradient reconstruction |
| Transition SST | `transition_sst/` | direct wall profile, monitors, residuals and final checks |
| Three-grid SST | `mesh_sensitivity/` | wall profiles, `mesh_summary.csv`, global sensitivity and mesh quality |
| Figure sources | `figure_sources/` | unannotated Fluent contours and the direct residual capture |

| Mesh / model | Final iteration |
|---|---:|
| Coarse SST | `156` |
| Medium SST | `161` |
| Fine SST | `236` |
| Fine Transition SST | `556` |

The calculation uses a `1.00 m` reference depth, so integrated mass and heat
reports are interpreted per unit span.

The restart filenames and SHA-256 values are listed in
[`fluent/restart_manifest.csv`](../../fluent/restart_manifest.csv).

`scripts/postprocess/crop_flow_field_figures.py` crops and labels the retained
Fluent contour images without changing contour values or limits.
