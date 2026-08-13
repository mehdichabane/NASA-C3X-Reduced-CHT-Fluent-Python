# Model-input files

| File | Contents |
|---|---|
| `c3x_archived_solid_properties.csv` | solid values recovered from the Fluent case and the conductivity law |
| `material_property_provenance.csv` | baseline-definition source, solution role and independent literature status of each material value |
| `thermophysical_literature_matches.csv` | exact and derived literature matches for the archived thermophysical constants, with match scope |
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

## Thermophysical-property definition and literature matches

The released Fluent state remains the authoritative definition of the archived
baseline constants. The literature records below are independent matches used to
make the model-input trail auditable; they do **not** prove which source was
consulted when the original Fluent material definitions were selected.

| Domain | Property | Definition used | Independent match and scope |
|---|---|---:|---|
| Solid | Density | `8030 kg/m3` | Exact C3X-literature match in Zheng et al. (2015), doi:10.1615/HeatTransRes.2015007514. That paper uses a different `cp` and conductivity law, so only density is matched. |
| Solid | Specific heat | `473 J/(kg K)` | Exact prior C3X-model match in Bianchini, Facchini & Mangani (2009), 8th European Turbomachinery Congress, University of Florence FLORE record [hdl:2158/420656](https://hdl.handle.net/2158/420656). |
| Solid | Conductivity | `k_s(T)=6.811+0.020176T` W/(m K) | Exact C3X-literature match in Prapamonthon et al. (2018), Table 2, doi:10.3390/en11041000. This citation is restricted to the conductivity law. |
| Hot gas | Density | Ideal gas, `M=28.96 kg/kmol` | Exact prior C3X-model molecular-weight match in Bianchini, Facchini & Mangani (2009). |
| Hot gas | Specific heat | `1075 J/(kg K)` | Exact prior C3X-model match in Bianchini, Facchini & Mangani (2009). |
| Hot gas | Dynamic viscosity | `3.33e-05 Pa s` | Exact prior C3X-model match in Bianchini, Facchini & Mangani (2009). |
| Hot gas | Thermal conductivity | `0.05234 W/(m K)` | Derived rounding match to Bianchini, Facchini & Mangani (2009): their `cp=1075 J/(kg K)`, `mu=3.33e-05 Pa s` and `Pr=0.684` imply `k=cp*mu/Pr=0.0523355263 W/(m K)`, which rounds to `0.05234`. The paper does not directly tabulate that conductivity value. |

Bianchini, Facchini & Mangani's 2009 C3X paper is archived by the University of
Florence as an open-access final refereed postprint. Its thermophysical setup
states `M=28.96 kg/kmol`, `cp=1075 J/(kg K)`, `mu=3.33e-05 kg/(m s)`,
`Pr=0.684`, and a constant ASTM 310 vane specific heat of `473 J/(kg K)`.
Those are direct literature matches to four archived constants; the gas
conductivity match is derived from the published `cp`, `mu` and `Pr` triple.

The density requires a separate qualification. Zheng et al. (2015) uses
`rho=8030 kg/m3` for the NASA C3X ASTM 310 vane, providing an exact independent
C3X match, but uses `cp=502 J/(kg K)` and another conductivity law. It therefore
does not support the archived `473 J/(kg K)` value or the present conductivity
relation.

Likewise, Prapamonthon et al. (2018) must not be read as validating the entire
material table. Its Table 2 uses steel `rho=7854 kg/m3` and
`cp=434 J/(kg K)`, and air `cp=1004.4 J/(kg K)`,
`k=0.0261 W/(m K)` and `mu=1.7831e-05 kg/(m s)`. The exact overlap with this
repository is the solid conductivity law only.

The full machine-readable qualification is in
`thermophysical_literature_matches.csv` and `material_property_provenance.csv`.
The hot-gas property choices are still not included in the present deterministic
sensitivity screening, so the NASA comparison metrics apply to the archived
baseline model definition rather than to a propagated thermophysical-property
uncertainty range.
