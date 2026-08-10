# Internal cooling boundary-condition sensitivity

This study tests how the fine-grid SST thermal comparison changes when the prescribed internal cooling conditions are perturbed. It is a sensitivity study, not an uncertainty quantification: the perturbation ranges below are screening values and are not presented as measured confidence intervals.

## Baseline

The starting point is the accepted fine-grid SST Run 145 solution. Geometry, mesh, external boundary conditions, material properties, turbulence model, discretization and convergence checks remain unchanged.

Only the ten internal convection boundaries are varied. Their baseline values are taken from `references/model_inputs/run145_4512_internal_convection.csv`.

## Screening matrix

Two one-factor families are used:

- internal heat-transfer coefficient: `h/h0 = 0.90, 0.95, 1.00, 1.05, 1.10`;
- coolant bulk temperature: `Tbulk - Tbulk,0 = -10, -5, 0, +5, +10 K`.

All ten passages are perturbed together in the first screening. Combined `h` and `Tbulk` perturbations are not included at this stage.

The exact boundary values are listed in `case_matrix.csv`.

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

## Quantities to compare

Each converged case should retain the same outputs used by the baseline workflow, including:

- wall-temperature bias, MAE, RMSE and MAPE on pressure and suction sides;
- HTC comparison metrics on both sides;
- mean external wall temperature and external heat-transfer rate;
- outlet Mach number;
- mass, fluid-solid interface and solid-energy balance checks;
- wall profiles required to compute `delta Tw = Tw(case) - Tw(baseline)`.

The main sensitivity coefficients will be evaluated around the baseline from the symmetric +/-5% and +/-5 K cases. The +/-10% and +/-10 K cases provide a wider screening check for nonlinearity.

## h_m10 pilot

The corrected `h_m10` case was restarted from the accepted fine-grid SST state at iteration 236. All ten internal heat-transfer coefficients were set to exactly `0.9 h0`; the ten coolant bulk temperatures were unchanged. The final state is iteration 271.

The final case/data files were checked directly: all ten convection boundaries contain the intended coefficient scale and baseline free-stream temperatures.

| Quantity | Baseline | `h_m10` | Change |
|---|---:|---:|---:|
| Mean external wall temperature | `655.619 K` | `661.724 K` | `+6.104 K` |
| External heat-transfer rate | `35.820 kW/m` | `33.888 kW/m` | `-5.393%` |
| Outlet Mach number | `0.901294` | `0.901302` | `+0.000804%` |
| Solid minimum temperature | `552.824 K` | `563.826 K` | `+11.002 K` |
| Solid maximum temperature | `716.831 K` | `720.356 K` | `+3.525 K` |

The final continuity residual is `3.5728e-4`. Over iterations 252-271, the three printed engineering monitors remain within the existing `0.02%` span criterion.

The final balance checks are:

| Check | `h_m10` | Limit |
|---|---:|---:|
| Relative mass imbalance | `0.000294%` | `0.01%` |
| Fluid-solid interface mismatch | `8.06e-7%` | `0.01%` |
| Solid heat imbalance | `0.00365%` | `0.05%` |
| Maximum wall `y+` | `0.4500` | `1.0` |

`h_m10` is therefore retained for the sensitivity study.

The NASA comparison was rebuilt from the saved CFF case/data fields with the same coordinate mapping and metric definitions as the baseline. Reapplying that extraction to the baseline reproduces the committed baseline metrics to numerical precision.

| Quantity | Surface | Baseline MAPE | `h_m10` MAPE |
|---|---|---:|---:|
| Pressure ratio | pressure | `0.926%` | `0.926%` |
| Pressure ratio | suction | `3.980%` | `3.987%` |
| Wall temperature | pressure | `1.448%` | `2.618%` |
| Wall temperature | suction | `2.005%` | `2.865%` |
| HTC | pressure | `7.795%` | `7.691%` |
| HTC | suction | `11.535%` | `10.752%` |

The 10% reduction in prescribed internal HTC therefore changes the thermal solution strongly enough to worsen the wall-temperature comparison while leaving the pressure comparison essentially unchanged. The HTC error does not move in the same direction as the wall-temperature error, so the two thermal quantities should be treated separately in the remaining screening cases.

Detailed values are in `h_m10_integral_summary.csv`, `h_m10_nasa_metrics.csv` and `run145_sst_fine_h_m10_global_checks.csv`.

## Completed one-factor screening

Both five-point families are now complete. The symmetric local derivatives and the wider five-point derivatives agree closely for the main thermal quantities.

| Quantity | HTC family | `Tbulk` family | HTC linear `R2` | `Tbulk` linear `R2` |
|---|---:|---:|---:|---:|
| Mean wall temperature | `-0.5783 K` per `+1% h` | `+0.30489 K/K` | `0.999012` | `0.999998` |
| External heat-transfer rate | `+184.15 W/m` per `+1% h` | `-95.601 W/(m K)` | `0.999229` | `0.9999999` |
| Mean solid temperature | `-0.6678 K` per `+1% h` | `+0.35479 K/K` | `0.999017` | `0.999999` |

For the `Tbulk` family, the central and five-point derivatives differ by only `0.0011%` for mean wall temperature and `0.0043%` for external heat-transfer rate. The maximum linear-fit residual is `0.072%` of the five-point response span for mean wall temperature and `0.025%` for heat-transfer rate. The HTC family is also close to linear, but its corresponding residuals are about `1.35%` and `1.19%` of the response span.

Using the mean baseline coolant bulk temperature (`410.022 K`) only as the reference scale for nondimensionalization, the local normalized sensitivities are `-0.0882` to `h` and `+0.1907` to a uniform `Tbulk` shift for mean wall temperature, and `+0.5141` to `h` and `-1.0943` to `Tbulk` for external heat-transfer rate. These normalized values compare local relative response strength; they do not make the two screening ranges equivalent physical uncertainties.

The two families give a consistent physical picture. Stronger prescribed internal cooling, obtained either by increasing `h` or decreasing `Tbulk`, lowers the wall and solid temperatures and increases the external heat-transfer rate. It also improves the NASA wall-temperature comparison while slightly worsening the NASA HTC comparison. Pressure ratio and outlet Mach remain effectively insensitive at the scale of these perturbations.

The completed OFAT screening does not identify `h`-`Tbulk` interaction effects. A combined-factor check is therefore a separate question; the natural next step, if interaction screening is required, is the four `(+/-5% h, +/-5 K)` corner cases around the baseline.

The consolidated results are in `h_family_summary.csv`, `h_family_local_sensitivity.csv`, `t_family_summary.csv`, `t_family_local_sensitivity.csv`, `t_family_linearity.csv` and `h_vs_t_family_comparison.csv`.
