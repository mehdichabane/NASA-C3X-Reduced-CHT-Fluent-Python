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
| Saved Fluent states | matching case/data pairs, SHA-256 manifest and archived live Fluent 26.1 saved-state report audits for the released fine SST and fine Transition SST states |
| Sensitivity-study consistency | committed case matrices and summary tables checked in CI for baseline agreement, expected case coverage and reported cross-case trends |

## Solver-side saved-state audit

`scripts/verification/replay_saved_state_reports.py` can be run in an
environment with a locally installed, licensed Fluent 26.1 instance. Its
separate direct dependency is pinned in `requirements-fluent.txt` as
`ansys-fluent-core==0.40.2`.

The helper explicitly launches Fluent `26.1.0` in 2D double precision with
`ui_mode="no_gui"`, checks the running Fluent version returned by the session,
opens one released `.cas.h5/.dat.h5` pair and recomputes existing scalar report
definitions from the saved state. The default fine-grid reports are external
heat-transfer rate, mean wall temperature and outlet Mach number.

Before launching Fluent, the helper checks that the conventionally matching
`.dat.h5` file is beside the requested `.cas.h5` file. A retained JSON audit
records the SHA-256 digest of both inputs as well as the requested and actual
Fluent version, dimension, precision and UI mode. The hashes can therefore be
checked directly against `fluent/restart_manifest.csv`.

Live executions have now been archived for both released fine-grid states under
[`results/processed/verification/live_saved_state_audits/`](../results/processed/verification/live_saved_state_audits/):

| Saved state | External heat rate [W] | Mean wall temperature [K] | Mass-weighted outlet Mach |
|---|---:|---:|---:|
| fine SST, iter 236 | `35819.60242176461` | `655.619216610248` | `0.9012944409738727` |
| fine Transition SST, iter 556 | `28548.27415186197` | `608.87899709921` | `0.9033510682539843` |

For both audits, the requested and actual Fluent version is `26.1.0`, the session
is 2D double precision with `ui_mode="no_gui"`, and the recorded case/data hashes
match the corresponding entries in `fluent/restart_manifest.csv`. The launch
configuration, local hashing helpers and archived-artifact provenance checks are
covered by CI tests; Fluent itself is not launched in CI.

The commands used by the helper are:

```bash
python -m pip install -r requirements-fluent.txt
python scripts/verification/replay_saved_state_reports.py c3x_run145_nasa_exact_fine_SST_final_iter236.cas.h5 --output run145_sst_fine_saved_state_audit.json
python scripts/verification/replay_saved_state_reports.py c3x_run145_transition_sst_fine_final_iter556.cas.h5 --output run145_transition_sst_fine_saved_state_audit.json
```

The matching `.dat.h5` files must remain beside the case files with the canonical
filenames listed in `fluent/restart_manifest.csv`.

This helper is intentionally outside `run_all.py` and GitHub Actions because the
CI environment does not contain Fluent. The archived executions demonstrate that
the released fine-grid solver states can be reopened through the pinned PyFluent
path and that their stored scalar report definitions can be recomputed. They are
not evidence of a replay from initialization and do not regenerate the full set
of wall and flux exports used by the repository.

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
