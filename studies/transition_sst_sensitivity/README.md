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

## Phase B2: inlet-turbulence-intensity sensitivity at fixed viscosity ratio

B2 keeps `mu_t/mu_in = 10` fixed and changes only the prescribed inlet turbulence intensity from the accepted `6.5%` baseline to the second C3X inlet level, `8.3%`. The new case restarts independently from the accepted Transition SST state at iteration 556.

### `tu083_vr10`

The case converges automatically at iteration `651` using the common 20-iteration report-definition criterion.

Final CFF hashes:

- case SHA-256: `bf4ce538011b3e41222af51479d3829c4311d855446fa59aabc89dff87e091c2`;
- data SHA-256: `efb468e1ebfb057a41a39663b561ff7c15defb6ed8e5c1b4eef34d604511038d`.

The 37 mesh datasets are byte-for-byte identical to the baseline. A direct comparison of Fluent `Thread Variables` shows a single intended boundary-condition change: inlet `turb-intensity` changes from `0.065` to `0.083`; all other serialized thread settings are unchanged.

The final `2-5 mm` pre-leading-edge diagnostic is:

- median `Tu = 1.23704%`;
- median `mu_t/mu = 7.52764`;
- median `Re_theta_t = 417.412`;
- median `k = 2.85903 m2/s2`.

Relative to `baseline_tu065_vr10`:

- mean external wall temperature: `608.879 -> 608.678 K` (`-0.033%`);
- external heat-transfer rate: `28.5483 -> 28.5133 kW/m` (`-0.122%`);
- outlet Mach number: `0.903351 -> 0.903358` (`+0.0007%`).

The prescribed inlet change is therefore strongly attenuated before the vane in this `vr10` configuration. At `50-55 mm` upstream, the median turbulence intensity is higher than the `6.5%` baseline (`4.186%` versus `3.924%`), but the decay curves approach one another and cross between the `25-30 mm` and `20-25 mm` bins. In the final `2-5 mm` bin, the `8.3%` case reaches `1.2370%`, compared with `1.2473%` for the baseline.

The suction-side transition-like response changes only slightly. The intermittency-gradient and wall-temperature-gradient maxima move from `x/Cx = 0.65338` to `0.65512`, and the wall-shear-gradient maximum from `0.65512` to `0.65685`. These shifts are one wall-face station in the present extraction and are not interpreted as a materially different experimental transition onset.

The final 20-iteration maximum relative changes are `0.01978%` for external heat rate, `0.00554%` for mean wall temperature and `0.000538%` for outlet Mach, all below the common `0.02%` criterion. Final continuity is `4.132e-05` and maximum wall `y+` is `0.4029`.

The explicitly recorded closure Flux Reports also pass the study limits:

- mass imbalance: `0.000086%`;
- fluid-solid interface heat mismatch: `0.000016%`;
- solid heat imbalance from `wall_vane` plus all ten cooling-hole heat rates: `0.002097%`.

Detailed B2 results are in `tu083_vr10_freestream_decay.csv`, `tu083_vr10_transition_signature.csv`, `tu083_vr10_global_checks.csv`, `tu083_vr10_integral_summary.csv`, `tu065_vs_tu083_vr10_diagnostic_summary.csv` and `b2_two_point_summary.csv`.

## Campaign conclusion

B1 establishes a strong, nonlinear viscosity-ratio sensitivity at fixed `Tu_in = 6.5%`:

`mu_t/mu_in: 10 -> 5 -> 1`

maps to approximately

`Tu_2-5mm: 1.247% -> 0.870% -> 0.364%`.

The accompanying thermal/transition response changes strongly while outlet Mach changes comparatively little. This supports inlet-to-vane turbulence decay as a major model sensitivity. It does not identify an optimal viscosity ratio and is not used to tune the calculation to NASA wall-temperature or HTC data.

B2 then changes the documented inlet turbulence level at fixed `mu_t/mu_in = 10`:

`Tu_in: 6.5% -> 8.3%`

while the near-vane median changes only

`Tu_2-5mm: 1.247% -> 1.237%`.

The corresponding changes in mean wall temperature (`-0.033%`), external heat-transfer rate (`-0.122%`) and outlet Mach (`+0.0007%`) are small, and the transition-like response shifts by only one wall-face station. Within the deterministic perturbations tested here, the viscosity-ratio changes therefore produce a much larger model response than the documented `6.5 -> 8.3%` inlet-intensity change.

The minimum sensitivity campaign is complete: two B1 viscosity-ratio runs and one B2 inlet-intensity run, all restarted independently from iteration 556 and closed against common convergence/balance criteria. No additional CFD case is required for the present diagnostic question. A `Tu x mu_t/mu` interaction case remains possible only if a later study poses a specific interaction question; it is not part of the current campaign.
