# Run 145 outlet-pressure selection record

## Experimental operating-point anchor

NASA-CR-168015 treats exit Mach number as a controlled cascade test variable.
In the Test Conditions section, Hylton et al. state that exit Mach numbers are
based on measured inlet total pressure and average measured exit-plane static
pressure. At a given Reynolds-number condition, the exit-Mach level was
established independently by adjusting the cascade exit pressure with a
controllable exhaust valve. Table IX reports Run 145 / code 4512 with
`M2 = 0.90`.

Primary source:
[Hylton et al., NASA-CR-168015 (1983)](https://ntrs.nasa.gov/citations/19830020105),
Test Conditions section and Table IX, report pp. 28-30.

Hylton's 1983 HOST conference paper independently describes the same facility
as having back-pressure regulation and exit-Mach-number control, and summarizes
the test matrix at exit Mach numbers near `0.9` and `1.05`:
[Gas side heat transfer](https://ntrs.nasa.gov/citations/19860002040).

The experiment therefore supplies an exit-Mach operating point, but the Run 145
Table IX row does not tabulate the corresponding measured exit static pressure.

## Fluent pressure-outlet selection

The retained project development record resolves how the released
`236200 Pa` setting was chosen. It was not copied from a NASA pressure table.
The pressure outlet was adjusted to reproduce the experimentally controlled
Run 145 exit-Mach operating point.

The relevant accepted history is:

| Stage | Outlet static pressure | Mass-weighted outlet Mach | Status |
|---|---:|---:|---|
| Provisional second-order point | `241200 Pa` | `0.88064076` | pre-adjustment calculation |
| Local isentropic estimate | `236228.236 Pa` | target `0.900000` | calculated update |
| Applied rounded setting | `236200 Pa` | `0.89951531` | accepted operating-point match |
| Current released fine SST baseline | `236200 Pa` | `0.90129444` | retained boundary condition |

The update from the provisional second-order point used a local isentropic
pressure-ratio correction, assuming the total-pressure level remains
approximately unchanged over the small operating-point adjustment:

```text
p_new = p_old * [
    (1 + (gamma - 1)/2 * M_target^2)
    / (1 + (gamma - 1)/2 * M_old^2)
]^(-gamma/(gamma - 1))
```

With

```text
p_old    = 241200 Pa
M_old    = 0.88064076
M_target = 0.90000000
gamma    = 1.4
```

this gives

```text
p_new = 236228.236 Pa
```

`gamma = 1.4` is recorded here because it is the value used in that historical
one-step estimate. The estimate was only a local control update used to propose
the next pressure-outlet value; it is not introduced as a separate gas-property
definition for the released Fluent baseline and it is not an uncertainty model.
The actual acceptance check was the subsequent Fluent response.

The estimate was rounded to `236200 Pa` before the next Fluent continuation.
The resulting recorded mass-weighted outlet Mach was `0.89951531`, an absolute
Mach difference of `0.00048469` from the `0.90` target (`0.0539%` relative to
the target).

The machine-readable selection history is in
[`../references/model_inputs/run145_outlet_pressure_selection.csv`](../references/model_inputs/run145_outlet_pressure_selection.csv).

## Interpretation in this repository

`236200 Pa` is therefore classified as an **operating-point boundary condition
adjusted to the NASA exit-Mach target**. It is neither a direct transcription of
a Run 145 NASA exit-pressure value nor a CFD quantity that was selected without
reference to the experiment.

Consequently, agreement between the computed outlet Mach and NASA `M2 = 0.90`
is an **operating-point consistency check**, not an independent validation
metric. The independent experimental comparisons in this repository are the
sampled surface pressure ratio, wall temperature and heat-transfer coefficient
profiles. Outlet Mach remains useful as a convergence monitor and as a global
mesh- or sensitivity-study response quantity.

The pressure adjustment used only the Run 145 aerodynamic operating-point target;
wall-temperature and HTC measurements were not used to select `236200 Pa`.
