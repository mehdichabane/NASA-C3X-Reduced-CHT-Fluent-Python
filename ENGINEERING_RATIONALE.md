# Engineering decision record

This is a **retrospective decision record** for the NASA C3X Run 145 benchmark.
It explains the engineering rationale embodied in the retained Fluent states,
exports, scripts and analysis. It is not presented as a contemporaneous lab
notebook, and it does not invent undocumented intermediate trials.

The purpose is to make the model easier to audit and defend: for each major
choice I state the decision, the alternatives that were relevant, why the
retained choice was used, the evidence available in this repository, the
consequence of the choice, and what evidence would make me change it.

The project remains a reduced benchmark rather than a complete ASME V&V 20
validation. The primary experimental source is Hylton et al.,
[NASA-CR-168015](https://ntrs.nasa.gov/citations/19830020105). ASME's grid-
refinement guidance is used only to delimit what the retained mesh record can
support, and Ansys Fluent documentation is used where model- or mesh-specific
best practice matters.

## 1. Use NASA C3X Run 145 / code 4512 as the benchmark operating point

**Decision.** I retained Run 145 / code 4512 as the single operating point for
this repository.

**Alternatives considered.** A different C3X run, several operating points in
one repository, or a less instrumented turbine-vane case.

**Why this choice.** Run 145 provides a coherent public experimental reference
for the quantities this reduced model can actually compare: surface pressure,
wall temperature and external heat-transfer coefficient, together with the
operating-point quantities and passage-level coolant data needed to define the
reduced thermal boundary conditions. Using one operating point also keeps the
verification, provenance and sensitivity work focused instead of spreading the
same effort across several only partly qualified cases.

**Evidence.** The external inputs and their NASA provenance are recorded in
[`docs/model_setup.md`](docs/model_setup.md) and
[`references/model_inputs/run145_4512_external_boundary_provenance.csv`](references/model_inputs/run145_4512_external_boundary_provenance.csv).
The comparison stations come from NASA-CR-168015 Appendix A and are documented
in [`docs/nasa_comparison.md`](docs/nasa_comparison.md).

**Consequence.** The repository demonstrates depth on one operating point; it
does not demonstrate that the same modeling choices generalize across the full
C3X test matrix.

**What would make me change it.** If the objective became demonstrating
methodology transfer rather than qualifying one benchmark, I would add a second
C3X operating point and require the same provenance, convergence, balance,
mesh-sensitivity and experimental-comparison workflow before treating it as an
independent confirmation.

## 2. Model a two-dimensional midspan section instead of a full 3D vane

**Decision.** The retained model is steady 2D RANS/CHT at the C3X midspan
section.

**Alternatives considered.** A full 3D vane with endwalls and spanwise flow, or
a still simpler external-flow-only model without solid conduction.

**Why this choice.** The project is deliberately a reduced benchmark sized for
the available Fluent Student scope. I kept the gas-solid conjugate problem
because wall temperature and heat transfer are central observables, while
excluding 3D/endwall physics that the retained mesh and setup do not resolve.
The reduction is therefore explicit rather than hidden: the model is intended
to test a controlled midspan RANS/CHT workflow, not to claim complete turbine-
vane fidelity.

**Evidence.** The scope and exclusions are stated in
[`docs/model_setup.md`](docs/model_setup.md). The README likewise labels the
case a reduced benchmark and explicitly excludes 3D/endwall effects.

**Consequence.** Spanwise redistribution, endwall secondary flows and other 3D
mechanisms cannot be predicted. Good agreement at the sampled midspan stations
cannot be extrapolated into a claim of full-vane agreement.

**What would make me change it.** I would move to 3D when the quantity of
interest depends materially on span, endwalls, secondary flow or coolant
redistribution, or when the objective changes from a reduced midspan benchmark
to a higher-fidelity vane prediction. That upgrade would require a new mesh-
convergence strategy and a new validation statement; it would not be a drop-in
extension of the present error metrics.

## 3. Represent the ten internal cooling passages with passage-specific `h` and `Tbulk`

**Decision.** The solid contains the ten C3X cooling passages geometrically, but
coolant flow is not solved. Each passage wall receives a passage-specific
convection condition.

**Alternatives considered.** Resolve the coolant flow in every passage; impose a
single uniform internal convection coefficient; or omit the internal passages
and prescribe a simplified solid boundary elsewhere.

**Why this choice.** NASA-CR-168015 supplies the passage geometry, thermal-entry
correction factors, passage Reynolds numbers and Run 145 coolant bulk
temperatures. Using these values preserves the principal spatial variation of
the internal thermal forcing while keeping the CFD problem tractable. A single
uniform `h` would discard information that is available in the experiment;
fully resolved coolant would change the scale and scope of the project.

The implemented closure is

```text
q'' = h (Tbulk - Twall)
Nu_D = Cr * 0.022 * Pr^0.5 * Re_D^0.8
h = Nu_D * k_air / D
```

**Evidence.** The source chain and generated inputs are documented in
[`docs/model_setup.md`](docs/model_setup.md) and
[`references/model_inputs/run145_4512_internal_convection.csv`](references/model_inputs/run145_4512_internal_convection.csv).
The sensitivity study is under
[`studies/internal_cooling_sensitivity/`](studies/internal_cooling_sensitivity/).

**Consequence.** The model does not predict coolant pressure loss, internal-flow
development or coolant temperature rise. Wall temperature is therefore a
coupled response to external convection, solid conduction and prescribed
internal convection; it is not a pure turbulence-model diagnostic.

**What would make me change it.** If passage development or coolant
redistribution became a quantity of interest, or if the uncertainty associated
with the prescribed convection dominated the validation question, I would
resolve the internal coolant domains and prescribe physically defensible inlet
mass-flow/temperature conditions instead of `h/Tbulk` wall conditions.

## 4. Retain compressibility, the energy equation and conjugate heat transfer

**Decision.** The gas uses ideal-gas density with the energy equation enabled,
and the gas/solid interface is solved conjugately.

**Alternatives considered.** Incompressible external flow; isothermal-wall CFD;
or external aerodynamics without solving solid conduction.

**Why this choice.** The retained fine-grid field reaches a local Mach number of
about `1.04`, and the experimental comparison includes wall temperature and
heat-transfer coefficient. An incompressible/isothermal reduction would remove
physics that are directly connected to the benchmark observables.

**Evidence.** Governing-model choices and material definitions are in
[`docs/model_setup.md`](docs/model_setup.md). The final pressure, wall-
temperature and HTC comparisons are in
[`docs/nasa_comparison.md`](docs/nasa_comparison.md).

**Consequence.** The model can represent the coupling between compressible gas-
side convection and solid conduction, but its thermal prediction still depends
on the retained constant gas-property choices and the reduced internal-cooling
closure.

**What would make me change it.** I would simplify only for a deliberately
separate aerodynamic study in a demonstrably low-Mach regime where thermal
quantities are not outputs of interest. For this Run 145 CHT comparison I would
not remove the energy equation or solid domain.

## 5. Keep SST `k-omega` as the primary turbulence model and Transition SST as a sensitivity model

**Decision.** SST `k-omega` is the primary reported model. Transition SST is
retained as a model-sensitivity branch, not promoted to the baseline.

**Alternatives considered.** Use Transition SST as the primary result simply
because transition can matter on turbine vanes; tune transition inputs to improve
the NASA thermal comparison; or introduce additional turbulence models without
a specific diagnostic question.

**Why this choice.** On the retained fine grid, Transition SST gives pressure
errors similar to SST but substantially larger wall-temperature and HTC errors.
More importantly, the Transition SST response is strongly sensitive to the
inlet turbulent-viscosity ratio through inlet-to-vane turbulence decay. The C3X
Run 145 data used here do not provide an experimentally verified transition
location that would allow me to identify which modeled response is physically
correct. The retained mesh also has a specific Transition-SST limitation: its
realized wall-normal inflation expansion is about `1.20`, above Fluent's
recommended value below `1.1` for transition modeling.

I therefore use the Transition SST result to expose model sensitivity rather
than to claim that SST is universally superior or that a transition model has
been disproved.

**Evidence.** Error metrics are in
[`docs/nasa_comparison.md`](docs/nasa_comparison.md); the inlet-turbulence study
is in
[`studies/transition_sst_sensitivity/README.md`](studies/transition_sst_sensitivity/README.md);
and the realized-mesh audit is in
[`docs/meshing_recipe.md`](docs/meshing_recipe.md). Fluent's turbulence-model
guidance notes that transition models require a low-Re mesh, sufficient
streamwise resolution, wall-normal expansion not exceeding about `1.1`, and an
assessment of inlet-to-leading-edge turbulence decay:
<https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_turb_choosing.html>.

**Consequence.** SST is the defensible primary case for this retained benchmark,
but the repository does not establish that fully turbulent SST is the physically
correct description of every C3X boundary-layer region.

**What would make me change it.** I would reconsider the primary model after a
Transition-SST-qualified mesh study with wall-normal growth below the documented
best-practice limit, at least medium/fine transition solutions, controlled
inlet-to-vane turbulence characterization, and experimental evidence capable of
discriminating transition behavior rather than only global thermal agreement.

## 6. Select the pressure outlet to reproduce the nominal operating point, but do not count outlet Mach as validation

**Decision.** The retained pressure outlet is `236200 Pa`, selected until the
Fluent mass-weighted outlet Mach was numerically consistent with NASA's nominal
Run 145 `M2 = 0.90`.

**Alternatives considered.** Treat the initial `241200 Pa` as fixed; invent or
infer a NASA exit static pressure not tabulated for Run 145; or use the matched
Mach as an additional independent validation metric.

**Why this choice.** NASA defines the run by an exit-Mach operating point and
states that the facility adjusted cascade exit pressure to establish that
condition, but Table IX does not tabulate the corresponding Run 145 exit static
pressure. I therefore used the known `M2` only as an operating-point control
target. A one-step isentropic update from `241200 Pa` and `Mout = 0.88064076`
proposed `236228.236 Pa`, rounded to `236200 Pa`, after which Fluent returned a
mass-weighted outlet Mach close to `0.90`.

NASA `M2` and the Fluent report are not definition-identical: the former is
pressure-derived from measurements, while the latter is a mass-flux-weighted
average of the local computed Mach field. Their proximity establishes operating-
point consistency; it is not a like-for-like validation error.

**Evidence.** The complete history and equation are in
[`docs/outlet_pressure_selection.md`](docs/outlet_pressure_selection.md) and
[`references/model_inputs/run145_outlet_pressure_selection.csv`](references/model_inputs/run145_outlet_pressure_selection.csv).

**Consequence.** Surface pressure, wall temperature and external HTC remain the
independent experimental comparison quantities. Outlet Mach remains useful as a
global operating-point, convergence and sensitivity monitor.

**What would make me change it.** A directly documented Run 145 exit static
pressure with a definition and measurement location compatible with the
computational boundary would replace the tuned pressure outlet. I would also
revisit the boundary location if a domain-sensitivity study showed that the
outlet materially affects the vane solution.

## 7. Resolve the wall to `y+ < 1` rather than use a wall-function-scale first cell

**Decision.** The fine grid uses a `1 micrometre` first layer and 30 inflation
layers; the retained SST external-wall `y+` range is
`0.01044 / 0.30441 / 0.45189` (min / mean / max).

**Alternatives considered.** A coarser near-wall mesh relying on wall functions,
or a substantially finer transition-oriented inflation stack from the start.

**Why this choice.** The primary SST calculation is intended to resolve the
near-wall region directly, and the thermal quantities of interest are strongly
wall-dependent. The realized `y+` values provide an a posteriori check that the
chosen first-cell height achieved that objective.

**Evidence.** Mesh dimensions, realized quality and `y+` are in
[`docs/meshing_recipe.md`](docs/meshing_recipe.md) and
[`docs/convergence_acceptance.md`](docs/convergence_acceptance.md).

**Consequence.** Near-wall SST resolution is strong, but a low `y+` value alone
does not make the whole mesh adequate. The trailing-edge profiles remain more
mesh-sensitive, and the `~1.20` inflation expansion is a known limitation for
Transition SST even though the transition-case maximum `y+` remains below 1.

**What would make me change it.** If Transition SST became a primary model, I
would rebuild the inflation stack around its stricter wall-normal expansion
requirement (below about `1.1`) while preserving `y+` near or below 1 and then
repeat mesh sensitivity. If a future wall-function RANS study were posed as a
separate question, it would require a deliberately different near-wall mesh and
would not be mixed with the present baseline.

## 8. Accept convergence using residuals, stable engineering quantities and conservation together

**Decision.** A fine-grid final state is accepted only after 20 iterations with
unchanged final discretization, continuity below `1e-3`, each selected
engineering-monitor relative span below `0.02%`, and the mass/interface/solid-
energy balances inside their project limits.

**Alternatives considered.** Stop as soon as Fluent's residual criterion is met;
use a fixed iteration count; or judge convergence only from visually flat
monitor curves.

**Why this choice.** Residual reduction is necessary but not sufficient for the
engineering quantities used in the benchmark. Fluent itself recommends judging
convergence using residual behavior together with representative solution
quantities and overall mass/energy conservation rather than relying on one
universal residual threshold. The project rule is therefore deliberately
multi-part and is labeled project-specific rather than universal.

**Evidence.** The rule, final-window values and balances are in
[`docs/convergence_acceptance.md`](docs/convergence_acceptance.md). Fluent's
convergence guidance is documented at
<https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_sec_solve_monitor.html>
and its successful-simulation guidance explicitly recommends residual,
engineering-variable and conservation checks:
<https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_gs_success_sim.html>.

**Consequence.** The accepted states are numerically stationary under the chosen
criteria and conserve the reported global quantities very tightly. This does
not prove physical correctness: a converged solution can still reflect an
inadequate model, mesh, material property or boundary condition.

**What would make me change it.** I would change the acceptance rule for an
unsteady problem, for a quantity of interest with slower convergence than the
current monitors, or if a sensitivity study showed that the current thresholds
permit a materially changing NASA comparison metric. The criterion should
follow the quantity of interest, not be preserved as a ritual number.

## 9. Report a three-grid sensitivity study, not a formal asymptotic GCI

**Decision.** Coarse, medium and fine SST results are used as a mesh-sensitivity
assessment. Richardson/GCI fields generated by the post-processing remain
screening diagnostics and are not reported as accepted discretization
uncertainties.

**Alternatives considered.** Call the three meshes a formal GCI study because
three solutions exist; report only the fine grid; or ignore the local profile
behavior because the global quantities change by less than `0.1%` from medium
to fine.

**Why this choice.** ASME's solution-verification guidance for grid refinement
requires the same problem to be solved on geometrically similar successively
refined grids. The retained Fluent meshes are real and auditable, but the
original Workbench/Ansys Meshing generation recipe, sizing controls and bias
history were not preserved well enough to establish a systematically similar
refinement family. In addition, the last `5%` near the trailing edge shows
larger local medium-to-fine differences than the global quantities.

**Evidence.** The three meshes, global and local sensitivity metrics, exploratory
Richardson/GCI diagnostics and missing generation history are documented in
[`docs/meshing_recipe.md`](docs/meshing_recipe.md). ASME's grid-refinement
workshop states the geometrically-similar-grid requirement explicitly:
<https://www.asme.org/codes-standards/publications-information/verification-validation-uncertainty/workshop-on-estimation-of-discretization-errors-based-on-grid-refinement-studies-2017/introduction>.

**Consequence.** I can defend that the retained global outputs are relatively
insensitive from medium to fine and quantify where local profiles remain more
sensitive. I cannot defend a formal discretization-uncertainty band from this
mesh record.

**What would make me change it.** I would regenerate coarse/medium/fine meshes
from one preserved parameterized procedure with controlled refinement ratios,
solve the same model on all three, verify monotonic/asymptotic behavior for the
quantities of interest, and only then promote Richardson/GCI calculations from
screening to an accepted solution-verification result.

## 10. Interpret NASA's `+/-3%` internal-HTC value as a sensitivity envelope, not a probability distribution

**Decision.** The NASA-reported estimated `+/-3%` uncertainty in the internal
cooling-hole HTC calculation is mapped onto the existing common-mode `h`
sensitivity family as an envelope. It is not labeled a 95% interval, standard
uncertainty or formal CFD input distribution.

**Alternatives considered.** Ignore the NASA value; treat `+/-3%` as a
probabilistic confidence interval without a stated coverage model; or add it
again to NASA's external-HTC Table VI uncertainty bars.

**Why this choice.** The existing `h/h0 = 0.90 ... 1.10` screening is close to
linear around the baseline, so the reported magnitude can be interpolated
without another Fluent solve. NASA does not provide the probability model or
coverage level needed to turn that magnitude into a formal stochastic input
uncertainty. The same internal-HTC term also participates in NASA's thermal
reduction, so adding it independently to the reported external-HTC uncertainty
would risk double counting.

**Evidence.** The mapping and numerical result are in
[`studies/internal_cooling_sensitivity/NASA_UNCERTAINTY.md`](studies/internal_cooling_sensitivity/NASA_UNCERTAINTY.md)
and
[`studies/internal_cooling_sensitivity/nasa_uncertainty_mapping.csv`](studies/internal_cooling_sensitivity/nasa_uncertainty_mapping.csv).
The broader experimental uncertainty record is summarized in
[`docs/nasa_comparison.md`](docs/nasa_comparison.md).

**Consequence.** The repo can state that a coherent common-mode `h +/-3%`
perturbation gives approximately `+/-1.735 K` on mean external wall temperature
and does not remove the positive SST wall-temperature bias. It cannot claim a
complete validation-uncertainty probability or confidence interval from that
calculation.

**What would make me change it.** I would move to formal input-uncertainty
propagation only if defensible distributions/coverage levels and correlations
were available for the relevant inputs, together with matching solved
sensitivities or an uncertainty-propagation design capable of treating them
consistently.

## 11. Make the post-processing reproducible without pretending the complete Fluent solve is replayable

**Decision.** The committed Python workflow deterministically rebuilds processed
tables, checks and figures from retained Fluent exports. Released case/data
states and headless PyFluent audits provide saved-state traceability. The repo
does not claim initialization-to-final solver replay.

**Alternatives considered.** Claim full reproducibility because the Python CI is
deterministic; omit the Fluent states and expose only plots; or require a
licensed Fluent solve inside public CI.

**Why this choice.** The analysis layer can be rebuilt in an ordinary CI runner,
while a full Fluent replay has licensing/runtime constraints and the original
complete initialization/run history was not retained. Preserving the actual
solver states, hashes and scalar re-audits is therefore useful evidence, but it
must be described as saved-state reproducibility rather than solver-history
reconstruction.

**Evidence.** The exact boundary is documented in
[`docs/reproducibility.md`](docs/reproducibility.md), the restart hashes in
[`fluent/restart_manifest.csv`](fluent/restart_manifest.csv), and the current CI
in [`.github/workflows/checks.yml`](.github/workflows/checks.yml).

**Consequence.** A reviewer can independently rebuild the analysis from the
committed exports and audit the released final states, but cannot use this repo
to prove that a fresh initialization will reproduce iteration 236 bit-for-bit.

**What would make me change it.** If a future licensed environment permits it, I
would define and archive a new initialization-to-final PyFluent/journal replay
for at least the primary fine SST case, with convergence gates and automatic
comparison of final integral quantities. I would describe that as a new
reproducible protocol, not retroactively claim it reconstructs undocumented
historical steps.

## 12. Treat 3D/resolved coolant as a new scientific model, not as a cosmetic upgrade

**Decision.** I stop the present repository at the reduced 2D/prescribed-coolant
scope unless a new scientific question requires higher fidelity.

**Alternatives considered.** Add 3D geometry, resolved coolant, more turbulence
models or more cells simply to make the portfolio look more complex.

**Why this choice.** Additional fidelity is useful only when it resolves a
known limitation connected to a quantity of interest. A full 3D/resolved-
coolant model would change the physics, boundary-condition definitions,
computational cost, mesh-verification problem and interpretation of agreement
with the midspan experiment. It should therefore be treated as a new model with
its own verification and validation plan rather than as a visually impressive
revision of the current benchmark.

**Evidence.** The present model boundaries are explicit in
[`docs/model_setup.md`](docs/model_setup.md), while the strongest retained
limitations are the non-reconstructed coolant flow, 2D/endwall omission,
non-formal mesh GCI and Transition-SST mesh qualification documented elsewhere
in this record.

**Consequence.** The repository remains narrow enough that every retained claim
can be traced to evidence. Its limitation is equally clear: it cannot answer
questions controlled by spanwise/endwall flow, passage coolant development or
other excluded 3D physics.

**What would make me change it.** I would open a separate higher-fidelity study
when at least one of the following is true:

1. the target quantity is demonstrably controlled by a currently excluded 3D or
   coolant-flow mechanism;
2. a second experimental operating point requires those mechanisms for a fair
   comparison;
3. the purpose becomes industrial/research prediction rather than a reduced
   benchmark; or
4. the available compute/licensing budget supports a systematic 3D mesh study
   rather than a single expensive demonstration mesh.

A credible 3D/resolved-coolant extension would need, at minimum, documented
geometry and coolant boundary conditions, a reproducible mesh-generation
strategy, near-wall qualification on both gas and coolant sides, conservation
checks, solution-convergence criteria, a mesh-sensitivity/verification plan and
a redefined experimental-comparison statement.

## Summary

The recurring rule behind these decisions is **do not claim more than the
retained evidence supports**. I prefer a reduced model with explicit boundaries,
quantified sensitivities and traceable decisions to a more complicated model
whose numerical and experimental credibility I cannot defend.
