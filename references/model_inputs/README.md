# Model-input files

| File | Contents |
|---|---|
| `c3x_archived_solid_properties.csv` | solid values recovered from the Fluent case and the conductivity law |
| `material_property_provenance.csv` | source status and role of each material value |
| `c3x_internal_convection_correction_factors.csv` | `C_r` values and DOI for the ten cooling boundaries |
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
`material_property_provenance.csv`. NIST AIRPROPS is used only as a general
dry-air comparator, not as the missing original source of the archived gas
constants. No uncertainty distribution is assigned to the undocumented choices,
so the reported NASA comparison errors apply to the archived model definition.
