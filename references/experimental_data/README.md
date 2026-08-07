# Run 145 experimental data

The experimental source is Hylton et al., NASA-CR-168015. The files in this
folder are compact transcriptions of the public Run 145 measurements and coolant
quantities used by the Python workflow.

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

## Reduced internal convection

The directly transcribed NASA coolant quantities remain in
`run145_4512_coolant_flow.csv`. The derived passage-specific convection table is
a model input, not an experimental measurement, and is therefore stored under
`references/model_inputs/run145_4512_internal_convection.csv`. Its complete
CoolProp-based reconstruction is implemented in
`scripts/preprocess/build_internal_convection_inputs.py`.

## Other files

- `run145_4512_pressure.csv`: external static-pressure measurements;
- `run145_4512_coolant_flow.csv`: coolant-flow quantities transcribed from the
  Run 145 Appendix A table;
- `c3x_heat_transfer_uncertainty_table_VI.csv`: uncertainty intervals used for
  the HTC comparison.
