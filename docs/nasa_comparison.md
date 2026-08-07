# Comparison with NASA Run 145 measurements

Pressure, wall-temperature and HTC stations come from Appendix A, page 180 of
Hylton et al., NASA-CR-168015. HTC uncertainty intervals come from Table VI,
report page 27. The transcribed source rows retain those page references in
`references/experimental_data/`.

This is a benchmark comparison. A complete [ASME V&V 20](https://www.asme.org/codes-standards/find-codes-standards/standard-for-verification-and-validation-in-computational-fluid-dynamics-and-heat-transfer/2009)
validation is not claimed because the experiment and all model inputs do not
have a combined uncertainty budget.

## Coordinate matching and metrics

Experimental stations are matched to the CFD wall profiles by axial coordinate
`x/Cx`, separately on the pressure and suction sides. Linear interpolation is
used. Bias is defined as CFD minus NASA.

The SST profile comes from the final fine-grid wall export. Transition SST uses
the direct 819-face Fluent wall export at iteration 556. HTC uncertainty bands
are assigned by experimental surface position `s/L`. The reported interval fraction
uses experimental HTC uncertainty only; it is not a combined validation
uncertainty.

`scripts/comparison/compare_run145.py` writes the pointwise tables and summary to
`results/processed/nasa_comparison/` and generates the three figures below.

## Pressure ratio

| Model | Surface | Points | Bias | MAE | RMSE | MAPE |
|---|---|---:|---:|---:|---:|---:|
| SST | Pressure | `14` | `-0.003532` | `0.007100` | `0.011515` | `0.926%` |
| SST | Suction | `14` | `-0.014069` | `0.023328` | `0.028166` | `3.980%` |
| Transition SST | Pressure | `14` | `-0.002105` | `0.006201` | `0.008862` | `0.793%` |
| Transition SST | Suction | `14` | `-0.013399` | `0.023569` | `0.029576` | `4.029%` |

![Pressure-ratio comparison](../results/figures/nasa_comparison/pressure_ratio.svg)

## Wall temperature

| Model | Surface | Points | Bias | MAE | RMSE | MAPE |
|---|---|---:|---:|---:|---:|---:|
| SST | Pressure | `31` | `+8.887 K` | `8.887 K` | `9.749 K` | `1.448%` |
| SST | Suction | `44` | `+12.999 K` | `12.999 K` | `15.022 K` | `2.005%` |
| Transition SST | Pressure | `31` | `-39.366 K` | `39.366 K` | `40.593 K` | `6.348%` |
| Transition SST | Suction | `44` | `-41.723 K` | `41.723 K` | `52.352 K` | `6.408%` |

![Wall-temperature comparison](../results/figures/nasa_comparison/wall_temperature.svg)

## Heat-transfer coefficient

| Model | Surface | Points | MAE | RMSE | MAPE | Inside experimental HTC interval |
|---|---|---:|---:|---:|---:|---:|
| SST | Pressure | `31` | `46.954 W/(m2 K)` | `62.406 W/(m2 K)` | `7.795%` | `58.06%` |
| SST | Suction | `44` | `84.320 W/(m2 K)` | `118.616 W/(m2 K)` | `11.535%` | `63.64%` |
| Transition SST | Pressure | `31` | `294.658 W/(m2 K)` | `350.778 W/(m2 K)` | `47.443%` | `9.68%` |
| Transition SST | Suction | `44` | `281.010 W/(m2 K)` | `389.862 W/(m2 K)` | `32.232%` | `31.82%` |

![Heat-transfer-coefficient comparison](../results/figures/nasa_comparison/heat_transfer_coefficient.svg)

## Why SST remains the primary case

Transition SST gives similar pressure errors but much larger thermal errors for
this mesh and operating point. The sharp rear suction-side increase is a model
response; Run 145 does not provide a measured transition location that would
confirm it.

The lower SST errors do not show that SST is generally superior to transition
models. Wall temperature also combines external convection, solid conduction
and the prescribed internal convection boundaries.
