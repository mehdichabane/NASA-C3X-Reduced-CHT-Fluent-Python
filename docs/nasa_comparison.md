# Comparison with NASA Run 145 measurements

Pressure, wall-temperature and HTC stations come from Appendix A, page 180 of
Hylton et al., NASA-CR-168015. HTC uncertainty intervals come from Table VI,
report page 27. The transcribed source rows retain those page references in
`references/experimental_data/`.

This is a benchmark comparison. Conformance to a complete
[ASME V&V 20](https://www.asme.org/codes-standards/find-codes-standards/standard-for-verification-and-validation-in-computational-fluid-dynamics-and-heat-transfer/2009)
validation assessment is not claimed. The retained mesh record does not support
an accepted formal discretization-uncertainty estimate, model-input uncertainty
is not propagated, and the available experimental uncertainty is insufficient
for a combined validation-uncertainty budget.

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

For wall temperature, MAE and RMSE in kelvin are the most directly interpretable
dimensional error measures and are therefore reported alongside MAPE. MAPE is
retained as a compact relative summary using absolute temperature in kelvin,
but it should not be interpreted alone: percentage errors can look small when
the compared temperatures have a large absolute baseline, and the value is not
invariant to an affine change of temperature scale.

Summary bias, MAE, RMSE and MAPE give equal weight to each experimental station.
They are station-wise statistics, not arc-length-weighted surface integrals;
regions with denser experimental station placement therefore contribute more
entries to the summary metrics.

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

At the reported precision, the magnitude of the wall-temperature bias equals
the MAE for all four rows. The stationwise temperature errors are therefore
one-signed over the sampled stations: the SST baseline is systematically hotter
than the NASA values, while the accepted Transition SST baseline is
systematically colder. This is a descriptive bias of the archived model states,
not a calibration target and not a decomposition of its physical cause.

![Wall-temperature comparison](../results/figures/nasa_comparison/wall_temperature.svg)

## Heat-transfer coefficient

| Model | Surface | Points | MAE | RMSE | MAPE | Inside experimental HTC interval |
|---|---|---:|---:|---:|---:|---:|
| SST | Pressure | `31` | `46.954 W/(m2 K)` | `62.406 W/(m2 K)` | `7.795%` | `58.06%` |
| SST | Suction | `44` | `84.320 W/(m2 K)` | `118.616 W/(m2 K)` | `11.535%` | `63.64%` |
| Transition SST | Pressure | `31` | `294.658 W/(m2 K)` | `350.778 W/(m2 K)` | `47.443%` | `9.68%` |
| Transition SST | Suction | `44` | `281.010 W/(m2 K)` | `389.862 W/(m2 K)` | `32.232%` | `31.82%` |

![Heat-transfer-coefficient comparison](../results/figures/nasa_comparison/heat_transfer_coefficient.svg)

*The HTC error bars show the reported experimental HTC uncertainty only. They
are not a combined CFD/experimental validation-uncertainty interval.*

## Why SST remains the primary case

Transition SST gives similar pressure errors but much larger thermal errors for
the accepted fine-grid baseline. The sharp rear suction-side increase is a model
response; Run 145 does not provide a measured transition location that would
confirm it.

The separate
[`Transition SST inlet-turbulence sensitivity study`](../studies/transition_sst_sensitivity/README.md)
shows that the imposed inlet turbulence state does not remain unchanged between
the computational inlet and the vane. At fixed `Tu_in = 6.5%`, changes in inlet
turbulent-viscosity ratio produce large changes in near-vane turbulence decay,
the suction-side transition-like response and the thermal field, while the
outlet Mach number changes much less. At viscosity ratio `10`, changing the
documented inlet turbulence level from `6.5%` to `8.3%` produces only a small
near-vane and thermal response because the inlet difference is strongly
attenuated before the leading edge.

All transition-response-front locations cited by that study are extracted from
the fine mesh only. No coarse/medium Transition SST mesh-sensitivity assessment
was performed for those coordinates, so they are fine-grid model-response
diagnostics rather than grid-converged transition locations.

These results explain a strong model sensitivity; they do not identify an
experimentally verified transition onset, calibrate the calculation, or show
that SST is generally superior to transition models. Wall temperature also
combines external convection, solid conduction and the prescribed internal
convection boundaries.
