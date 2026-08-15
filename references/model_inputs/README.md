# Model-input files

| File | Contents |
|---|---|
| `c3x_archived_solid_properties.csv` | solid values recovered from the Fluent case and the conductivity law |
| `material_property_provenance.csv` | baseline-definition source, solution role and literature status of each material value |
| `thermophysical_literature_matches.csv` | exact and derived literature matches for the archived thermophysical constants |
| `c3x_internal_convection_correction_factors.csv` | per-hole `C_r` values transcribed from NASA-CR-168015 Figure 7 |
| `run145_4512_external_boundary_provenance.csv` | NASA operating-point values, Fluent boundary inputs and computed outlet Mach |
| `run145_outlet_pressure_selection.csv` | pressure-outlet selection record and isentropic update |
| `run145_4512_internal_convection.csv` | generated CoolProp properties and convection coefficients |
| `run145_wall_surface_coordinate_reference.csv` | pressure/suction labels for the final wall coordinates |
| `transition_sst_settings.csv` | inlet, Transition SST and discretization settings recovered from the saved case and transcript |

The complete Fluent setup is documented in
[`docs/model_setup.md`](../../docs/model_setup.md). The outlet-pressure adjustment
has its own short record in
[`docs/outlet_pressure_selection.md`](../../docs/outlet_pressure_selection.md).

## External boundary inputs

`run145_4512_external_boundary_provenance.csv` separates direct NASA operating
conditions from Fluent-specific inputs and computed quantities. NASA-CR-168015
Table IX gives Run 145 (code 4512) as `PTI = 58.57 psia`, `TTI = 792 K`,
`M1 = 0.16`, `M2 = 0.90` and `Tu = 6.5%`. The Fluent inlet total pressure
`403800 Pa` is the rounded SI implementation of the NASA value.

The inlet turbulent-viscosity ratio `10` is a Fluent modelling input, not a NASA
measurement. The pressure outlet `236200 Pa` was selected to reproduce the
nominal Run 145 exit-Mach operating point with the Fluent mass-weighted outlet
Mach report; it was not transcribed from a NASA exit-pressure table. The full
`241200 Pa -> 236200 Pa` adjustment sequence is kept in
[`run145_outlet_pressure_selection.csv`](run145_outlet_pressure_selection.csv)
and the dedicated engineering note linked above.

## Reduced internal cooling

The ten internal passage walls use prescribed convection rather than resolved
coolant flow. The model uses the NASA correlation

```text
Nu_D = C_r * 0.022 * Pr^0.5 * Re_D^0.8
h = Nu_D * k_air / D
```

NASA Figure 7 (report p. 16) supplies the passage diameters and per-hole
correction factors: `C_r = 1.118` for holes 1-7, `1.056` for holes 8-9 and
`1.025` for hole 10. Run 145 coolant bulk temperatures and Reynolds numbers come
from Appendix A, report p. 181.

`run145_4512_internal_convection.csv` combines those NASA quantities with
CoolProp air properties evaluated at each bulk temperature and `101325 Pa`.
That pressure is only the property-evaluation convention used by the
preprocessing script; the NASA passage Reynolds numbers are supplied
independently. Rebuild/check the table with:

```text
python scripts/preprocess/build_internal_convection_inputs.py --check
```

## Material values and literature checks

The archived Fluent baseline uses:

| Domain | Property | Fluent definition | Literature cross-check |
|---|---|---:|---|
| Solid | Density | `8030 kg/m3` | Zheng et al. (2015), C3X density match |
| Solid | Specific heat | `473 J/(kg K)` | Bianchini, Facchini & Mangani (2009), prior C3X-model match |
| Solid | Conductivity | `k_s(T)=6.811+0.020176T` W/(m K) | Prapamonthon et al. (2018), Table 2 |
| Hot gas | Density | ideal gas, `M=28.96 kg/kmol` | Bianchini, Facchini & Mangani (2009) |
| Hot gas | Specific heat | `1075 J/(kg K)` | Bianchini, Facchini & Mangani (2009) |
| Hot gas | Dynamic viscosity | `3.33e-05 Pa s` | Bianchini, Facchini & Mangani (2009) |
| Hot gas | Thermal conductivity | `0.05234 W/(m K)` | rounds from the Bianchini `cp`, `mu` and `Pr` values |

These literature entries are independent consistency checks on the archived
setup, not a reconstruction of which source was consulted when the original
Fluent material definitions were entered. The detailed match scope remains in
`thermophysical_literature_matches.csv` and `material_property_provenance.csv`.
