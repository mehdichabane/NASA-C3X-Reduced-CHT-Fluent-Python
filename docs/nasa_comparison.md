# Comparison with NASA Run 145 measurements

Pressure, wall-temperature and HTC stations come from Appendix A, page 180 of
Hylton et al., NASA-CR-168015. Regional external-HTC uncertainty intervals come
from Table VI, report page 27. Additional experimental uncertainties reported
in the Data Uncertainties subsection and Table VII are transcribed in
`references/experimental_data/c3x_experimental_uncertainty_summary.csv`.

This is a benchmark comparison. Conformance to a complete
[ASME V&V 20](https://www.asme.org/codes-standards/find-codes-standards/standard-for-verification-and-validation-in-computational-fluid-dynamics-and-heat-transfer/2009)
validation assessment is not claimed. NASA supplies multiple experimental
uncertainty estimates, but the retained mesh record does not support an accepted
formal discretization-uncertainty estimate and model-input uncertainty is not
propagated. The repository therefore does not construct a combined
validation-uncertainty budget.

The NASA Run 145 exit Mach number is an operating-point anchor rather than an
independent validation observable in this model. The Fluent pressure outlet was
adjusted using the NASA `M2 = 0.90` target, so the resulting fine-grid
`Mout = 0.901294` is reported as an operating-point consistency and convergence
check. It is not included among the independent experimental comparison metrics
below. The complete pressure-selection history is in
[`outlet_pressure_selection.md`](outlet_pressure_selection.md).

## NASA experimental uncertainty record

NASA's Data Uncertainties subsection reports the component uncertainties that
feed the experimental reduction. The values transcribed here are:

| Quantity | Reported uncertainty |
|---|---:|
| External vane surface temperature | about `±1 °C` |
| Free-stream gas temperature | about `±11 °C` |
| External airfoil profile | about `±0.008 cm` |
| Cooling-hole location | about `±0.013 cm` |
| Cooling-hole diameter | `±0.005 cm` |
| Internal cooling-hole HTC calculation | estimated `±3%` |
| Vane-material thermal conductivity used in the experimental reduction | about `±3%` |
| Pressure measurement | `±0.7 kPa` |

Table VII separately reports uncertainty in test parameters:

| Test parameter | Reported uncertainty |
|---|---:|
| Reynolds number, `Re` | `±3.1%` |
| Mach number, `MN` | `±0.9%` |
| Wall-to-gas temperature ratio, `Tw/Tg` | `±2.0%` |
| Inlet turbulence intensity, `Tu` | `±10.0%` |

NASA states that the key uncertainty analysis uses the Kline and McClintock
method (Ref. 23); the `Tu` value is reported as being based on prior experience
with the LDA system. These values are source metadata in the present repository,
not stochastic inputs propagated through Fluent.

Table VI is already the resulting *regional external-HTC uncertainty* for the
C3X experimental reduction. The component uncertainties above are therefore not
added again to the Table VI HTC intervals. Doing so would double-count sources
already represented in NASA's external-HTC uncertainty analysis.

NASA also cautions that these values describe uncertainty in the absolute level
when the data are used for verification. Some systematic contributions affect
multiple runs similarly, so uncertainty in run-to-run trends can be smaller than
the absolute-level uncertainty.

## Coordinate matching and metrics

Experimental stations are matched to the CFD wall profiles by axial coordinate
`x/Cx`, separately on the pressure and suction sides. Linear interpolation is
used. Bias is defined as CFD minus NASA.

The SST profile comes from the final fine-grid wall export. Transition SST uses
the direct 819-face Fluent wall export at iteration 556. HTC uncertainty bands
are assigned by experimental surface position `s/L`. The reported interval
fraction uses Table VI experimental HTC uncertainty only; it is not a combined
validation uncertainty.

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

*The HTC error bars show the reported Table VI experimental HTC uncertainty
only. They are not a combined CFD/experimental validation-uncertainty interval.*

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
