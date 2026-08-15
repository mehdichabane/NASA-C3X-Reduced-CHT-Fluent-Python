# Project development notes

The CFD model was already substantially complete when this repository was first
made public. The public Git history therefore starts later than the actual CFD
work. I can recover the retained solver states and a few engineering sequences,
but not reliable calendar dates for the pre-public simulations.

## Retained Fluent states

The restart release keeps four Fluent 26.1 states:

| Model / grid | Cells | Final iteration |
|---|---:|---:|
| coarse SST | `14,657` | `156` |
| medium SST | `23,781` | `161` |
| fine SST | `44,760` | `236` |
| fine Transition SST | `44,760` | `556` |

The case/data hashes are in
[`../fluent/restart_manifest.csv`](../fluent/restart_manifest.csv). The fine SST
state at iteration 236 is the baseline used for the reported comparison. Its
final 20 iterations are the unchanged second-order confirmation window described
in [`convergence_acceptance.md`](convergence_acceptance.md).

The exact dates of these pre-public solves are not recoverable from the retained
repository, so I do not assign dates or a coarse-to-medium-to-fine execution
order that I cannot support.

## Outlet-pressure adjustment

One pre-public engineering adjustment is preserved well enough to reconstruct.
My provisional pressure outlet was `241200 Pa`, which gave a Fluent
mass-weighted outlet Mach of `0.88064076`. A local isentropic estimate suggested
`236228.236 Pa`; I rounded that to `236200 Pa` and obtained a value close to the
Run 145 target:

| Stage | Outlet pressure | Fluent outlet Mach |
|---|---:|---:|
| provisional state | `241200 Pa` | `0.88064076` |
| isentropic estimate | `236228.236 Pa` | — |
| applied setting | `236200 Pa` | `0.89951531` |
| retained fine SST state | `236200 Pa` | `0.90129444` |

I use this only as an operating-point adjustment, not as an independent
validation result. The full calculation is in
[`outlet_pressure_selection.md`](outlet_pressure_selection.md).

## From SST to Transition SST

The Transition SST transcript preserves a clearer solver chronology. I started
from the accepted fine SST state at iteration `236`, enabled Transition SST, and
used first-order convection for `k`, `omega`, intermittency and `Re_theta_t`
while the added equations settled.

A checkpoint was saved at iteration `386`. Those four equations were then
changed to Second Order Upwind, and the run continued to iteration `556`.
Iteration `536` was kept as a converged candidate and `537-556` formed the final
unchanged confirmation window.

The restart bundle also contains the Transition SST transcript, monitor history
and direct wall export. See [`../fluent/README.md`](../fluent/README.md) and
[`../data/fluent_exports/transition_sst/PROVENANCE.md`](../data/fluent_exports/transition_sst/PROVENANCE.md).

## First public snapshot

The first public commit is
[`12a311d`](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/commit/12a311db3d0cf794a0fb0e150a850e2070bfa8ff),
**“Publish NASA C3X Run 145 benchmark,”** on **7 August 2026**.

That snapshot already contained the reduced RANS/CHT benchmark, the three SST
grids, the fine Transition SST result, NASA comparisons, convergence and
conservation checks, Fluent exports, Python analysis and tests. The
[`initial-public-release`](https://github.com/mehdichabane/NASA-C3X-Reduced-CHT-Fluent-Python/releases/tag/initial-public-release)
followed the same day with the retained restart states and checksums.

## Main additions after publication

The later Git history mainly records qualification and follow-up work around the
existing CFD model:

- **10 Aug:** added the five-point internal-cooling `h` and `Tbulk` sensitivity
  families and the `h × Tbulk` interaction study.
- **12-13 Aug:** tightened mesh/Transition SST claims, improved input and material
  provenance, pinned CI, and recovered the outlet-pressure selection record.
- **14 Aug:** recovered the exact Transition SST scheme sequence, separated NASA
  and Fluent outlet-Mach definitions, and added headless PyFluent saved-state
  audits.
- **15 Aug:** mapped NASA's reported `±3%` internal-HTC magnitude onto the
  existing cooling sensitivity family, then simplified the portfolio
  documentation.

The saved-state audits reopen the released fine SST and Transition SST files and
recompute the stored heat-rate, wall-temperature and outlet-Mach reports. They
confirm that the released final states can still be opened and queried in
Fluent 26.1; they are not full initialization-to-final reruns. Details are in
[`reproducibility.md`](reproducibility.md).

For future CFD extensions I intend to keep the development record as the work is
done: branch before changing the baseline, retain solver transcripts and useful
checkpoints, keep raw exports separate from derived analysis, and merge through
CI rather than trying to reconstruct the history afterwards.
