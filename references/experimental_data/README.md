# Run 145 experimental data

The experimental source is Hylton et al., NASA-CR-168015. The files in this
folder are compact transcriptions of the public Run 145 measurements, coolant
quantities and experimental-uncertainty information used or referenced by the
Python workflow.

## External thermal data

`run145_4512_heat_transfer_temperature.csv` keeps both the normalized values
transcribed from Appendix A, page 180, and their dimensional reconstruction.
The conversion used in the project is explicit:

```text
T_ref = 811 K
HTC_ref = 1135 W/(m²·K)
T_wall = T_norm × T_ref
h_exp = h_norm × HTC_ref
```

For example, the first pressure-side station gives
`0.8385 × 811 K = 680.024 K` and
`0.5425 × 1135 W/(m²·K) = 615.738 W/(m²·K)` after rounding.

`T_ref = 811 K` is the reference temperature used to dimensionalize the NASA
thermal table. It is not the Fluent inlet total temperature, which is `792 K`.
For the CFD comparison, the heat-transfer coefficient is evaluated with the
same reference temperature:

```text
q_into_vane = -q_fluent,fluid-side
h_CFD = q_into_vane / (811 K - T_wall)
```

## Experimental uncertainty record

NASA-CR-168015 contains more uncertainty information than the regional external
HTC intervals alone. `c3x_experimental_uncertainty_summary.csv` transcribes the
additional values explicitly reported in the Data Uncertainties subsection and
Table VII:

| Quantity | NASA uncertainty | Report page |
|---|---:|---:|
| External vane surface temperature | about `±1 °C` | `24` |
| Free-stream gas temperature | about `±11 °C` | `24` |
| External airfoil profile | about `±0.008 cm` | `24` |
| Cooling-hole location | about `±0.013 cm` | `24` |
| Cooling-hole diameter | `±0.005 cm` | `24` |
| Internal cooling-hole HTC calculation | estimated `±3%` | `24` |
| Vane-material thermal conductivity used in the experimental reduction | about `±3%` | `24` |
| Pressure measurement | `±0.7 kPa` | `27` |
| Reynolds number, `Re` | `±3.1%` | `28`, Table VII |
| Mach number, `MN` | `±0.9%` | `28`, Table VII |
| Wall-to-gas temperature ratio, `Tw/Tg` | `±2.0%` | `28`, Table VII |
| Inlet turbulence intensity, `Tu` | `±10.0%` | `28`, Table VII |

NASA states that the key uncertainty analysis uses the Kline and McClintock
method (its Ref. 23). The `Tu` value is reported separately as being based on
significant prior experience with the LDA system.

The existing `c3x_heat_transfer_uncertainty_table_VI.csv` is a different level
of uncertainty information: Table VI reports the *resulting regional uncertainty
in the external C3X heat-transfer coefficient* after the experimental reduction.
The component uncertainties above must therefore not be added again to the
Table VI HTC intervals. In this repository, Table VI remains the only uncertainty
used to draw HTC error bars and to calculate the fraction of CFD stations inside
the reported experimental HTC interval.

NASA also notes that these uncertainties are intended to indicate uncertainty in
the absolute level when the data are used for verification. Some common
systematic contributions can affect multiple runs similarly, so uncertainty in
run-to-run trends may be smaller than the absolute-level values.

None of the values in `c3x_experimental_uncertainty_summary.csv` is propagated
through the CFD model in the current repository. They document the experimental
evidence and its limitations; they are not a combined CFD/experimental
validation-uncertainty budget.

## Reduced internal convection

The directly transcribed NASA coolant quantities remain in
`run145_4512_coolant_flow.csv`. They come from the Run 145 coolant-flow table in
Appendix A, report page 181. The derived passage-specific convection table is a
model input, not an experimental measurement, and is therefore stored under
`references/model_inputs/run145_4512_internal_convection.csv`. Its complete
CoolProp-based reconstruction is implemented in
`scripts/preprocess/build_internal_convection_inputs.py`.

Passage diameters and the individual `C_r` correction factors used by that
reconstruction are direct transcriptions of NASA Figure 7 (report p. 16).

## Other files

- `run145_4512_pressure.csv`: external static-pressure measurements;
- `run145_4512_coolant_flow.csv`: coolant-flow quantities transcribed from the
  Run 145 Appendix A table on report page 181;
- `c3x_heat_transfer_uncertainty_table_VI.csv`: regional external-HTC
  uncertainty intervals from NASA Table VI used for the HTC comparison;
- `c3x_experimental_uncertainty_summary.csv`: additional measurement,
  geometry, reduction-input and test-parameter uncertainties reported by NASA.
