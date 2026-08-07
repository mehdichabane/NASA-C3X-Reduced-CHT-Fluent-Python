# Fine-grid convergence and balances

A final state is retained when the settings remain unchanged for 20 iterations,
the continuity residual is below `1e-3`, each engineering-monitor relative span
is below `0.02%`, and the mass and heat balances meet the limits below.

## SST final window: iterations 217-236

The active continuity criterion was first met at iteration 216. The calculation
continued for 20 iterations with the same second-order settings.

| Check | Result | Limit |
|---|---:|---:|
| Continuity residual | `6.6568e-04` | `1e-3` |
| Outlet-Mach span | `0.004506%` | `0.02%` |
| Mean-wall-temperature span | `0.000124%` | `0.02%` |
| Heat-rate span | `0.001741%` | `0.02%` |
| Relative mass imbalance | `0.0000509%` | `0.01%` |
| Fluid-solid interface mismatch | `0.00000558%` | `0.01%` |
| Solid heat imbalance | `0.001921%` | `0.05%` |
| Maximum wall `y+` | `0.45189` | `1.0` |

The solid receives `35,819.602 W/m` through the external interface and rejects
`35,818.914 W/m` through the internal convection boundaries, leaving
`0.688 W/m`.

| Final residual window | Engineering monitors |
|---|---|
| ![SST residuals](../results/figures/convergence/run145_sst_residuals_final_window.svg) | ![SST monitors](../results/figures/convergence/run145_sst_monitors.svg) |

## Transition SST final window: iterations 537-556

The case starts from the fine SST field. The transition equations changed to
bounded second order at iteration 386.

| Check | Result | Limit |
|---|---:|---:|
| Continuity residual | `5.4279e-05` | `1e-3` |
| Outlet-Mach span | `0.000539%` | `0.02%` |
| Mean-wall-temperature span | `0.000065%` | `0.02%` |
| Heat-rate span | `0.000354%` | `0.02%` |
| Relative mass imbalance | `0.0001503%` | `0.01%` |
| Fluid-solid interface mismatch | `0.0000191%` | `0.01%` |
| Solid heat imbalance | `0.0001889%` | `0.05%` |
| Maximum wall `y+` | `0.398393` | `1.0` |

| Engineering monitors | Final second-order residuals |
|---|---|
| ![Transition SST monitors](../results/figures/convergence/run145_transition_sst_monitors.svg) | ![Transition SST residuals](../results/figures/convergence/run145_transition_sst_residuals_second_order_window.svg) |

The source monitor, residual and balance exports are under
`data/fluent_exports/` and `data/fluent_exports/transition_sst/`.
