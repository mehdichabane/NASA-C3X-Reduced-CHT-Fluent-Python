# Transition SST inlet-turbulence sensitivity

This study investigates why the fine-grid Transition SST solution preserves the Run 145 pressure comparison while producing a substantially different thermal field from the SST baseline. It is a model-behavior and sensitivity study, not a calibration exercise and not an uncertainty quantification.

Phase A diagnoses the accepted Transition SST solution at iteration 556. Phase B then perturbs the inlet turbulence state in controlled one-factor cases while keeping the mesh, thermal boundary conditions, numerics and Transition SST model settings unchanged.

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

For the upstream freestream diagnostic, only fluid cells upstream of the geometric leading edge and farther than `8 mm` from a wall are retained. Values are summarized in axial bins using the median, with the 10th and 90th percentiles also retained for `Tu`. This filter was checked at 5, 8, 10 and 15 mm wall-distance cutoffs; the near-leading-edge median remains approximately `1.24-1.29%`.

The current case therefore does not carry the imposed `6.5%` unchanged to the vane. In the `2-5 mm` freestream bin immediately upstream of the leading edge:

- median `Tu = 1.2473%`;
- 10th-90th percentile `Tu = 1.0371-1.8159%`;
- median `mu_t/mu = 7.851`;
- median `Re_theta_t = 412.933`.

Relative to the prescribed inlet intensity, the median `Tu` reduction is about `80.81%`. The corresponding turbulent kinetic energy also falls strongly, so this is not only an acceleration effect.

Detailed values are in `baseline_freestream_decay.csv`; the case audit is in `baseline_case_audit.csv`.

## Phase A: wall transition signature

The `wall_vane-shadow` loop was traversed geometrically from the leading edge to the trailing edge on each side. Saved wall-adjacent intermittency, `Re_theta_t`, wall temperature and wall shear were then inspected along the two paths.

On the suction side, the transported intermittency remains near `0.020` through the first half of the surface and then begins a sharp local rise. The largest concurrent gradients in intermittency and wall temperature occur around `s/L = 0.4972`, `x/Cx = 0.6534`; the largest wall-shear gradient is nearby at `s/L = 0.4994`, `x/Cx = 0.6551`. The pressure side shows no comparable mid-side intermittency rise: between `0.1 < s/L < 0.9`, its saved intermittency remains approximately `0.02000-0.02044`.

This location is described here as a **transition-like response front**, not as an experimentally established transition onset. In particular, the transported wall-adjacent intermittency does not approach `0.5` in the mid-suction-side region, so a `gamma = 0.5` criterion is not used.

Selected threshold and gradient locations are recorded in `baseline_transition_signature.csv`.

## Phase B1: viscosity-ratio sensitivity at fixed inlet intensity

The first controlled case, `tu065_vr05`, keeps `Tu_in = 6.5%` and changes only the inlet turbulent viscosity ratio from `10` to `5`. It is restarted from the accepted Transition SST state at iteration 556 and converges at iteration 686.

The final inlet face fields still reproduce `Tu = 6.500000%`, `gamma = 1.000000` and `Re_theta_t = 100.359274`. The final mesh is byte-for-byte identical to the baseline mesh.

The global checks pass the existing study limits:

- mass imbalance: `0.000396%`;
- fluid-solid interface mismatch: `2.26e-5%`;
- solid heat imbalance: `0.00621%`;
- maximum saved wall `y+`: `0.3983`.

The main integral response relative to the `vr10` baseline is:

- mean external wall temperature: `608.879 -> 604.438 K` (`-4.441 K`);
- external heat-transfer rate: `28.5483 -> 27.7758 kW/m` (`-2.706%`);
- outlet Mach number: `0.903351 -> 0.903562` (`+0.0234%`).

The freestream-decay diagnostic changes substantially. In the same `2-5 mm` pre-leading-edge bin:

- median `Tu`: `1.2473 -> 0.8701%` (`-30.24%`);
- median `mu_t/mu`: `7.851 -> 3.698` (`-52.89%`);
- median `Re_theta_t`: `412.933 -> 655.346` (`+58.71%`);
- median `k`: `2.9090 -> 1.4145 m2/s2` (`-51.38%`);
- median speed changes by only about `-0.004%`.

The suction-side transition-like response also moves downstream. The maximum intermittency-gradient location shifts from `x/Cx = 0.6534` to `0.6858`; the maximum wall-temperature-gradient location shifts from `0.6534` to `0.6842`; and the maximum wall-shear-gradient location shifts from `0.6551` to `0.6858`. The pressure-side mid-surface intermittency remains near `0.0200` with no comparable response front.

This first controlled perturbation therefore supports the proposed mechanism: reducing inlet `mu_t/mu` at fixed `Tu_in` increases freestream turbulence decay, lowers the turbulence level reaching the vane and delays the suction-side transition-like thermal/shear response. It also changes the thermal field substantially while leaving outlet Mach nearly unchanged. The result is a sensitivity observation, not a calibration result and not proof that a specific experimental transition location has been recovered.

Detailed results are in `tu065_vr05_global_checks.csv`, `tu065_vr05_integral_summary.csv`, `tu065_vr05_freestream_decay.csv`, `tu065_vr05_transition_signature.csv` and `vr10_vs_vr05_diagnostic_summary.csv`.

## Interpretation and decision gate

Phase A established that the baseline computational inlet is prescribed at `6.5%` turbulence intensity while the saved solution contains only about `1.25%` median freestream turbulence intensity immediately upstream of the vane. The first B1 perturbation shows that reducing `mu_t/mu_in` from `10` to `5` lowers that near-vane value further to about `0.87%` and moves the suction-side transition-like response downstream by roughly `0.03 x/Cx`.

The spatial measurement/reference location of the experimental `6.5%` turbulence level has still not been established from NASA-CR-168015 in this study. Subsequent levels are therefore chosen from the inlet-to-vane decay problem rather than selected to minimize NASA temperature or HTC error.
