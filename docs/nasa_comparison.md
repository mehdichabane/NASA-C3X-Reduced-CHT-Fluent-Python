# Comparison with NASA Run 145 measurements

Pressure, wall-temperature and heat-transfer-coefficient (HTC) stations come
from Appendix A, page 180 of Hylton et al., NASA-CR-168015. Regional external-
HTC uncertainty intervals come from Table VI, report page 27. Additional
experimental uncertainties reported in the Data Uncertainties subsection and
Table VII are transcribed in
`references/experimental_data/c3x_experimental_uncertainty_summary.csv`.

The outlet Mach is used only to match the nominal Run 145 operating point. NASA
`M2 = 0.90` and Fluent's mass-weighted outlet Mach are defined differently; the
selection of the `236200 Pa` pressure outlet is documented in
[`outlet_pressure_selection.md`](outlet_pressure_selection.md).

## NASA experimental uncertainty record

NASA's Data Uncertainties subsection reports the component uncertainties used in
the experimental reduction:

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
method (Ref. 23); the `Tu` value is based on prior experience with the laser
Doppler anemometry (LDA) system. Table VI already gives the resulting regional
external-HTC uncertainty, so the component values above are not added again to
those intervals.

NASA also notes that some systematic contributions affect multiple runs in a
similar way, so uncertainty in run-to-run trends can be smaller than uncertainty
in the absolute level.

## Coordinate matching and metrics

Experimental stations are matched to the CFD wall profiles by axial coordinate
`x/Cx`, separately on the pressure and suction sides. Linear interpolation is
used. Bias is defined as CFD minus NASA.

The SST profile comes from the final fine-grid wall export. Transition SST uses
the direct 819-face Fluent wall export at iteration 556. HTC uncertainty bands
are assigned by experimental surface position `s/L` using the Table VI regional
intervals.

`scripts/comparison/compare_run145.py` writes the pointwise tables and summary to
`results/processed/nasa_comparison/` and generates the three figures below.

For wall temperature, mean absolute error (MAE) and root-mean-square error
(RMSE) in kelvin are reported alongside mean absolute percentage error (MAPE).
MAPE is kept as a compact relative summary using absolute temperature in kelvin,
but it should not be read alone because the large absolute temperature baseline
can make percentage errors look small.

Summary bias, MAE, RMSE and MAPE give equal weight to each experimental station.
They are station-wise statistics rather than arc-length-weighted surface
integrals, so regions with denser experimental station placement contribute more
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

At the reported precision, the wall-temperature errors are one-signed over the
sampled stations: SST is systematically hotter than the NASA values, while
Transition SST is systematically colder.

![Wall-temperature comparison](../results/figures/nasa_comparison/wall_temperature.svg)

## Heat-transfer coefficient

| Model | Surface | Points | MAE | RMSE | MAPE | Inside experimental HTC interval |
|---|---|---:|---:|---:|---:|---:|
| SST | Pressure | `31` | `46.954 W/(m²·K)` | `62.406 W/(m²·K)` | `7.795%` | `58.06%` |
| SST | Suction | `44` | `84.320 W/(m²·K)` | `118.616 W/(m²·K)` | `11.535%` | `63.64%` |
| Transition SST | Pressure | `31` | `294.658 W/(m²·K)` | `350.778 W/(m²·K)` | `47.443%` | `9.68%` |
| Transition SST | Suction | `44` | `281.010 W/(m²·K)` | `389.862 W/(m²·K)` | `32.232%` | `31.82%` |

![Heat-transfer-coefficient comparison](../results/figures/nasa_comparison/heat_transfer_coefficient.svg)

The HTC error bars use the Table VI experimental uncertainty intervals.

## Why SST remains the primary case

Transition SST gives pressure errors close to SST but substantially worsens the
wall-temperature and HTC comparison on the current fine grid. The separate
[`Transition SST inlet-turbulence sensitivity study`](../studies/transition_sst_sensitivity/README.md)
also shows that the suction-side transition-like response is strongly affected
by turbulence decay between the inlet and the vane, especially through the
inlet turbulent-viscosity ratio.

Transition SST is therefore retained as a sensitivity case rather than the
baseline. No coarse or medium Transition SST cases were run, so the reported
transition-response locations are fine-grid diagnostics.
