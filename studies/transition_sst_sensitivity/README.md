# Transition SST inlet-turbulence sensitivity

This study investigates why the fine-grid Transition SST solution preserves the Run 145 pressure comparison while producing a substantially different thermal field from the SST baseline. It is a model-behavior and sensitivity study, not a calibration exercise and not an uncertainty quantification.

No new Fluent boundary condition has been changed at this stage. Phase A diagnoses the accepted Transition SST solution at iteration 556 before defining a sensitivity matrix.

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

## Interpretation and decision gate

The Phase A result provides a concrete mechanism to test: the current computational inlet is prescribed at `6.5%` turbulence intensity, but the saved solution contains only about `1.25%` median freestream turbulence intensity immediately upstream of the vane. The suction-side thermal/shear response changes sharply near `x/Cx ~ 0.65`, while the pressure side does not show the same transported-intermittency signature.

This is a hypothesis-generating diagnostic, not proof that freestream decay causes the Transition SST thermal disagreement. Causality requires controlled perturbation runs.

Before defining those runs, the spatial measurement/reference location of the experimental `6.5%` turbulence level must be verified from NASA-CR-168015. It has not been established from the primary report in this study yet. The subsequent `Tu_in` and `mu_t/mu_in` levels will therefore be chosen a priori from the physical inlet-to-vane decay problem rather than selected to minimize the NASA temperature or HTC error.
