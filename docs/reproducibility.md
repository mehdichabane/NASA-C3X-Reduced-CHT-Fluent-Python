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

The requirement files pin the project's direct Python dependencies, but they are
not a complete transitive lockfile or a frozen operating-system image. GitHub
Actions runs the checks on ubuntu-24.04 with Python 3.13.
Accordingly, the repository demonstrates deterministic regenerated outputs in
the tested CI environment; it does not claim a bit-for-bit freeze of every
transitive package or runner component.

## What can be reproduced

| Item | Available evidence |
|---|---|
| Python processing | source scripts, version-pinned direct dependencies, regression tests and the CI workflow |
| Internal convection coefficients | NASA coolant rows, geometry, `C_r`, CoolProp script and committed output |
| SST and Transition SST comparison profiles | direct wall exports and coordinate reference |
| Mesh-quality tables | CFF parser and released SST case files |
| Solid temperature gradient | solid temperatures, CFF adjacency and linear-field test |
| Saved Fluent states | matching case/data pairs and SHA-256 manifest |
| Sensitivity-study consistency | committed case matrices and summary tables checked in CI for baseline agreement, expected case coverage and reported cross-case trends |

## Optional solver-side saved-state audit

`scripts/verification/replay_saved_state_reports.py` can be run in an
environment with a locally installed, licensed Fluent 26.1 instance. Its
separate direct dependency is pinned in `requirements-fluent.txt` as
`ansys-fluent-core==0.40.2`.

The helper explicitly launches Fluent `26.1.0` in 2D double precision, checks
the running Fluent version returned by the session, opens one released
`.cas.h5/.dat.h5` pair and recomputes existing scalar report definitions from
the saved state. The default fine-grid reports are external heat-transfer rate,
mean wall temperature and outlet Mach number.

The launch configuration is unit-tested in CI without a Fluent installation.
No JSON produced by an actual licensed Fluent 26.1 execution is committed at
present, so the repository demonstrates the audit configuration and released
solver state, not a recorded live execution of that audit.

A local live audit can be recorded explicitly with:

```bash
python -m pip install -r requirements-fluent.txt
python scripts/verification/replay_saved_state_reports.py PATH_TO_FINE_CASE.cas.h5 --output saved_state_report_audit.json
```

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

The released Fluent state is the authoritative baseline-definition record for
material constants used by the archived calculations. Independent literature
matches are recorded with explicit exact or derived scope in
`references/model_inputs/`; thermophysical-property sensitivity remains outside
the current screening scope. Their exact status is listed in
[`references/model_inputs/README.md`](../references/model_inputs/README.md).
