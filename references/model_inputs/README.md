# Model-input files

| File | Contents |
|---|---|
| `c3x_archived_solid_properties.csv` | solid values recovered from the Fluent case and the conductivity law |
| `material_property_provenance.csv` | baseline-definition source, solution role and independent literature status of each material value |
| `c3x_internal_convection_correction_factors.csv` | archived per-hole `C_r` assignments plus their source qualification |
| `run145_4512_internal_convection.csv` | generated CoolProp properties and convection coefficients |
| `run145_wall_surface_coordinate_reference.csv` | pressure/suction labels for the final wall coordinates |
| `transition_sst_settings.csv` | inlet, Transition SST and discretization settings recovered from the saved case and transcript |

`scripts/preprocess/build_internal_convection_inputs.py --check` rebuilds the
internal-convection table. The hot-gas and solid values used in Fluent are
listed in [`docs/model_setup.md`](../../docs/model_setup.md).

For the generated internal-convection table, CoolProp air properties are
evaluated at each NASA coolant bulk temperature and a fixed `101325 Pa` pressure.
That pressure is a property-evaluation convention in the reduced preprocessing,
not a Run 145 coolant-pressure measurement or a resolved coolant-flow boundary
condition. The NASA passage Reynolds numbers are supplied independently, and
sensitivity to the property-evaluation pressure is not included in the
screening study.

## Internal-convection correction-factor source qualification

Trompoukis et al. (2021), Section 5,
[doi:10.3390/ijtpp6020020](https://doi.org/10.3390/ijtpp6020020), documents the
reduced 2D correlation
`Nu_D = 0.022 C_r Pr^0.5 Re_D^0.8` and states that `C_r` accounts for thermal
entrance-region effects, with values spanning approximately `1.03-1.12` across
the ten C3X channels. That paper attributes `C_r` to Hylton et al. (1983), but
it does not tabulate the ten individual `C_r` assignments.

Accordingly, `c3x_internal_convection_correction_factors.csv` is the repository's
authoritative record of the per-hole assignments used by the released Fluent
states. The individual values are not attributed to a table in Trompoukis et al.;
that publication is cited for the correlation, physical role and approximate
range of `C_r`. The archived assignments remain unchanged so the generated
boundary inputs remain consistent with the released solver states. Changing
them would alter the prescribed cooling boundary conditions and would require
new Fluent runs rather than a documentation-only correction.

## Thermophysical-property definition and citation status

| Domain | Property | Definition used | Role in the steady solution | Baseline record / independent citation |
|---|---|---:|---|---|
| Solid | Density | `8030 kg/m3` | Pseudo-transient path only | Released Fluent state |
| Solid | Specific heat | `473 J/(kg K)` | Pseudo-transient path only | Released Fluent state |
| Solid | Conductivity | `k_s(T)=6.811+0.020176T` W/(m K) | Steady conduction and wall temperature | Released Fluent state; independently matches Prapamonthon et al. (2018), Table 2, doi:10.3390/en11041000 |
| Hot gas | Density | Ideal gas, `M=28.96 kg/kmol` | Compressible-flow response | Released Fluent state |
| Hot gas | Specific heat | `1075 J/(kg K)` | Energy equation | Released Fluent state |
| Hot gas | Dynamic viscosity | `3.33e-05 Pa s` | Reynolds number and turbulence transport | Released Fluent state |
| Hot gas | Thermal conductivity | `0.05234 W/(m K)` | Gas-side heat transfer | Released Fluent state |

The released Fluent state is the authoritative definition of the archived
baseline constants. Independent literature citations are asserted only where
they are directly documented rather than assigned retroactively. The hot-gas
property choices are not included in the present deterministic sensitivity
screening, so the NASA comparison metrics apply to this archived baseline model
definition rather than to a propagated thermophysical-property uncertainty
range. Machine-readable status is in `material_property_provenance.csv`.
