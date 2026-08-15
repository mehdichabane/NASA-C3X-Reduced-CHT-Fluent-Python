# Retrospective development history

This is an **evidence-backed retrospective history** of the NASA C3X Run 145
benchmark. The CFD work was already substantially developed when the repository
was first published, so this page does not invent a week-by-week pre-public Git
history or backdate commits.

The record deliberately separates two kinds of evidence:

- **solver evidence** — Fluent case/data pairs, iterations, hashes, transcripts,
  monitors and exports can establish facts about retained CFD states;
- **public repository evidence** — commits, pull requests, CI runs and releases
  establish when repository content became public and how it subsequently
  changed.

GitHub documents commits as records of specific changes with a unique SHA,
author and time, while pull requests collect the commits, checks and file changes
used to review a branch before merge:

- <https://docs.github.com/en/pull-requests/reference/commits>
- <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/getting-started/about-pull-requests>
- <https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/using-the-activity-view-to-see-changes-to-a-repository>

## Evidence boundary

| Evidence | What it supports | What it does not prove by itself |
|---|---|---|
| Fluent case/data pair | retained mesh, setup and solved state | original creation date or every earlier trial |
| Fluent transcript / monitor / export | chronology or quantities explicitly recorded there | undocumented actions outside the retained record |
| SHA-256 manifest | identity of the released binary artifact | when the private work began |
| Git commit | repository state/change, Git author and time | when a pre-existing local CFD file was originally created |
| Pull request / CI | visible branch-to-main change and automated checks | unaided authorship of every line |
| GitHub release | public availability of named assets at a recorded time | an earlier private calendar timeline |

The current Git tree does not preserve the original workstation modification
times needed to date the private Fluent work reliably. Those timestamps are not
reconstructed from present Git metadata or filenames.

## 1. Retained solver states

The accepted Fluent states are identified in
[`../fluent/restart_manifest.csv`](../fluent/restart_manifest.csv):

| Model / grid | Cells | Final iteration | Retained evidence |
|---|---:|---:|---|
| coarse SST | `14,657` | `156` | case/data + SHA-256 |
| medium SST | `23,781` | `161` | case/data + SHA-256 |
| fine SST | `44,760` | `236` | case/data + SHA-256 |
| fine Transition SST | `44,760` | `556` | case/data + SHA-256 + transcript/monitors/direct wall export |

This establishes a real four-state Fluent evidence set. It **does not** prove a
calendar date for each solve or a coarse -> medium -> fine execution order, so
no such ordering is asserted here.

### Fine SST state

The accepted fine SST state is iteration `236`. The committed solver evidence
includes full/final residual histories, engineering monitors, mass/interface/
solid-energy checks, wall `y+`, mesh audits and wall/field exports. The active
continuity criterion was first met at iteration `216`; iterations `217-236` are
the final unchanged second-order confirmation window. See
[`convergence_acceptance.md`](convergence_acceptance.md).

### One retained engineering adjustment sequence

The outlet-pressure record preserves an actual pre-release adjustment sequence,
without attaching unsupported calendar dates to it:

| Stage | Outlet pressure | Fluent mass-weighted outlet Mach |
|---|---:|---:|
| provisional second-order state | `241200 Pa` | `0.88064076` |
| local isentropic control estimate | `236228.236 Pa` | not a solved state |
| applied rounded setting | `236200 Pa` | `0.89951531` |
| released fine SST baseline | `236200 Pa` | `0.90129444` |

The calculation and interpretation are in
[`outlet_pressure_selection.md`](outlet_pressure_selection.md). This sequence is
useful because it preserves a provisional condition, the engineering calculation
used to change it and the subsequent Fluent response. It also records the later
methodological clarification that NASA `M2` and Fluent's mass-weighted outlet
Mach are not definition-identical observables.

### Transition SST chronology

The Transition SST history is unusually well preserved by the restart-bundle
transcript and monitor record. The sequence begins from the accepted fine SST
state at iteration `236`:

1. Transition SST is enabled from the iteration-236 SST state.
2. A warm-start case/data pair is saved before the stabilization change.
3. `k`, `omega`, intermittency and `Re_theta_t` use scheme index `0` (First
   Order Upwind) through iteration `386`.
4. A first-order iteration-386 checkpoint is saved.
5. Those four equations are changed to scheme index `1` (Second Order Upwind).
6. The iteration-386 state is saved again before further iteration.
7. The calculation continues to iteration `556`.
8. Iteration `536` is retained as a converged candidate and iterations
   `537-556` form the final unchanged confirmation window.

Pressure interpolation and density, momentum and energy convection retain their
existing second-order settings through this chronology. See
[`../fluent/README.md`](../fluent/README.md).

The direct iteration-556 wall export provides an independent traceability path:
it contains all `819` external wall faces and reproduces the saved wall heat
rate, mean wall temperature and wall-`y+` reports. See
[`../data/fluent_exports/transition_sst/PROVENANCE.md`](../data/fluent_exports/transition_sst/PROVENANCE.md).

## 2. First public snapshot — 7 August 2026

The public Git history begins with commit
[`12a311d`](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/commit/12a311db3d0cf794a0fb0e150a850e2070bfa8ff),
**“Publish NASA C3X Run 145 benchmark,”** recorded at
`2026-08-07 11:02:56 UTC`.

That initial commit already contains a mature benchmark: the reduced RANS/CHT
model, three SST grids, the fine Transition SST result, NASA pressure/thermal
comparison, convergence and conservation evidence, Fluent exports, Python
analysis, tests/CI and explicit reproducibility limitations.

The defensible inference is therefore narrow: these materials were present in
the public project **no later than 7 August 2026**. The commit does not reveal
when each underlying private Fluent file was first created or how long the
pre-public work took.

The
[`initial-public-release`](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/releases/tag/initial-public-release)
was published at `2026-08-07 11:12:42 UTC`. Its restart ZIP exposed the coarse,
medium and fine SST states and the fine Transition SST state with checksums, plus
the Transition transcript/monitor/direct-wall evidence. Thus the binary CFD
artifacts accompanied the original public project rather than appearing only
after the later documentation work.

## 3. Git-backed development after publication

From 7 August onward, the chronology is Git-backed. The main milestones are:

| Date | Public change | What changed |
|---|---|---|
| 10 Aug | [PR #1](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/1) | completed the five-point `h` / `Tbulk` internal-cooling sensitivity families and `h x Tbulk` interaction study |
| 12 Aug | [PRs #2-#4](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pulls?q=is%3Apr+is%3Aclosed) | narrowed Transition/mesh claims and tightened provenance/repository hygiene without changing CFD results |
| 13 Aug | PRs #5-#13 | made external BC, material, uncertainty and turbulence-input provenance explicit; pinned CI; recovered the outlet-pressure selection record |
| 14 Aug | PRs #14-#19 | recovered exact Transition SST scheme chronology, clarified NASA-vs-Fluent Mach definitions, created and archived live saved-state audits, and tightened portfolio presentation |
| 15 Aug | [PR #20](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/20) | mapped NASA's `+/-3%` internal-HTC magnitude onto the existing sensitivity family without claiming formal UQ |
| 15 Aug | [PR #21](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/21) | refocused the README without changing science |
| 15 Aug | [PR #22](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/22) | added the retrospective engineering decision record |

The August 12-14 changes are intentionally kept in the history even when they
correct wording or narrow a claim. A credible development record should show
methodological corrections rather than erase them.

### Saved-state audit milestone

PRs #16-#17 added and then executed a headless Fluent 26.1/PyFluent audit of the
released fine states. The archived executions recompute:

| Saved state | External heat rate | Mean wall temperature | Mass-weighted outlet Mach |
|---|---:|---:|---:|
| fine SST, iter 236 | `35819.60242176461 W` | `655.619216610248 K` | `0.9012944409738727` |
| fine Transition SST, iter 556 | `28548.27415186197 W` | `608.87899709921 K` | `0.9033510682539843` |

The audit JSONs record case/data hashes matching the release manifest. This
shows that the released fine states can be reopened and their stored report
definitions recomputed. It does **not** replay initialization or the full solver
history. The exact boundary is in [`reproducibility.md`](reproducibility.md).

The
[`portfolio-snapshot-2026-08-14`](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/releases/tag/portfolio-snapshot-2026-08-14)
release captures that later verification/provenance/sensitivity state.

## 4. Evidence chain visible to a reviewer

```text
NASA source data + geometry
        |
        v
model-input provenance + generated cooling inputs
        |
        v
Fluent case/data states + exports + monitors + transcript
        |
        +--> SHA-256 restart manifest
        |
        v
deterministic Python processing and numerical checks
        |
        v
first public commit + restart release (7 Aug 2026)
        |
        v
PR/CI history of sensitivities, corrections and provenance work
        |
        v
live Fluent 26.1 saved-state audits + portfolio snapshot
```

Each layer answers a different question. Source records identify input origins;
solver artifacts establish the retained CFD states; scripts show how derived
metrics are produced; Git records public evolution; CI checks regression
consistency.

## 5. What this history supports — and what it does not

It supports that a mature benchmark and its four retained restart states were
publicly present on 7 August 2026; that Transition SST has a preserved internal
solver chronology; that the outlet-pressure adjustment has a retained
engineering sequence; and that later extensions/corrections were made through
visible PRs and CI.

It **does not** support claims about:

- the exact start date or duration of the private pre-public work;
- original workstation modification times;
- an exact chronological order among the three accepted SST grid solves;
- every rejected pre-public geometry, mesh, BC or solver trial;
- the original SpaceClaim/Ansys Meshing GUI history;
- bit-for-bit regeneration of the original meshes;
- initialization-to-iteration-236 final-state equivalence;
- full solver replay of every sensitivity case;
- unaided authorship of every line of code/documentation;
- authorship of NASA or third-party source material.

This page is evidence of project evolution, not a substitute for being able to
explain, reopen and modify the model.

## 6. Recordkeeping policy for future CFD work

Future scientific extensions should create their history contemporaneously:

1. create a study branch before changing the baseline;
2. commit a short plan with the question, controlled variables, baseline restart
   hash and acceptance criteria;
3. retain Fluent transcripts and monitor/residual histories for materially
   different solver stages;
4. keep checkpoints when models, BCs or discretization settings change instead
   of overwriting the only prior state;
5. hash every solver state selected for long-term retention;
6. keep raw solver evidence identifiable from derived Python analysis;
7. add tests and interpretation after the raw evidence is retained;
8. open a pull request, pass CI, then merge to `main`;
9. preserve later corrections as new commits/PRs instead of rewriting or
   backdating history.

This policy cannot retroactively create a missing pre-public notebook. Its value
is to make every **future** CFD decision easier to audit, reproduce and defend
from the moment it is made.
