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

## Pilot run

Run `h_m10` first from the converged fine-grid SST state. Change only the ten internal heat-transfer coefficients, keep their free-stream temperatures unchanged, continue the existing solution until the same convergence and balance criteria are satisfied, and save a new case/data pair plus the standard wall and report exports.
