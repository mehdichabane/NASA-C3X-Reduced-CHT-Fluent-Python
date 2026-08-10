# Staged Transition SST inlet-turbulence sensitivity plan

## Objective

Separate the effect of the prescribed inlet turbulence intensity from the effect of the inlet turbulent viscosity ratio on:

- freestream turbulence decay between the computational inlet and the vane;
- the saved Transition SST transition-response fields;
- the wall thermal response;
- the NASA Run 145 comparison.

The study is diagnostic and sensitivity-oriented. Case levels are not selected to minimize NASA error, and the resulting spread is not interpreted as an uncertainty interval.

## Stage B1 — turbulent-viscosity-ratio pilots

B1 keeps `Tu_in = 6.5%` fixed and varies only the inlet turbulent viscosity ratio. All runs start independently from the accepted Transition SST solution at iteration 556.

| Case | `Tu_in` | `mu_t/mu_in` | Status |
|---|---:|---:|---|
| `tu065_vr01` | 6.5% | 1 | complete |
| `tu065_vr05` | 6.5% | 5 | complete |
| `baseline_tu065_vr10` | 6.5% | 10 | complete |

The three-point result is summarized in `b1_three_point_summary.csv`.

B1 shows that reducing `mu_t/mu_in` causes substantially stronger freestream turbulence decay before the vane. In the `2-5 mm` pre-leading-edge bin, median `Tu` changes from about `1.247%` at ratio 10 to `0.870%` at ratio 5 and `0.364%` at ratio 1. The suction-side transition-like response moves progressively downstream, with the ratio-1 case reaching the trailing-edge region. The thermal response is large while outlet Mach remains comparatively insensitive.

This is a sensitivity result, not a ranking of viscosity ratios and not a calibration to NASA wall-temperature or HTC data.

## Experimental inlet-turbulence reference

NASA-CR-168015 describes `Tu` in the C3X test-condition table as the average inlet turbulence intensity. The combustor-induced cascade inlet level was measured with LDA as `6.5%`; upstream circular rods raised it to `8.3%`. The facility description locates the LDA optical access at the cascade inlet plane.

The experimental values are therefore treated as inlet-level conditions. They are not assumed to be leading-edge turbulence targets, and the exact axial correspondence between the experimental inlet plane and the reduced computational inlet is not inferred.

## Stage B2 — inlet-turbulence-intensity sensitivity

B2 now uses the experimental inlet-level clarification rather than inventing two arbitrary turbulence-intensity levels.

Keep the accepted baseline viscosity ratio fixed at `mu_t/mu_in = 10` and vary only `Tu_in`:

| Case | `Tu_in` | `mu_t/mu_in` | Status |
|---|---:|---:|---|
| `baseline_tu065_vr10` | 6.5% | 10 | complete |
| `tu083_vr10` | 8.3% | 10 | planned |

The `8.3%` level is the second inlet turbulence condition documented for the C3X cascade. Using ratio 10 keeps a direct connection to the accepted baseline and makes the new run a clean one-factor perturbation. It is not chosen because it improves or worsens the NASA comparison.

After `tu083_vr10`, compare the same near-vane turbulence, wall-response and integral quantities as in B1. A lower-intensity pilot or an interaction case should only be added if this result creates a specific scientific question that the existing cases cannot answer.

## Campaign size

The minimum campaign is now:

- existing accepted baseline: 1 case;
- B1: 2 new runs, complete;
- B2: 1 new run, planned.

This gives **three new CFD runs total** before any optional follow-up. The reduction from the original four-run plan follows the primary-source clarification that `6.5%` and `8.3%` are the documented C3X inlet turbulence levels.

## Common restart and numerics

Each sensitivity run starts independently from the same accepted Transition SST final solution at iteration 556. Do not chain one sensitivity case into the next and do not initialize the solution.

Except for the named inlet turbulence parameter, retain the accepted Transition SST setup unchanged:

- total pressure and total temperature;
- flow direction;
- inlet intermittency `1.0`;
- internal cooling boundary conditions;
- mesh and materials;
- Transition SST model options and built-in correlations;
- bounded second-order discretization;
- report definitions and balance criteria.

## Diagnostics

For each case, extract the same quantities:

- median and 10th/90th-percentile `Tu` in all upstream bins;
- `mu_t/mu`, `Re_theta_t`, velocity and `k` in the same bins;
- suction-side intermittency thresholds and transition-like response metrics;
- pressure-side intermittency range;
- `Tw_mean`, external heat-transfer rate and outlet Mach;
- mass balance, coupled-interface heat mismatch and wall `y+`;
- solid temperature extrema/mean;
- NASA pressure, wall-temperature and HTC metrics when the comparison step is performed.

For a response that approaches the trailing edge, do not use the unrestricted global maximum of a wall gradient. Retain threshold locations and restrict the interior gradient search to `x/Cx < 0.98` so that the geometric trailing edge does not replace the transition-like model-response indicator.

## Convergence and closure protocol

Use the existing engineering monitor criterion on a common final 20-iteration window:

- external heat-transfer-rate maximum relative change `< 0.02%`;
- mean wall-temperature maximum relative change `< 0.02%`;
- outlet-Mach maximum relative change `< 0.02%`;
- continuity `< 1e-3`;
- no adverse trend in the Transition SST residuals.

Then require:

- relative mass imbalance `< 0.01%`;
- fluid-solid interface mismatch `< 0.01%`;
- solid heat imbalance `< 0.05%`;
- maximum wall `y+ < 1`.

At final closure, explicitly compute and save the Fluent Flux Reports for inlet/outlet mass flow, `wall_vane`/`wall_vane-shadow` heat transfer and the ten cooling-hole heat rates. Do not rely on those values being recoverable from a later CFF file if they were not saved as report definitions.

For Fluent report-definition convergence conditions, `Ignore Iterations Before` is a count of new iterations to ignore, not an absolute global iteration number.

## Interpretation rules

1. Report the actual near-vane `Tu`; do not label a case only by its inlet value.
2. Do not choose or discard cases because they improve or worsen NASA MAPE.
3. Treat the suction-side response-front metric as a CFD model-response indicator, not an experimentally measured transition onset.
4. Keep pressure, wall temperature and HTC conclusions separate.
5. Do not infer statistical confidence intervals or parameter probabilities from this deterministic screening.
6. Do not modify Transition SST empirical correlations during B1/B2.

## Optional follow-up

Only after B2 should an interaction or lower-intensity case be considered. Add one only if the completed one-factor results identify a concrete unresolved mechanism; otherwise stop the campaign.
