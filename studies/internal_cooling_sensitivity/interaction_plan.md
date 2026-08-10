# h-Tbulk interaction screening

The completed one-factor screening is extended with a local two-factor, two-level full factorial check around the accepted baseline. This remains a deterministic sensitivity study, not an uncertainty quantification.

## Factors and levels

Two coded factors are used:

- `x_h = -1`: all ten internal heat-transfer coefficients at `0.95 h0`;
- `x_h = +1`: all ten internal heat-transfer coefficients at `1.05 h0`;
- `x_T = -1`: all ten coolant bulk temperatures at `Tbulk,0 - 5 K`;
- `x_T = +1`: all ten coolant bulk temperatures at `Tbulk,0 + 5 K`.

The four corner cases are:

| Case | `x_h` | `x_T` | `x_h*x_T` | Physical setting |
|---|---:|---:|---:|---|
| `h_m05_t_m05` | -1 | -1 | +1 | `0.95 h0`, `Tbulk,0 - 5 K` |
| `h_m05_t_p05` | -1 | +1 | -1 | `0.95 h0`, `Tbulk,0 + 5 K` |
| `h_p05_t_m05` | +1 | -1 | -1 | `1.05 h0`, `Tbulk,0 - 5 K` |
| `h_p05_t_p05` | +1 | +1 | +1 | `1.05 h0`, `Tbulk,0 + 5 K` |

Exact values for every cooling boundary are in `interaction_case_matrix.csv`.

## Restart and acceptance protocol

Every corner case is restarted independently from the same accepted fine-grid SST baseline state at iteration 236. No case is restarted from another interaction corner. Geometry, mesh, external boundary conditions, material properties, turbulence model, discretization, monitors and convergence checks remain unchanged.

The existing acceptance criteria are retained:

- engineering-monitor relative span below `0.02%` over the accepted post-transient window;
- final continuity residual below `1e-3`;
- relative mass imbalance below `0.01%`;
- fluid-solid interface heat-rate mismatch below `0.01%`;
- solid heat imbalance below `0.05%`;
- maximum wall `y+` below `1`.

Each accepted corner retains the same integral quantities and NASA comparison metrics as the one-factor families.

## Interaction estimate

For any response `Y`, fit the coded bilinear model

`Y = beta0 + beta_h*x_h + beta_T*x_T + beta_hT*x_h*x_T`.

With the four corner responses, the interaction coefficient is

`beta_hT = (Y_pp - Y_pm - Y_mp + Y_mm) / 4`,

where the first sign refers to `h` and the second to `Tbulk`.

The conventional two-level factorial interaction effect is `2*beta_hT`.

A mixed finite-difference derivative in physical units can also be reported as

`d2Y/(d h_scale d Tbulk) ~= (Y_pp - Y_pm - Y_mp + Y_mm) / (4 * 0.05 * 5 K)`.

Because there is one deterministic CFD result at each of four corners and the four-parameter bilinear model is saturated, this screening does not attach ANOVA p-values or experimental-error confidence intervals to the interaction. Interpretation is based on interaction magnitude relative to the main responses and on physical consistency.
