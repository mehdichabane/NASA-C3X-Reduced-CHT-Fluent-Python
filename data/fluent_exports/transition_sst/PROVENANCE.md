# Transition SST direct wall export

`run145_transition_sst_fine_wall_direct_fluent_iter556.csv` was exported from
Fluent 26.1 at iteration 556 on the hot-gas-side coupled wall
`wall_vane-shadow`. It contains one row for each of the 819 wall faces:

```text
cellnumber, x-coordinate, y-coordinate, pressure, temperature,
intermittency, momentum-thickness-re, y-plus, heat-flux,
face-area-magnitude
```

Three independent report comparisons check the export:

- `sum(heat-flux * face-area) = -28548.268708 W/m`, compared with
  `-28548.269 W/m` from the wall heat-rate report;
- area-weighted wall temperature `608.878993 K`, compared with
  `608.878997 K` from the report definition;
- wall `y+` min / area average / max
  `0.007890 / 0.251092 / 0.398393`, matching the Fluent surface reports.

The matching case/data pair, transcript and monitor history are in the restart
bundle and listed in `fluent/restart_manifest.csv`.

SHA-256 of the direct wall export:
`bf7f7825147db9cbf00d3d08700c169f1d91151e78010d39a0303f82cd61d4d2`
