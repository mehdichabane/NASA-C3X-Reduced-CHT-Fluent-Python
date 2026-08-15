# Live Fluent saved-state audits

These JSON files archive one-shot local executions of
`scripts/verification/replay_saved_state_reports.py` against the two released
fine-grid solver states.

The helper launched Fluent `26.1.0` in 2D double precision with
`ui_mode="no_gui"`, read the matching released `.cas.h5/.dat.h5` pair and
recomputed three report definitions already stored in each saved case:

- `fine_external_heat_rate`;
- `fine_wall_temperature_avg`;
- `fine_mach_outlet`.

The recorded case/data SHA-256 digests match the corresponding fine SST and fine
Transition SST entries in `fluent/restart_manifest.csv`. The absolute Windows
paths in the JSON files are incidental execution metadata; the input hashes and
canonical filenames establish solver-state identity.

| Saved state | External heat rate [W] | Mean wall temperature [K] | Mass-weighted outlet Mach |
|---|---:|---:|---:|
| fine SST, iter 236 | `35819.60242176461` | `655.619216610248` | `0.9012944409738727` |
| fine Transition SST, iter 556 | `28548.27415186197` | `608.87899709921` | `0.9033510682539843` |

These files document saved-state report reproducibility only. Mesh generation,
iteration replay and sensitivity reruns are outside this archive.
