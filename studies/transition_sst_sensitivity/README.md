# Transition SST inlet-turbulence sensitivity

This study investigates why the fine-grid Transition SST solution preserves the Run 145 pressure comparison while producing a substantially different thermal field from the SST baseline. It is a model-behavior and sensitivity study, not a calibration exercise and not an uncertainty quantification.

Phase A diagnoses the accepted Transition SST solution at iteration 556. Phase B perturbs the inlet turbulence state in controlled one-factor cases while keeping the mesh, thermal boundary conditions, numerics and Transition SST model settings unchanged.

## Baseline case

The archived baseline is the accepted fine-grid Transition SST solution documented in `references/model_inputs/transition_sst_settings.csv` and `data/fluent_exports/transition_sst/`.

Key inlet settings are:

- turbulence intensity: `6.5%`;
- turbulent viscosity ratio: `10`;
- inlet intermittency: `1.0`;
- inlet transition momentum-thickness Reynolds number: obtained by Fluent from its turbulence-intensity correlation;
- Transition SST roughness correlation: off;
- curvature correction: off;
- production limiter: on;
- Kato-Launder production limiter: on;
- custom transition correlations: none.

The diagnostic was rebuilt directly from the final CFF case/data pair:

- case SHA-256: `1d798a84b90a06c55471b229b41ca2da08eece4925f8560280f6ad808bc50a30`;
- data SHA-256: `9f1664a5dd11f615b4582cf62be1cf5b520d822d066adbcd4a74b95c91324c52`.

The mesh contains 44,760 cells, 90,768 faces and 45,999 nodes. The computational inlet is about `58.605 mm` upstream of the geometric leading edge.

## Phase A: freestream-decay diagnostic

The saved inlet face fields reproduce the prescribed turbulence state exactly:

- `Tu = 6.500000%` on all 76 inlet faces;
- `gamma = 1.000000`;
- `Re_theta_t = 100.359274`.

Local turbulence intensity is reconstructed from the saved fields as

`Tu = 100 sqrt(2 k / 3) / |U|`.

For the upstream freestream diagnostic, only fluid cells upstream of the geometric leading edge and farther than `8 mm` from a wall are retained. Values are summarized in axial bins using the median, with the 10th and 90th percentiles also retained for `Tu`.

In the `2-5 mm` freestream bin immediately upstream of the leading edge, the baseline contains:

- median `Tu = 1.2473%`;
- median `mu_t/mu = 7.851`;
- median `Re_theta_t = 412.933`.

The imposed inlet value therefore does not remain unchanged to the vane. Detailed values are in `baseline_freestream_decay.csv`; the case audit is in `baseline_case_audit.csv`.

## Phase A: wall transition signature

The `wall_vane-shadow` loop is traversed geometrically from the leading edge to the trailing edge on each side. Saved wall-adjacent intermittency, wall temperature and wall shear are then inspected along the paths.

For the baseline, the largest concurrent suction-side gradients in intermittency and wall temperature occur around `x/Cx = 0.6534`; the largest wall-shear gradient is nearby at `x/Cx = 0.6551`. The pressure side shows no comparable mid-side intermittency rise.

This is described as a **transition-like response front**, not as an experimentally established transition onset. Selected threshold and gradient locations are recorded in `baseline_transition_signature.csv`.

## Phase B1: viscosity-ratio sensitivity at fixed inlet intensity

All B1 cases retain `Tu_in = 6.5%` and change only the inlet turbulent viscosity ratio. Each case restarts independently from the accepted Transition SST state at iteration 556.

### `tu065_vr05`

Changing `mu_t/mu_in` from `10` to `5` gives:

- near-leading-edge median `Tu`: `1.2473 -> 0.8701%`;
- near-leading-edge median `mu_t/mu`: `7.851 -> 3.698`;
- near-leading-edge median `Re_theta_t`: `412.933 -> 655.346`;
- mean external wall temperature: `608.879 -> 604.438 K`;
- external heat-transfer rate: `28.5483 -> 27.7758 kW/m`;
- outlet Mach number: `0.903351 -> 0.903562`.

The suction-side transition-like response moves downstream from about `0.65` to `0.69 x/Cx`. The final mesh is byte-for-byte identical to the baseline mesh and the recorded mass, interface, solid-energy and `y+` checks pass the study limits.

### `tu065_vr01`

Changing `mu_t/mu_in` from `10` to `1` produces a much stronger response. The case converges at iteration `1046`.

Final CFF hashes:

- case SHA-256: `8d703624e063247955182ada4e7021311bf25e81a5f5e33952eebe572d47e268`;
- data SHA-256: `a0ece8767b071d8e34c8bb34a0349112835779c8abc0db3122a55b963478b4da`.

The mesh and all non-target boundary-condition settings remain unchanged. The final inlet still contains `Tu = 6.500000%`, `gamma = 1.000000` and `Re_theta_t = 100.359274`.

The final `2-5 mm` pre-leading-edge diagnostic is:

- median `Tu = 0.36371%`;
- median `mu_t/mu = 0.63855`;
- median `Re_theta_t = 1062.83`;
- median `k = 0.24909 m2/s2`.

Relative to the `vr10` baseline:

- mean external wall temperature: `608.879 -> 574.705 K` (`-5.613%`);
- external heat-transfer rate: `28.5483 -> 22.9198 kW/m` (`-19.716%`);
- outlet Mach number: `0.903351 -> 0.905424` (`+0.229%`).

The final 20-iteration maximum relative changes saved in the Fluent convergence-condition history are `0.00268%` for external heat rate, `0.000394%` for mean wall temperature and `0.000070%` for outlet Mach, all below the study criterion of `0.02%`. Final continuity is `2.02e-5`, and maximum saved wall `y+` is `0.3936`.

The suction-side response has moved into the trailing-edge region. The first `gamma >= 0.025` location is `x/Cx = 0.9616`; the interior intermittency-gradient and wall-shear-gradient maxima are near `0.9667` and `0.9680`, respectively. The wall-temperature-gradient maximum is no longer co-located with these two signatures. For this case, gradient searches are restricted to `x/Cx < 0.98` to prevent the geometric trailing edge itself from dominating the metric. The resulting locations remain model-response diagnostics, not experimental transition-onset measurements.

The final CFF pair preserves the mass-flow, coupled-interface, `y+`, residual and report-convergence quantities recorded in `tu065_vr01_global_checks.csv`. The separate cooling-hole total heat-rate Flux Report used for the earlier solid-energy balance was not persisted as a report definition in this final CFF pair. No final coolant-total or solid-heat-imbalance value is reconstructed or invented from the saved files; subsequent cases must record that Flux Report explicitly at closure.

Detailed B1 results are in the `tu065_vr05_*`, `tu065_vr01_*`, `vr10_vs_vr05_diagnostic_summary.csv`, `vr10_vs_vr01_diagnostic_summary.csv` and `b1_three_point_summary.csv` files.

## Experimental inlet-turbulence reference

NASA-CR-168015 defines `Tu` in the C3X test-condition table as the **average inlet turbulence intensity**. The report states that the combustor-induced cascade inlet level was `6.5%`, measured with the LDA, and that installing circular rods upstream increased the inlet level to `8.3%`. The facility description places the LDA optical access at the cascade inlet plane.

This resolves the earlier ambiguity sufficiently for the sensitivity design: `6.5%` is an experimental inlet-level quantity, not a documented `6.5%` leading-edge target. The exact geometric correspondence between the experimental inlet measurement plane and this reduced computational inlet is not assumed.

## B1 conclusion and B2 decision

B1 establishes a strong, nonlinear viscosity-ratio sensitivity at fixed `Tu_in = 6.5%`:

`mu_t/mu_in: 10 -> 5 -> 1`

maps to approximately

`Tu_2-5mm: 1.247% -> 0.870% -> 0.364%`.

The accompanying thermal/transition response changes strongly while outlet Mach changes comparatively little. This supports the inlet-to-vane turbulence-decay mechanism as a major model sensitivity. It does not identify an optimal viscosity ratio and is not used to tune the calculation to NASA wall-temperature or HTC data.

For B2, retain `mu_t/mu_in = 10` so that only inlet turbulence intensity changes relative to the accepted baseline. The next case is `tu083_vr10`, using the second C3X inlet turbulence level documented in NASA-CR-168015:

- `Tu_in = 8.3%`;
- `mu_t/mu_in = 10`;
- restart independently from accepted Transition SST iteration 556;
- all other settings unchanged.

The existing `baseline_tu065_vr10` is the B2 anchor. This requires one new B2 run rather than inventing an additional inlet turbulence level. Any lower-intensity or interaction case remains optional and must be justified after the `6.5 -> 8.3%` response is known.
