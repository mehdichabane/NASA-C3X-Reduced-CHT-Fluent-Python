# Retrospective development history

This page records the development history that can be supported by retained
solver artifacts and the public GitHub record. It is **retrospective**: the CFD
work was already substantially developed when the repository was first
published, so this page does not pretend that Git contains the original local
week-by-week engineering history.

The distinction matters. A Git commit can establish what content was published
at a given commit and who authored that Git change, while a Fluent case/data
pair, transcript, monitor history or exported field can establish facts about a
solver state. Neither source should be made to say more than it preserves.

GitHub's documentation describes commits as records of specific changes, with a
unique SHA, author and time, and pull requests as the place where a branch's
commits, checks and file changes are reviewed before merge:

- <https://docs.github.com/en/pull-requests/reference/commits>
- <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/getting-started/about-pull-requests>
- <https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/using-the-activity-view-to-see-changes-to-a-repository>

## Evidence classes used here

| Evidence class | What it can establish | What it cannot establish by itself |
|---|---|---|
| Fluent case/data pair | retained solver state, mesh, settings and fields stored in that state | original creation date, every earlier trial, or authorship of the engineering decisions |
| Fluent transcript / monitor / export | solver chronology or quantities explicitly recorded in that artifact | undocumented steps outside the retained record |
| SHA-256 manifest | identity of the released binary artifact | when the underlying CFD work originally began |
| Git commit | repository content at that commit, Git author/time and change history | the date on which pre-existing local CFD files were first created |
| Pull request / CI run | public branch-to-main development, reviewable diff and automated checks | proof that every line was written without tools or assistance |
| GitHub release | public availability of named release assets at the recorded publication time | an earlier private development timeline |

No file-system timestamp from the current Git tree is used as evidence of the
original local CFD chronology. The repository API does not preserve the
original workstation modification times needed to make that inference safely.
No commit has been backdated to reconstruct missing history.

---

## 1. Solver history retained independently of Git dates

The accepted Fluent restart set is content-addressed in
[`fluent/restart_manifest.csv`](../fluent/restart_manifest.csv). The retained
states are:

| Model / grid | Cells | Final iteration | Retained evidence |
|---|---:|---:|---|
| coarse SST | `14,657` | `156` | case/data pair + SHA-256 |
| medium SST | `23,781` | `161` | case/data pair + SHA-256 |
| fine SST | `44,760` | `236` | case/data pair + SHA-256 |
| fine Transition SST | `44,760` | `556` | case/data pair + SHA-256 + transcript/monitors/direct wall export |

These four accepted states establish that the published benchmark is based on
real retained Fluent solutions, not only on plotted or manually transcribed
summary values. The manifest does **not** establish the calendar date on which
each solve was first completed, and it does not establish a chronological
coarse -> medium -> fine execution order. The three SST states are therefore
presented as a retained solution set rather than as a dated run sequence.

### Fine SST retained state

The accepted fine SST state is iteration `236`. The committed convergence and
solver exports preserve:

- the full and final-window residual histories;
- engineering-monitor histories;
- mass, gas-solid interface and solid-energy balance checks;
- wall `y+` and realized-mesh audits;
- direct Fluent contour sources and wall data used in the NASA comparison.

The active continuity criterion was first met at iteration `216`; iterations
`217-236` form the final unchanged second-order confirmation window documented
in [`convergence_acceptance.md`](convergence_acceptance.md).

### Retained outlet-pressure adjustment sequence

A separate project-development record preserves an actual engineering adjustment
made before the released fine baseline. The ordering below is supported by the
record itself; no calendar dates are assigned to these stages:

| Stage | Outlet pressure | Fluent mass-weighted outlet Mach |
|---|---:|---:|
| provisional second-order state | `241200 Pa` | `0.88064076` |
| local isentropic control estimate | `236228.236 Pa` | not a solved state |
| applied rounded setting | `236200 Pa` | `0.89951531` |
| released fine SST baseline | `236200 Pa` | `0.90129444` |

The complete reasoning is in
[`outlet_pressure_selection.md`](outlet_pressure_selection.md). The sequence is
useful development evidence because it records a provisional condition, the
control calculation used to change it, and the subsequent Fluent response. It
also records the later methodological correction that NASA `M2` and Fluent's
mass-weighted outlet Mach are not definition-identical observables.

### Transition SST chronology preserved by the Fluent record

The Transition SST sequence is much more detailed because the restart bundle
retains a Fluent transcript and monitor history. It starts from the accepted
fine SST state at iteration `236`:

1. Transition SST (four equations) is enabled from the iteration-236 SST state.
2. A Transition SST warm-start case/data pair is written before the deliberate
   stabilization change.
3. `k`, `omega`, intermittency and transition momentum-thickness Reynolds number
   are set to Fluent scheme index `0` (First Order Upwind).
4. Those four transport equations remain first order through iteration `386`.
5. A first-order iteration-386 checkpoint is written.
6. The four Transition SST transport equations are changed to scheme index `1`
   (Second Order Upwind).
7. The iteration-386 state is written again before further iteration.
8. The calculation continues with those second-order settings to iteration
   `556`.
9. Iteration `536` is retained as a converged candidate; iterations `537-556`
   form the final unchanged confirmation window.

Pressure interpolation and the density, momentum and energy convection schemes
remain at their existing second-order settings through that Transition SST
sequence. The restart-bundle evidence and limitations are described in
[`../fluent/README.md`](../fluent/README.md).

The direct iteration-556 wall export provides a second traceability path. It has
one row for each of the `819` external vane wall faces, and independently
reproduces the saved wall heat-rate report, area-weighted mean wall temperature
and wall-`y+` statistics. See
[`../data/fluent_exports/transition_sst/PROVENANCE.md`](../data/fluent_exports/transition_sst/PROVENANCE.md).

---

## 2. First public repository snapshot — 7 August 2026

The public Git history begins with commit
[`12a311d`](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/commit/12a311db3d0cf794a0fb0e150a850e2070bfa8ff),
**“Publish NASA C3X Run 145 benchmark,”** recorded by GitHub at
`2026-08-07 11:02:56 UTC`.

That first public commit was already a mature benchmark rather than an empty
repository scaffold. It already contained, among other material:

- the reduced 2D RANS/CHT model description;
- accepted coarse, medium and fine SST results;
- the fine Transition SST result;
- NASA pressure, wall-temperature and HTC comparisons;
- convergence, balance, mesh-sensitivity and wall-resolution evidence;
- Fluent exports and post-processing scripts;
- tests and a GitHub Actions analysis workflow;
- explicit limitations on mesh-history and solver reproducibility.

This establishes a clear boundary for interpretation: those artifacts existed
in the public project **no later than the first Git publication**. The commit
cannot establish when each underlying local Fluent solve was originally created
or how long the pre-public engineering work took.

### Initial restart release

The GitHub release
[`initial-public-release`](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/releases/tag/initial-public-release)
was published on `2026-08-07 11:12:42 UTC`, shortly after the first commit. It
made the Fluent restart archive publicly available together with checksums. The
archive contains the accepted coarse, medium and fine SST states and the fine
Transition SST state, plus the Transition SST transcript, monitor history and
direct wall export.

This is the strongest public timestamp for the original solver-artifact set: it
shows that the binary restart evidence accompanied the initial public project
rather than being reconstructed only after the later documentation work.

---

## 3. Public development after the initial snapshot

From this point onward the development chronology is Git-backed. The entries
below summarize the major merged pull requests rather than treating every
formatting commit as a separate engineering milestone.

### 10 August 2026 — internal-cooling sensitivity becomes a full study

[PR #1 — Add internal cooling sensitivity and interaction study](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/1)
merged the completed five-point prescribed-HTC and coolant-temperature
screening families together with local sensitivities, linearity diagnostics,
NASA comparison metrics, closure checks and the local `h x Tbulk` interaction
screening.

This is an important change in project character: the repository moved from a
single qualified baseline plus turbulence-model comparison toward explicit
boundary-condition sensitivity analysis.

### 12 August 2026 — scope and provenance are tightened

The next public pass deliberately narrowed claims rather than adding new CFD
results:

- [PR #2](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/2): exposed local trailing-edge mesh sensitivity and narrowed the Transition SST mesh/transition-location claims;
- [PR #3](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/3): corrected provenance and repository-hygiene wording without altering CFD outputs;
- [PR #4](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/4): further separated archived baseline facts from source attributions that could not be reconstructed confidently.

These changes are retained in the history because corrections and narrowed
claims are part of the engineering record, not defects to erase from it.

### 13 August 2026 — source selection and methodological boundaries become machine-readable

PRs #5-#13 added or strengthened the traceability layer around the already
retained calculations:

- [#5](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/5) classified external Run 145 quantities as direct NASA data, rounded implementation values, model inputs, archived solver BCs or computed outputs;
- [#6](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/6) recovered independently checkable thermophysical literature matches without pretending to reconstruct the original source-selection trail;
- [#7](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/7) transcribed the NASA experimental uncertainty record and separated it from the external-HTC Table VI intervals;
- [#8](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/8) separated experimental inlet turbulence intensity from Fluent Transition SST model inputs;
- [#9](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/9) and [#11](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/11) tightened CI reproducibility by pinning the hosted runner and GitHub Actions;
- [#10](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/10) aligned material-property provenance wording with the machine-readable records;
- [#12](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/12) improved the README opening without changing science;
- [#13](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/13) recovered and documented the `241200 -> 236200 Pa` outlet-pressure development sequence and explicitly removed outlet-Mach agreement from the set of independent validation metrics.

### 14 August 2026 — retained solver states are audited more deeply

The next group used retained Fluent evidence to correct or strengthen facts that
could be checked directly instead of relying on recollection:

- [PR #14](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/14) recovered the exact Transition SST discretization chronology and audited the realized CFF mesh, including the approximately `1.20` inflation growth limitation;
- [PR #15](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/15) clarified the non-identical NASA and Fluent exit-Mach definitions;
- [PR #16](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/16) prepared a headless, hash-traceable PyFluent saved-state audit;
- [PR #17](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/17) archived live Fluent 26.1 executions of that audit for both released fine states;
- [PR #18](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/18) documented the immutable action pins;
- [PR #19](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/19) streamlined the portfolio README and aligned the Transition SST scheme wording with the retained record.

The live audits recompute from the released saved states:

| Saved state | External heat rate | Mean wall temperature | Mass-weighted outlet Mach |
|---|---:|---:|---:|
| fine SST, iter 236 | `35819.60242176461 W` | `655.619216610248 K` | `0.9012944409738727` |
| fine Transition SST, iter 556 | `28548.27415186197 W` | `608.87899709921 K` | `0.9033510682539843` |

The case/data hashes recorded by those audits match the release manifest. This
shows that the released fine states can be reopened through the documented
Fluent 26.1/PyFluent path and that their stored report definitions reproduce the
archived scalar values. It is still a saved-state audit, not an initialization-
to-final solver replay.

A second GitHub release,
[`portfolio-snapshot-2026-08-14`](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/releases/tag/portfolio-snapshot-2026-08-14),
then captured this verification/provenance/sensitivity state of the portfolio.

### 15 August 2026 — uncertainty interpretation and engineering rationale

Three later pull requests make the already-completed CFD work easier to
interpret and defend:

- [PR #20](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/20) maps NASA's reported `+/-3%` internal cooling-hole HTC calculation magnitude onto the existing central `h` sensitivity as a common-mode envelope, explicitly not a probability interval;
- [PR #21](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/21) refocuses the README around results, scope and reproducibility without changing the CFD;
- [PR #22](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/pull/22) adds the retrospective [`ENGINEERING_DECISIONS.md`](../ENGINEERING_DECISIONS.md), recording the rationale, alternatives, consequences and change triggers for twelve major modeling and verification choices.

---

## 4. Evidence chain available to a reviewer

The project can now be followed through several independent layers rather than
through a single polished README:

```text
NASA source data and geometry
        |
        v
model-input provenance + generated internal-convection inputs
        |
        v
retained Fluent solver states / exports / monitors / transcript
        |
        +--> SHA-256 restart manifest
        |
        v
deterministic Python processing, comparisons and numerical checks
        |
        v
first public commit + restart release (7 Aug 2026)
        |
        v
subsequent PRs with CI-checked corrections, sensitivities and provenance work
        |
        v
live Fluent 26.1 saved-state audits + later portfolio snapshot
```

This chain is useful because the different layers answer different questions:
source provenance supports where inputs came from; solver artifacts support what
Fluent state was retained; scripts support how metrics were derived; Git supports
how the public repository evolved; CI supports regression consistency.

---

## 5. What this history supports

The retained evidence supports the following statements:

- a mature C3X benchmark, including the three SST grids and fine Transition SST
  result, was present in the first public repository commit on 7 August 2026;
- the corresponding accepted Fluent restart states were released publicly with
  cryptographic hashes on the same day;
- the fine Transition SST solver chronology is preserved more deeply than a
  final filename alone because a transcript, monitors and direct wall export are
  retained;
- at least one pre-release engineering adjustment sequence is independently
  recorded for the pressure outlet;
- after publication, extensions and corrections were made through visible
  branches/pull requests and repeatedly checked by the repository CI;
- later documentation corrections generally narrow or qualify claims rather
  than silently rewriting the archived solver results;
- the released fine-grid states can be reopened in Fluent 26.1 and their stored
  scalar reports recomputed through the archived PyFluent audit path.

These are evidence statements about the project record. They are not presented
as proof of unaided authorship or as a substitute for being able to defend and
modify the model in an interview.

---

## 6. What this history does **not** support

The repository deliberately does **not** claim to know what the retained
artifacts cannot prove:

- the exact calendar start date or duration of the private pre-public CFD work;
- the exact original workstation creation/modification time of each Fluent file;
- a complete chronological ordering of the coarse, medium and fine SST solves;
- every rejected geometry, mesh, boundary condition or solver trial that may
  have existed before publication;
- the original SpaceClaim and Ansys Meshing GUI operation history;
- a bit-for-bit regeneration of the original meshes from an editable Workbench
  recipe;
- an initialization-to-iteration-236 replay establishing equivalence with the
  released fine SST state;
- solver-run equivalence for every internal-cooling or Transition SST sensitivity
  case from the Python CI workflow;
- authorship of NASA measurements, NASA geometry or third-party source material.

The detailed reproducibility boundary remains in
[`reproducibility.md`](reproducibility.md).

---

## 7. Recordkeeping policy for future CFD extensions

Future scientific work should make its development history contemporaneous
instead of relying on retrospective reconstruction. For a new operating point,
mesh family or model-sensitivity campaign, the intended workflow is:

1. create a dedicated branch before changing the baseline;
2. commit a short study plan that states the question, controlled variables,
   baseline restart hash and acceptance criteria;
3. retain Fluent transcripts and monitor/residual histories for materially
   different solver stages;
4. keep checkpoints when a model, boundary condition or discretization setting
   is deliberately changed rather than overwriting the only prior state;
5. hash every solver state selected for long-term retention;
6. commit raw solver evidence separately from derived Python analysis where
   practical;
7. add the analysis, tests and interpretation only after the raw evidence is
   identifiable;
8. open a pull request, allow the full CI workflow to run, then merge to `main`;
9. preserve corrections as new commits/PRs instead of rewriting or backdating
   history.

That policy cannot retroactively create a missing pre-public notebook, and it is
not intended to. Its purpose is to make every **future** CFD decision easier to
audIT, reproduce and defend from the moment it is made.
