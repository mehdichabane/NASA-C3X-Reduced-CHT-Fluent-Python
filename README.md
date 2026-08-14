# NASA C3X Run 145: reduced RANS/CHT benchmark

[![Rebuild and test analysis](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/actions/workflows/checks.yml/badge.svg?branch=main)](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/actions/workflows/checks.yml)

Verification-focused benchmark of NASA C3X Run 145 using steady two-dimensional
compressible RANS and conjugate heat transfer in Ansys Fluent 26.1. Python
scripts rebuild the processed results, compare them with public NASA data and
check convergence, conservation, mesh sensitivity and sensitivity-study
consistency.

> **Scope.** This is a reduced benchmark, not a complete ASME V&V 20 validation.
> Internal coolant flow, film cooling and three-dimensional effects are not
> resolved, and no combined CFD/experimental validation-uncertainty budget is
> claimed.

## Project snapshot

| Item | Summary |
|---|---|
| Model | Hot-gas passage + solid vane; SST `k-omega` primary; ten cooling passages represented by NASA-derived convection boundary conditions |
| Main comparison | NASA Run 145 pressure, wall temperature and external HTC |
| Numerical checks | Three grids, final-window convergence, mass/interface/solid-energy balances and wall `y+` |
| Sensitivity studies | Transition SST inlet turbulence and prescribed internal-cooling `h` / `Tbulk` |
| Reproducibility | Deterministic Python workflow in CI, released Fluent restart states and archived headless PyFluent saved-state audits |

## Fine-grid SST results

| Metric | Pressure side | Suction side |
|---|---:|---:|
| Wall-temperature MAE / MAPE | `8.887 K / 1.448%` | `12.999 K / 2.005%` |
| HTC MAPE | `7.795%` | `11.535%` |
| Pressure-ratio MAPE | `0.926%` | `3.980%` |

| Global check | Fine SST result |
|---|---:|
| Cells / final iteration | `44,760 / 236` |
| Mass-weighted outlet Mach | `0.901294` |
| Relative mass imbalance | `0.0000509%` |
| Fluid-solid interface mismatch | `0.00000558%` |
| Solid heat imbalance | `0.001921%` |
| Maximum wall `y+` | `0.45189` |

The outlet Mach is an **operating-point check**, not an independent validation
metric. NASA `M2 = 0.90` is pressure-derived, whereas the saved Fluent report is
a mass-flux-weighted average of local outlet Mach. The boundary-condition
selection history is documented in
[`docs/outlet_pressure_selection.md`](docs/outlet_pressure_selection.md).

| Wall temperature | Heat-transfer coefficient |
|---|---|
| ![NASA wall-temperature comparison](results/figures/nasa_comparison/wall_temperature.svg) | ![NASA heat-transfer-coefficient comparison](results/figures/nasa_comparison/heat_transfer_coefficient.svg) |

| Fine mesh | Pressure ratio |
|---|---|
| ![Fine-grid mesh](results/figures/mesh/run145_fine_mesh_overview.png) | ![NASA pressure-ratio comparison](results/figures/nasa_comparison/pressure_ratio.svg) |

HTC error bars show the reported NASA experimental HTC uncertainty only; they
are not a combined CFD/experimental validation band.

## Model scope

The calculation resolves steady compressible external flow, solid conduction
and the gas-solid CHT interface. Ideal-gas density, the energy equation and
second-order final discretization are retained. SST `k-omega` is the primary
model; Transition SST is used as a sensitivity case.

The ten internal passages are present geometrically but their coolant flow is
not solved. Each passage wall receives a NASA-derived, passage-specific
convection condition based on `h` and `Tbulk`. The model also excludes coolant
pressure loss and temperature development, film cooling, endwall flow,
radiation, structural response and unsteady wake passing.

Full equations, boundary conditions, material values and source provenance are
in [`docs/model_setup.md`](docs/model_setup.md).

## Verification and experimental comparison

- **Convergence and conservation.** The accepted SST state retains unchanged
  second-order settings for a final 20-iteration window, with engineering
  monitor spans below `0.02%` and the mass/interface/solid-energy checks shown
  above. See [`docs/convergence_acceptance.md`](docs/convergence_acceptance.md).
- **Mesh sensitivity.** Coarse, medium and fine SST meshes contain `14,657`,
  `23,781` and `44,760` cells. Medium-to-fine changes in outlet Mach, mean wall
  temperature and external heat rate are all below `0.1%`, while local trailing
  edge profiles remain more sensitive. The three meshes support a sensitivity
  assessment, not a formal asymptotic GCI. See
  [`docs/meshing_recipe.md`](docs/meshing_recipe.md).
- **NASA comparison.** Pressure and thermal stations come from
  NASA-CR-168015. The workflow reports bias, MAE, RMSE and MAPE and keeps NASA
  experimental uncertainty separate from unquantified CFD/model-input
  uncertainty. See [`docs/nasa_comparison.md`](docs/nasa_comparison.md).

Transition SST gives pressure errors similar to SST but substantially larger
thermal errors in the retained fine-grid case. It is therefore kept as a model
sensitivity rather than promoted as the primary thermal result; the repository
does not claim an experimentally verified transition location.

## Sensitivity studies

These are deterministic screening studies, not calibration or probabilistic
uncertainty quantification.

| Controlled perturbation | Main observed response |
|---|---|
| Internal cooling `h/h0: 1.00 -> 0.90` | `Tw_mean +6.104 K`; external heat rate `-5.393%`; outlet Mach `+0.000804%` |
| Transition SST `mu_t/mu_in: 10 -> 1` at `Tu_in = 6.5%` | Near-LE `Tu 1.247% -> 0.364%`; transition-like suction response `x/Cx 0.653 -> 0.967`; external heat rate `-19.716%` |
| Transition SST `Tu_in: 6.5% -> 8.3%` at `mu_t/mu_in = 10` | Near-LE `Tu 1.247% -> 1.237%`; `Tw_mean -0.033%`; external heat rate `-0.122%` |

Details are in
[`studies/internal_cooling_sensitivity/README.md`](studies/internal_cooling_sensitivity/README.md)
and
[`studies/transition_sst_sensitivity/README.md`](studies/transition_sst_sensitivity/README.md).

## Reproduce the analysis workflow

Tested in CI with Python 3.13:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt -r requirements-preprocess.txt
python scripts/preprocess/build_internal_convection_inputs.py --check
python scripts/run_all.py
python -m pytest -q
```

`run_all.py` executes 14 processing, verification and plotting stages from the
committed Fluent exports; it does not launch Fluent.

The separate
[Fluent restart release](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/releases/tag/initial-public-release)
contains the retained Fluent 26.1 case/data pairs. SHA-256 values are recorded in
[`fluent/restart_manifest.csv`](fluent/restart_manifest.csv). Archived live
PyFluent audits reopen the released fine SST and fine Transition SST states in
Fluent 26.1 and recompute stored scalar reports. They are saved-state audits,
not initialization-to-final solver replays. See
[`docs/reproducibility.md`](docs/reproducibility.md).

## Technical documentation

- [Model definition and implementation](docs/model_setup.md)
- [Run 145 outlet-pressure selection](docs/outlet_pressure_selection.md)
- [Fine-grid convergence and balances](docs/convergence_acceptance.md)
- [Three-grid mesh record](docs/meshing_recipe.md)
- [NASA comparison and uncertainty interpretation](docs/nasa_comparison.md)
- [Internal cooling sensitivity](studies/internal_cooling_sensitivity/README.md)
- [Transition SST sensitivity](studies/transition_sst_sensitivity/README.md)
- [Reproducibility status](docs/reproducibility.md)
- [Experimental data transcription](references/experimental_data/README.md)

## Source and licence

Primary experimental source: [Hylton et al., *Analytical and Experimental
Evaluation of the Heat Transfer Distribution over the Surfaces of Turbine
Vanes*, NASA-CR-168015, 1983](https://ntrs.nasa.gov/citations/19830020105).

Code is released under the MIT License. Citation metadata are in
[`CITATION.cff`](CITATION.cff). NASA data and Ansys-generated material remain
subject to their original terms; see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
