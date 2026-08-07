# NASA C3X Run 145: reduced RANS/CHT benchmark

[![Rebuild and test analysis](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/actions/workflows/checks.yml/badge.svg?branch=main)](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/actions/workflows/checks.yml)

Steady two-dimensional compressible RANS and conjugate heat-transfer model of
the NASA C3X turbine vane, solved with Ansys Fluent 26.1 and checked with
Python. The repository is intended for readers who already know basic CFD and
Fluent; it is not a Fluent tutorial.

The hot-gas passage and solid vane are resolved. The ten internal passages use
passage-specific convection boundary conditions, so coolant flow and film
cooling are not resolved.

**Skills shown:** compressible CFD, conjugate heat transfer, mesh verification,
experimental comparison, Python automation and regression testing.

## Fine-grid SST results

| Quantity | Result |
|---|---:|
| Final iteration | `236` |
| Outlet Mach number | `0.901` |
| Wall-temperature MAPE | `1.448%` pressure / `2.005%` suction |
| HTC MAPE | `7.795%` pressure / `11.535%` suction |
| Pressure-ratio MAPE | `0.926%` pressure / `3.980%` suction |
| Relative mass imbalance | `5.1e-5%` |
| Fluid-solid interface mismatch | `5.6e-6%` |
| Solid heat imbalance | `0.0019%` |
| Maximum wall `y+` | `0.452` |

| Wall temperature | Heat-transfer coefficient |
|---|---|
| ![NASA wall-temperature comparison](results/figures/nasa_comparison/wall_temperature.svg) | ![NASA heat-transfer-coefficient comparison](results/figures/nasa_comparison/heat_transfer_coefficient.svg) |

| Fine mesh | Pressure ratio |
|---|---|
| ![Fine-grid mesh](results/figures/mesh/run145_fine_mesh_overview.png) | ![NASA pressure-ratio comparison](results/figures/nasa_comparison/pressure_ratio.svg) |

## Reduced model

Included:

- steady 2D compressible external flow;
- ideal-gas density and the energy equation;
- translationally periodic cascade passage;
- gas-solid conjugate heat transfer;
- SST `k-omega` as the primary turbulence model;
- fine-grid Transition SST sensitivity case;
- second-order final discretization.

Excluded:

- resolved coolant flow and coolant pressure loss;
- film cooling;
- three-dimensional endwall effects;
- radiation, structural response and wake passing.

The model definition, equations, boundary conditions, material values and links
to their implementations are in [`docs/model_setup.md`](docs/model_setup.md).

## Three-grid and balance checks

| Mesh | Cells | External wall faces | Final SST iteration |
|---|---:|---:|---:|
| Coarse | `14,657` | `311` | `156` |
| Medium | `23,781` | `473` | `161` |
| Fine | `44,760` | `819` | `236` |

Medium-to-fine changes are `0.0972%` for outlet Mach, `0.0332%` for mean
external wall temperature and `0.0837%` for external heat-transfer rate. These
values are a three-grid sensitivity result, not a formal asymptotic GCI.

The fine SST calculation continued for 20 iterations after the active
continuity criterion was first met. The final-window monitor spans and the mass,
interface and solid-energy balances are listed in
[`docs/convergence_acceptance.md`](docs/convergence_acceptance.md). Mesh quality
and missing GUI settings are recorded in
[`docs/meshing_recipe.md`](docs/meshing_recipe.md).

## Comparison with Run 145 measurements

Appendix A, page 180 of NASA-CR-168015 supplies the pressure, wall-temperature
and HTC stations used here. CFD profiles are matched by axial coordinate on the
pressure and suction sides. `scripts/comparison/compare_run145.py` calculates
bias, MAE, RMSE, maximum absolute error and MAPE.

Transition SST gives similar pressure errors but much larger thermal errors. It
is kept as a sensitivity case rather than used as the primary thermal result.
The mapping, point counts, metrics and interpretation limits are in
[`docs/nasa_comparison.md`](docs/nasa_comparison.md).

The repository reports a benchmark comparison and numerical verification
assessment. It does not claim a complete [ASME V&V 20](https://www.asme.org/codes-standards/find-codes-standards/standard-for-verification-and-validation-in-computational-fluid-dynamics-and-heat-transfer/2009)
validation because the experiment and model inputs do not have a combined
uncertainty budget.

## Run from a fresh clone

Tested with Python 3.13.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python scripts/run_all.py
python -m pytest -q
```

`run_all.py` executes 13 project-specific processing, verification and plotting
stages. It reads the committed Fluent exports and does not launch Fluent.

To rebuild the ten internal-convection inputs, install CoolProp and run the
separate check:

```bash
python -m pip install -r requirements-preprocess.txt
python scripts/preprocess/build_internal_convection_inputs.py --check
```

## Saved Fluent states

The matching [Fluent restart release](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/releases/tag/initial-public-release)
contains Fluent 26.1 case/data pairs for coarse, medium and fine SST, plus the
fine Transition SST case. Filenames, iterations, cell counts and SHA-256 values
are in [`fluent/restart_manifest.csv`](fluent/restart_manifest.csv). Reopening
steps are in [`fluent/README.md`](fluent/README.md).

The saved states can be reopened. The original SpaceClaim and Ansys Meshing GUI
history was not retained. No complete replay from initialization, with a
transcript and final-state equivalence checks, is included. The exact status is
summarized in
[`docs/reproducibility.md`](docs/reproducibility.md).

## Technical notes

- [Model definition and implementation](docs/model_setup.md)
- [Fine-grid convergence and balances](docs/convergence_acceptance.md)
- [Three-grid mesh record](docs/meshing_recipe.md)
- [NASA coordinate matching and error metrics](docs/nasa_comparison.md)
- [Reproducibility status](docs/reproducibility.md)
- [Experimental data transcription](references/experimental_data/README.md)

## Known limits

- The model is steady and two-dimensional.
- Internal cooling is represented by prescribed convection boundaries.
- The original interactive meshing history was not saved.
- Some material values lack their original source-selection record.
- Input-property uncertainty is not propagated into the comparison metrics.
- No coarse or medium Transition SST calculation is included.

## Source and licence

Primary experimental source: [Hylton et al., *Analytical and Experimental
Evaluation of the Heat Transfer Distribution over the Surfaces of Turbine
Vanes*, NASA-CR-168015, 1983](https://ntrs.nasa.gov/citations/19830020105).

Code is released under the MIT License. NASA data and Ansys-generated material
remain subject to their original terms; see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
