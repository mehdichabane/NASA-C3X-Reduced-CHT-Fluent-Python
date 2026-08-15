# Internal cooling boundary-condition sensitivity

This study tests how the fine-grid SST thermal comparison changes when the
prescribed internal cooling conditions are perturbed. The cases are deterministic
screening runs; the ranges below are not measured confidence intervals.

## Baseline

The starting point is the accepted fine-grid SST Run 145 solution. Geometry, mesh, external boundary conditions, material properties, turbulence model, discretization and convergence checks remain unchanged.

Only the ten internal convection boundaries are varied. Their baseline values are taken from `references/model_inputs/run145_4512_internal_convection.csv`.

## Screening matrix

Two completed one-factor families are used:

- internal heat-transfer coefficient: `h/h0 = 0.90, 0.95, 1.00, 1.05, 1.10`;
- coolant bulk temperature: `Tbulk - Tbulk,0 = -10, -5, 0, +5, +10 K`.

All ten passages are perturbed together. The local interaction check uses the four `(±5% h, ±5 K)` corners around the same baseline; exact values are listed in `interaction_case_matrix.csv`.

Because all ten passages are perturbed coherently, this screening probes
common-mode scaling and offset directions. Passage-to-passage uncertainty and
errors specific to individual passage correction factors `C_r` are outside this
matrix.

The one-factor boundary values are listed in `case_matrix.csv`.

## Case IDs

| Case | Change from baseline |
|---|---|
| `baseline` | none |
| `h_m10` | all internal `h` values multiplied by 0.90 |
| `h_m05` | all internal `h` values multiplied by 0.95 |
| `h_p05` | all internal `h` values multiplied by 1.05 |
| `h_p10` | all internal `h` values multiplied by 1.10 |
| `t_m10` | all internal `Tbulk` values shifted by -10 K |
| `t_m05` | all internal `Tbulk` values shifted by -5 K |
| `t_p05` | all internal `Tbulk` values shifted by +5 K |
| `t_p10` | all internal `Tbulk` values shifted by +10 K |
| `h_m05_t_m05` | `0.95 h0`, `Tbulk,0 - 5 K` |
| `h_m05_t_p05` | `0.95 h0`, `Tbulk,0 + 5 K` |
| `h_p05_t_m05` | `1.05 h0`, `Tbulk,0 - 5 K` |
| `h_p05_t_p05` | `1.05 h0`, `Tbulk,0 + 5 K` |

## Quantities compared

Each accepted case retains the same outputs used by the baseline workflow, including:

- wall-temperature bias, MAE, RMSE and MAPE on pressure and suction sides;
- HTC comparison metrics on both sides;
- mean external wall temperature and external heat-transfer rate;
- outlet Mach number;
- mass, fluid-solid interface and solid-energy balance checks;
- wall profiles required to compute `delta Tw = Tw(case) - Tw(baseline)`.

The local one-factor sensitivity coefficients use the symmetric `±5%` and `±5 K` cases. The `±10%` and `±10 K` cases provide the wider screening check for nonlinearity.

## h_m10 pilot

The first completed sensitivity case was `h_m10`, restarted from the fine SST baseline at iteration 236 with all ten internal heat-transfer coefficients set to `0.9 h0` and unchanged coolant bulk temperatures. The final state at iteration 271 passed the same monitor, conservation and wall-`y+` checks used for the baseline.

| Quantity | Baseline | `h_m10` | Change |
|---|---:|---:|---:|
| Mean external wall temperature | `655.619 K` | `661.724 K` | `+6.104 K` |
| External heat-transfer rate | `35.820 kW/m` | `33.888 kW/m` | `-5.393%` |
| Outlet Mach number | `0.901294` | `0.901302` | `+0.000804%` |

The lower internal HTC therefore moved the thermal solution in the expected direction while leaving the aerodynamic operating point essentially unchanged. It was retained and expanded into the completed five-point `h` family below. Detailed pilot checks and NASA-comparison metrics remain in `h_m10_integral_summary.csv`, `h_m10_nasa_metrics.csv` and `run145_sst_fine_h_m10_global_checks.csv`.

## Completed one-factor screening

Both five-point families are complete. The symmetric local derivatives and the wider five-point derivatives agree closely for the main thermal quantities.

| Quantity | HTC family | `Tbulk` family | HTC linear `R2` | `Tbulk` linear `R2` |
|---|---:|---:|---:|---:|
| Mean wall temperature | `-0.5783 K` per `+1% h` | `+0.30489 K/K` | `0.999012` | `0.999998` |
| External heat-transfer rate | `+184.15 W/m` per `+1% h` | `-95.601 W/(m·K)` | `0.999229` | `0.9999999` |
| Mean solid temperature | `-0.6678 K` per `+1% h` | `+0.35479 K/K` | `0.999017` | `0.999999` |

For the `Tbulk` family, the central and five-point derivatives differ by only `0.0011%` for mean wall temperature and `0.0043%` for external heat-transfer rate. The maximum linear-fit residual is `0.072%` of the five-point response span for mean wall temperature and `0.025%` for heat-transfer rate. The HTC family is also close to linear, but its corresponding residuals are about `1.35%` and `1.19%` of the response span.

Using the mean baseline coolant bulk temperature (`410.022 K`) only as the reference scale for nondimensionalisation, the local normalised sensitivities are `-0.0882` to `h` and `+0.1907` to a uniform `Tbulk` shift for mean wall temperature, and `+0.5141` to `h` and `-1.0943` to `Tbulk` for external heat-transfer rate. These normalised values compare local relative response strength; they do not make the two screening ranges equivalent physical uncertainties.

The two families give a consistent physical picture. Stronger prescribed internal cooling, obtained either by increasing `h` or decreasing `Tbulk`, lowers the wall and solid temperatures and increases the external heat-transfer rate. It also improves the NASA wall-temperature comparison while slightly worsening the NASA HTC comparison. Pressure ratio and outlet Mach remain effectively insensitive at the scale of these perturbations.

## Completed interaction screening

The four `(±5% h, ±5 K)` corners were restarted independently from the same accepted baseline at iteration 236 and evaluated with the same convergence and balance criteria. The coded bilinear model is

`Y = beta0 + beta_h*x_h + beta_T*x_T + beta_hT*x_h*x_T`.

For the principal thermal responses:

| Quantity | Main effect `h` | Main effect `Tbulk` | Interaction effect | Interaction / `h` | Interaction / `Tbulk` |
|---|---:|---:|---:|---:|---:|
| Mean wall temperature | `-5.7830 K` | `+3.0473 K` | `+0.0650 K` | `1.12%` | `2.13%` |
| External heat-transfer rate | `+1841.45 W/m` | `-955.66 W/m` | `-25.10 W/m` | `1.36%` | `2.63%` |
| Mean solid temperature | `-6.6781 K` | `+3.5459 K` | `+0.0783 K` | `1.17%` | `2.21%` |

The interaction is therefore resolved but small relative to both main effects in this local screening box. The factorial main effects also reproduce the symmetric one-factor effects closely: the relative differences are about `0.0023%` (`h`) and `0.054%` (`Tbulk`) for mean wall temperature, and `0.0014%` and `0.036%` for external heat-transfer rate.

The four-corner bilinear model is saturated, so no ANOVA p-values or experimental-error confidence intervals are inferred from these deterministic CFD runs. The result supports a predominantly additive local response, with a small bilinear correction over the tested `±5% h` and `±5 K` range.

Consolidated one-factor results are in `h_family_summary.csv`, `h_family_local_sensitivity.csv`, `t_family_summary.csv`, `t_family_local_sensitivity.csv`, `t_family_linearity.csv` and `h_vs_t_family_comparison.csv`. Interaction inputs and results are in `interaction_case_matrix.csv`, `interaction_plan.md`, `interaction_corner_summary.csv`, `interaction_factorial_coefficients.csv`, `interaction_additivity_check.csv` and `interaction_main_effect_consistency.csv`.
