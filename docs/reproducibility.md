# Reproducibility status

## Commands tested on the repository contents

```bash
python -m venv .venv
python -m pip install -r requirements.txt -r requirements-preprocess.txt
python scripts/preprocess/build_internal_convection_inputs.py --check
python scripts/run_all.py
python -m pytest -q
git diff --exit-code
```

The Python workflow uses repository-relative paths. It rebuilds geometry import
files, processed tables, numerical checks and figures from committed Fluent CSV
and text exports. SVG output uses a fixed Matplotlib hash salt and omits date
metadata, so unchanged inputs produce identical SVG files. The workflow does not
run Fluent.

## What can be reproduced

| Item | Available evidence |
|---|---|
| Python processing | source scripts, pinned dependencies and regression tests |
| Internal convection coefficients | NASA coolant rows, geometry, `C_r`, CoolProp script and committed output |
| SST and Transition SST comparison profiles | direct wall exports and coordinate reference |
| Mesh-quality tables | CFF parser and released SST case files |
| Solid temperature gradient | solid temperatures, CFF adjacency and linear-field test |
| Saved Fluent states | matching case/data pairs and SHA-256 manifest |
| Sensitivity-study consistency | committed case matrices and summary tables checked in CI for baseline agreement, expected case coverage and reported cross-case trends |

## Optional solver-side saved-state audit

`scripts/verification/replay_saved_state_reports.py` can be run in an
environment with PyFluent and a locally installed, licensed Fluent instance. It
opens one released `.cas.h5/.dat.h5` pair and recomputes existing scalar report
definitions from the saved state. The default fine-grid reports are external
heat-transfer rate, mean wall temperature and outlet Mach number.

This helper is intentionally outside `run_all.py` and GitHub Actions because the
CI environment does not contain Fluent. It narrows the gap between the released
solver state and the Python post-processing, but it is not evidence of a replay
from initialization and does not regenerate the full set of wall and flux
exports used by the repository.

## What cannot be replayed from the repository

The original SpaceClaim and Ansys Meshing GUI history was not saved. The source
curves and saved meshes are available, but the operation sequence and several
mesh controls are missing.

The repository does not contain a complete replay from initialization with a
transcript, final monitors, balances and comparison against the saved iteration
236 state. Equivalence from initialization is therefore unresolved.

The Fluent solves that generated the internal-cooling and Transition SST
sensitivity-study CSVs are also not replayed by the Python workflow. CI checks
the internal consistency and headline relationships of those committed study
outputs; it does not establish solver-run equivalence for the sensitivity cases.

Several material constants are recoverable from the saved case but lack their
original source-selection record. Their status is listed in
[`references/model_inputs/README.md`](../references/model_inputs/README.md).
