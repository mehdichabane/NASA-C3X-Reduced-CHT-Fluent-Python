# Run 145 outlet-pressure selection

## Operating-point target

NASA-CR-168015 reports Run 145 (code 4512) with an exit Mach number of
`M2 = 0.90`. NASA defines this exit Mach from measured inlet total pressure and
average measured exit-plane static pressure, and the facility used back-pressure
control to set the exit-Mach condition. Table IX does not tabulate the
corresponding Run 145 exit static pressure.

Primary source: [Hylton et al., NASA-CR-168015 (1983)](https://ntrs.nasa.gov/citations/19830020105),
Test Conditions section and Table IX, report pp. 28–30.

The Fluent quantity used for the operating-point adjustment is different: the
saved `fine_mach_outlet` report is a surface mass-weighted average of the local
outlet Mach field. I therefore use the two values only to match the nominal
operating point; outlet Mach is not treated as an independent validation metric.

## Pressure adjustment

The first second-order calculation used a provisional outlet static pressure of
`241200 Pa` and gave a Fluent mass-weighted outlet Mach of `0.88064076`.

I used a local isentropic pressure-ratio correction to estimate the pressure
needed for a nominal target Mach of `0.90`:

```text
p_new = p_old * [
    (1 + (gamma - 1)/2 * M_target^2)
    / (1 + (gamma - 1)/2 * M_old^2)
]^(-gamma/(gamma - 1))
```

with

```text
p_old    = 241200 Pa
M_old    = 0.88064076
M_target = 0.90000000
gamma    = 1.4
```

which gives

```text
p_new = 236228.236 Pa
```

I rounded that estimate to `236200 Pa` for the next Fluent continuation. The
subsequent run gave a mass-weighted outlet Mach of `0.89951531`. The released
fine-grid SST baseline keeps the same `236200 Pa` boundary condition and gives
`Mout = 0.90129444`.

| Stage | Outlet static pressure | Fluent mass-weighted outlet Mach |
|---|---:|---:|
| Provisional second-order point | `241200 Pa` | `0.88064076` |
| Isentropic estimate | `236228.236 Pa` | `n/a (estimate only)` |
| Applied rounded setting | `236200 Pa` | `0.89951531` |
| Released fine SST baseline | `236200 Pa` | `0.90129444` |

`236200 Pa` was therefore retained as the pressure-outlet boundary condition for
the Run 145 operating point. Wall-temperature and HTC measurements were not used
to choose it.

The machine-readable history is in
[`../references/model_inputs/run145_outlet_pressure_selection.csv`](../references/model_inputs/run145_outlet_pressure_selection.csv).
