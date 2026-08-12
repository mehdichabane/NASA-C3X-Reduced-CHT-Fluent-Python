# Model-input files

| File | Contents |
|---|---|
| `c3x_archived_solid_properties.csv` | solid values recovered from the Fluent case and the conductivity law |
| `material_property_provenance.csv` | source status and role of each material value |
| `c3x_internal_convection_correction_factors.csv` | archived per-hole `C_r` assignments plus their provenance qualification |
| `run145_4512_internal_convection.csv` | generated CoolProp properties and convection coefficients |
| `run145_wall_surface_coordinate_reference.csv` | pressure/suction labels for the final wall coordinates |
| `transition_sst_settings.csv` | inlet, Transition SST and discretization settings recovered from the saved case and transcript |

`scripts/preprocess/build_internal_convection_inputs.py --check` rebuilds the
internal-convection table. The hot-gas and solid values used in Fluent are
listed in [`docs/model_setup.md`](../../docs/model_setup.md).

For the generated internal-convection table, CoolProp air properties are
evaluated at each NASA coolant bulk temperature and a fixed `101325 Pa` pressure.
That pressure is a property-evaluation convention in the reduced preprocessing,
not a retained Run 145 coolant-pressure measurement or a resolved coolant-flow
boundary condition. The NASA passage Reynolds numbers are supplied independently,
and sensitivity to the property-evaluation pressure is not included in the
screening study.

## Internal-convection correction-factor provenance

Trompoukis et al. (2021), Section 5,
[doi:10.3390/ijtpp6020020](https://doi.org/10.3390/ijtpp6020020), documents the
reduced 2D correlation
`Nu_D = 0.022 C_r Pr^0.5 Re_D^0.8` and states that `C_r` accounts for thermal
entrance-region effects, with values spanning approximately `1.03-1.12` across
the ten C3X channels. That paper attributes `C_r` to Hylton et al. (1983), but
it does not tabulate the ten individual `C_r` values.

The exact per-hole assignments in
`c3x_internal_convection_correction_factors.csv` are therefore treated as
archived project inputs whose original per-hole transcription record was not
retained. They are not presented as independently re-transcribed values from
Trompoukis et al. The values are kept unchanged here so the generated boundary
inputs remain consistent with the released Fluent states; changing them would
change the prescribed cooling boundary conditions and would require new solver
runs rather than a documentation-only correction.

## Thermophysical-property provenance

| Domain | Property | Definition used | Role in the steady solution | Source record |
|---|---|---:|---|---|
| Solid | Density | `8030 kg/m3` | Pseudo-transient path only | Not retained |
| Solid | Specific heat | `473 J/(kg K)` | Pseudo-transient path only | Not retained |
| Solid | Conductivity | `k_s(T)=6.811+0.020176T` W/(m K) | Steady conduction and wall temperature | Prapamonthon et al. (2018), Table 2, doi:10.3390/en11041000 |
| Hot gas | Density | Ideal gas, `M=28.96 kg/kmol` | Compressible-flow response | Not retained |
| Hot gas | Specific heat | `1075 J/(kg K)` | Energy equation | Not retained |
| Hot gas | Dynamic viscosity | `3.33e-05 Pa s` | Reynolds number and turbulence transport | Not retained |
| Hot gas | Thermal conductivity | `0.05234 W/(m K)` | Gas-side heat transfer | Not retained |

The exact values and source status are stored in
`material_property_provenance.csv`. No external source is assigned retroactively
to values whose original source-selection record is missing, and no uncertainty
distribution is assigned to those undocumented choices. The reported NASA
comparison errors therefore apply to the archived model definition rather than
to a propagated property-uncertainty range.
