# Transition SST inlet-turbulence sensitivity plan

## Objective

Separate the effect of prescribed inlet turbulence intensity from the effect of inlet turbulent-viscosity ratio on:

- freestream turbulence decay between the computational inlet and the vane;
- the Transition SST wall-response fields;
- the thermal solution;
- the NASA Run 145 comparison.

Case levels are controlled diagnostic perturbations selected independently of the NASA comparison error.

## Case matrix

All runs restart independently from the accepted Transition SST solution at iteration 556.

| Case | `Tu_in` | `mu_t/mu_in` | Status |
|---|---:|---:|---|
| `baseline_tu065_vr10` | 6.5% | 10 | complete |
| `tu065_vr05` | 6.5% | 5 | complete |
| `tu065_vr01` | 6.5% | 1 | complete |
| `tu083_vr10` | 8.3% | 10 | complete |

B1 varies viscosity ratio at fixed `Tu_in = 6.5%`. B2 varies inlet turbulence intensity at fixed `mu_t/mu_in = 10`; `8.3%` is the second inlet turbulence level documented for the C3X cascade.

## Common restart and numerics

Do not chain sensitivity cases or reinitialise the solution. Except for the named inlet turbulence parameter, retain the accepted Transition SST setup unchanged, including:

- external and internal thermal boundary conditions;
- mesh and materials;
- inlet intermittency and built-in transition correlations;
- pressure, density, momentum and energy discretisation;
- `Second Order Upwind` for `k`, `omega`, intermittency and transition momentum-thickness Reynolds number;
- report definitions and balance criteria.

## Diagnostics

For each case, extract the same quantities:

- upstream-bin median and 10th/90th-percentile `Tu`;
- `mu_t/mu`, `Re_theta_t`, velocity and `k` in the same bins;
- suction-side intermittency thresholds and transition-like response metrics;
- pressure-side intermittency range;
- mean wall temperature, external heat-transfer rate and outlet Mach;
- mass balance, coupled-interface heat mismatch and wall `y+`;
- solid temperature statistics;
- NASA pressure, wall-temperature and HTC metrics when the comparison step is performed.

If a response approaches the trailing edge, retain threshold locations and restrict the interior gradient search to `x/Cx < 0.98` so the geometric trailing edge does not replace the transition-like model-response indicator.

## Convergence and closure

Use a common final 20-iteration window with:

- external heat-transfer-rate maximum relative change `< 0.02%`;
- mean wall-temperature maximum relative change `< 0.02%`;
- outlet-Mach maximum relative change `< 0.02%`;
- continuity `< 1e-3`;
- no adverse trend in the Transition SST residuals.

Then require relative mass imbalance `< 0.01%`, fluid-solid interface mismatch `< 0.01%`, solid heat imbalance `< 0.05%` and maximum wall `y+ < 1`.

At final closure, save Fluent Flux Reports for inlet/outlet mass flow, `wall_vane`/`wall_vane-shadow` heat transfer and the ten cooling-hole heat rates. For report-definition convergence conditions, `Ignore Iterations Before` is a count of new iterations to ignore, not an absolute global iteration number.

## Interpretation

Report the actual near-vane turbulence level rather than identifying a case only by its inlet value. Treat the suction-side response front as a CFD model-response indicator, not an experimentally measured transition onset. Keep pressure, wall-temperature and HTC conclusions separate, and do not modify the Transition SST empirical correlations during the campaign.

The planned B1/B2 campaign is complete. A `Tu x mu_t/mu` interaction case is left for a future study only if a specific interaction question is posed.
