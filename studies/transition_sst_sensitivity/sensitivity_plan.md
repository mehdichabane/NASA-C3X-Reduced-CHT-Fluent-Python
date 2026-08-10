# Staged Transition SST inlet-turbulence sensitivity plan

## Objective

Separate the effect of the prescribed inlet turbulence intensity from the effect of the inlet turbulent viscosity ratio on:

- freestream turbulence decay between the computational inlet and the vane;
- the saved Transition SST transition-response fields;
- the wall thermal response;
- the NASA Run 145 comparison.

The study is diagnostic and sensitivity-oriented. Case levels are not selected to minimize NASA error, and the resulting spread is not interpreted as an uncertainty interval.

## Why a staged plan

The accepted baseline prescribes `Tu_in = 6.5%` and `mu_t/mu_in = 10`, but the final saved solution contains only about `1.25%` median freestream turbulence intensity in the `2-5 mm` bin immediately upstream of the leading edge. Because Fluent documents that the inlet turbulent viscosity ratio controls freestream turbulence decay, a direct two-factor grid chosen only from inlet values could waste runs on cases that reach nearly the same state at the vane.

The plan therefore uses the minimum useful one-factor pilots first, then chooses the turbulence-intensity levels from the observed inlet-to-vane mapping.

## Stage B1 — turbulent-viscosity-ratio pilots

Keep the nominal experimental/mainstream input value used by the baseline, `Tu_in = 6.5%`, and vary only the turbulent viscosity ratio within the low range recommended for Transition SST inlet specification.

| Case | `Tu_in` | `mu_t/mu_in` | Status |
|---|---:|---:|---|
| `tu065_vr01` | 6.5% | 1 | planned |
| `tu065_vr05` | 6.5% | 5 | planned |
| `baseline_tu065_vr10` | 6.5% | 10 | complete |

Only two new CFD runs are required in B1 because the ratio-10 endpoint already exists.

### B1 decision quantities

For each case, extract exactly the same diagnostics as for the baseline:

- median and 10th/90th-percentile `Tu` in all upstream bins;
- `mu_t/mu` and `Re_theta_t` in the same bins;
- `Tu` in the `10-5 mm` and `5-2 mm` / `2-5 mm` near-leading-edge bins;
- suction-side transition-like response-front location from the same gradient/threshold definitions;
- pressure-side intermittency range;
- `Tw_mean`, external heat-transfer rate and outlet Mach;
- mass/interface/solid-energy balances and wall `y+`;
- NASA pressure, wall-temperature and HTC metrics.

The B1 result answers one clean question: at fixed inlet turbulence intensity, how strongly does the viscosity-ratio specification change the turbulence state that actually reaches the vane and the resulting thermal/transition response?

## Stage B2 — turbulence-intensity pilots

Do not fix the two new `Tu_in` values before B1 is analyzed.

After B1, select one viscosity-ratio level and choose two new inlet turbulence intensities **a priori from the measured inlet-to-vane mapping**, not from NASA fit quality. The selected values should produce clearly separated near-leading-edge turbulence states while remaining numerically and physically sensible for the Transition SST model.

The preferred ratio for B2 will be the lowest B1 ratio that still gives a well-resolved, physically useful near-vane freestream state; if all three are suitable, retain `mu_t/mu_in = 10` for continuity with the accepted baseline.

| Case | `Tu_in` | `mu_t/mu_in` | Status |
|---|---:|---:|---|
| `tu_low_vrXX` | TBD after B1 | selected after B1 | gated |
| `baseline_tu065_vr10` or corresponding B1 anchor | 6.5% | selected anchor | complete/planned |
| `tu_high_vrXX` | TBD after B1 | selected after B1 | gated |

B2 therefore requires two additional CFD runs unless the B1 result shows that a different design is necessary.

## Minimum campaign size

The intended minimum campaign is:

- existing accepted baseline: 1 case;
- B1: 2 new runs;
- B2: 2 new runs;

for **four new CFD runs total** before any optional interaction/robustness case.

This is deliberately smaller than a blind `3 x 3` matrix. It yields two three-point one-factor families sharing an accepted anchor and separates inlet-intensity sensitivity from viscosity-ratio sensitivity without assuming that inlet values map linearly to the vane.

## Common restart and numerics

Each sensitivity run should start independently from the same accepted Transition SST final solution at iteration 556. Do not chain one sensitivity case into the next and do not initialize the solution.

Except for the named inlet turbulence parameter, retain the accepted Transition SST setup unchanged:

- total pressure and total temperature;
- flow direction;
- inlet intermittency `1.0`;
- internal cooling boundary conditions;
- mesh and materials;
- Transition SST model options and built-in correlations;
- bounded second-order discretization;
- report definitions and balance criteria.

Using the common Transition SST state avoids repeatedly re-creating the two additional transition fields from the SST-only solution. A later independent-restart spot check can be added only if the sensitivity responses suggest path dependence.

## Convergence protocol

Run in blocks. After the first 20 iterations, continue in 15-iteration blocks until a common final 20-iteration window satisfies the existing engineering monitor criterion:

- external heat-transfer-rate relative span `< 0.02%`;
- mean wall-temperature relative span `< 0.02%`;
- outlet-Mach relative span `< 0.02%`;
- continuity `< 1e-3`;
- no adverse trend in the Transition SST residuals.

Then require the existing global checks:

- relative mass imbalance `< 0.01%`;
- fluid-solid interface mismatch `< 0.01%`;
- solid heat imbalance `< 0.05%`;
- maximum wall `y+ < 1`.

No fixed iteration count is assumed in advance.

## Interpretation rules

1. Report the actual near-vane `Tu`; do not label a case only by its inlet value.
2. Do not choose or discard cases because they improve or worsen NASA MAPE.
3. Treat the suction-side response-front metric as a CFD model-response indicator, not an experimentally measured transition onset.
4. Keep pressure, wall temperature and HTC conclusions separate.
5. Do not infer statistical confidence intervals or parameter probabilities from this deterministic screening.
6. Do not modify Transition SST empirical correlations during B1/B2.

## Optional follow-up

Only after B1 and B2 are complete should an interaction check be considered. A single cross-case may be sufficient if the one-factor responses indicate strong non-additivity; otherwise no factorial expansion is necessary.