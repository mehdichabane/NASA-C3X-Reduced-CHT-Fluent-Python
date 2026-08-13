# Model-input files

| File | Contents |
|---|---|
| `c3x_archived_solid_properties.csv` | solid values recovered from the Fluent case and the conductivity law |
| `material_property_provenance.csv` | baseline-definition source, solution role and independent literature status of each material value |
| `c3x_internal_convection_correction_factors.csv` | per-hole `C_r` values transcribed from NASA-CR-168015 Figure 7 |
| `run145_4512_external_boundary_provenance.csv` | NASA operating-point values, Fluent external boundary inputs and their provenance classification |
| `run145_4512_internal_convection.csv` | generated CoolProp properties and convection coefficients |
| `run145_wall_surface_coordinate_reference.csv` | pressure/suction labels for the final wall coordinates |
| `transition_sst_settings.csv` | inlet, Transition SST and discretization settings recovered from the saved case and transcript |

`scripts/preprocess/build_internal_convection_inputs.py --check` rebuilds the
internal-convection table. The hot-gas and solid values used in Fluent are
listed in [`docs/model_setup.md`](../../docs/model_setup.md).

## External operating-point and boundary-condition provenance

`run145_4512_external_boundary_provenance.csv` separates direct NASA operating
point values from Fluent-specific model inputs and computed outputs.

NASA-CR-168015 Table IX (report p. 30) gives Run 145 / code 4512 as
`PTI = 58.57 psia`, `TTI = 792 K`, `M1 = 0.16`, `M2 = 0.90` and
`Tu = 6.5%`. The Fluent pressure-inlet value `403800 Pa` is the rounded SI
implementation of `58.57 psia = 403825.9 Pa`; the difference is about
`0.0064%`.

The inlet turbulent-viscosity ratio `10` is not a NASA measurement. It is a
Fluent turbulence-boundary modeling input retained in the released solver state.
The value also corresponds to Fluent's default turbulent-viscosity ratio when
using the intensity/viscosity-ratio specification method. Its influence is
explicitly screened in the Transition SST sensitivity study.

The pressure-outlet value `236200 Pa` is likewise classified by provenance rather
than retroactively attributed to the experiment. NASA explains that its reported
exit Mach number uses measured inlet total pressure and average measured
exit-plane static pressure, but Table IX does not tabulate that exit static
pressure numerically for Run 145. The repository therefore treats `236200 Pa`
as the released Fluent baseline pressure-outlet setting. No direct NASA
transcription or unverified isentropic derivation is claimed for that number.
With the Fluent operating pressure set to `0 Pa`, this pressure-outlet setting is
numerically an absolute static pressure.

For the generated internal-convection table, CoolProp air properties are
evaluated at each NASA coolant bulk temperature and a fixed `101325 Pa` pressure.
That pressure is a property-evaluation convention in the reduced preprocessing,
not a Run 145 coolant-pressure measurement or a resolved coolant-flow boundary
condition. The NASA passage Reynolds numbers are supplied independently, and
sensitivity to the property-evaluation pressure is not included in the
screening study.

## Internal-convection source record

Hylton et al., NASA-CR-168015 (1983), directly documents the internal cooling
closure used by the experiment. In the heat-transfer measurement section it
gives

```text
Nu_D = C_r * 0.022 * Pr^0.5 * Re_D^0.8
```

and states that `C_r` corrects the fully developed smooth-pipe expression for
thermal entrance-region effects. For the experimental `Pr`, `Re_D` and `x/D`
range, the report states that `C_r` is approximately `1.03-1.12` and attributes
the correction to its Ref. 22, Crawford and Kays, *Convective Heat and Mass
Transfer* (1980).

More importantly for the released model, NASA Figure 7 (report p. 16) directly
tabulates the ten C3X passage diameters and their individual `C_r` values. The
values in `c3x_internal_convection_correction_factors.csv` are therefore direct
transcriptions of the primary NASA report, not repository-only assignments:

```text
holes 1-7 : C_r = 1.118
holes 8-9 : C_r = 1.056
hole 10   : C_r = 1.025
```

The Run 145 coolant bulk temperatures and passage Reynolds numbers are
transcribed from Appendix A, report p. 181. `run145_4512_internal_convection.csv`
combines those measurements with the Figure 7 diameters and `C_r` values and
CoolProp air properties. This correction changes source attribution and page
metadata only; it does not change the prescribed cooling inputs used by the
released Fluent states.

Trompoukis et al. (2021),
[doi:10.3390/ijtpp6020020](https://doi.org/10.3390/ijtpp6020020), remains a
useful later C3X reference, but it is not needed as the primary source for the
per-hole `C_r` values or for the correlation because both are documented in
NASA-CR-168015 itself.

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