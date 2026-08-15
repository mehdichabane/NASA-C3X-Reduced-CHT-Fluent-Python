# Transition SST inlet-turbulence sensitivity

This study asks why the fine-grid Transition SST case preserves the Run 145 pressure comparison while producing a substantially different thermal field from the SST baseline. Phase A diagnoses the accepted Transition SST solution; Phase B changes the inlet turbulence state one parameter at a time while keeping the mesh, thermal boundary conditions, numerics and model settings fixed.

The study is diagnostic rather than a calibration exercise. The case levels were not chosen to minimise NASA error.

## Case matrix

All sensitivity cases restart independently from the accepted Transition SST state at iteration 556.

| Case | `Tu_in` | `mu_t/mu_in` | Purpose |
|---|---:|---:|---|
| `baseline_tu065_vr10` | 6.5% | 10 | accepted baseline |
| `tu065_vr05` | 6.5% | 5 | viscosity-ratio sensitivity |
| `tu065_vr01` | 6.5% | 1 | viscosity-ratio sensitivity |
| `tu083_vr10` | 8.3% | 10 | inlet-intensity sensitivity |

The accepted baseline also uses inlet intermittency `1.0`, the built-in Transition SST correlations, and no roughness or curvature correction. Detailed settings are in `references/model_inputs/transition_sst_settings.csv`.

## Baseline freestream decay

The computational inlet is about `58.605 mm` upstream of the geometric leading edge. The saved inlet faces contain the prescribed `Tu = 6.5%`, but the local turbulence level decays strongly before the vane.

For the upstream diagnostic, fluid cells ahead of the leading edge and more than `8 mm` from a wall are grouped in axial bins. Turbulence intensity is reconstructed from the saved fields as

`Tu = 100 sqrt(2 k / 3) / |U|`.

In the `2–5 mm` bin immediately upstream of the leading edge, the accepted baseline gives:

- median `Tu = 1.2473%`;
- median `mu_t/mu = 7.851`;
- median `Re_theta_t = 412.933`.

The full decay curve is in `baseline_freestream_decay.csv`.

## Transition-like wall response

The vane wall is traversed from leading edge to trailing edge on the pressure and suction sides. In the baseline case, the strongest concurrent suction-side intermittency and wall-temperature gradients occur near `x/Cx = 0.6534`, with the wall-shear gradient near `0.6551`.

This location is used only as a transition-like response front in the CFD solution. It is not treated as an experimentally measured transition onset. The extracted thresholds and gradient locations are in `baseline_transition_signature.csv`.

## Viscosity-ratio sensitivity at fixed `Tu_in = 6.5%`

Reducing the inlet turbulent-viscosity ratio produces much stronger freestream decay before the vane and a large thermal response.

| `mu_t/mu_in` | Near-LE median `Tu` | Mean wall temperature | External heat rate | Outlet Mach | Suction-side response |
|---:|---:|---:|---:|---:|---|
| 10 | `1.2473%` | `608.879 K` | `28.5483 kW/m` | `0.903351` | about `0.65 x/Cx` |
| 5 | `0.8701%` | `604.438 K` | `27.7758 kW/m` | `0.903562` | about `0.69 x/Cx` |
| 1 | `0.3637%` | `574.705 K` | `22.9198 kW/m` | `0.905424` | trailing-edge region |

The ratio-1 case moves the intermittency and wall-shear response to about `x/Cx = 0.962–0.968`. For that case, the interior gradient search is restricted to `x/Cx < 0.98` so the geometric trailing edge does not dominate the diagnostic.

The three-point result is summarised in `b1_three_point_summary.csv`; detailed case outputs remain in the corresponding `tu065_vr05_*`, `tu065_vr01_*` and comparison CSVs.

## Experimental inlet-turbulence reference

NASA-CR-168015 reports `Tu` as the average inlet turbulence intensity for the C3X cascade. The combustor-induced inlet level was `6.5%`, measured with laser Doppler anemometry (LDA), and upstream rods increased it to `8.3%`.

These values are therefore treated as inlet-level conditions, not leading-edge targets. The exact axial correspondence between the experimental measurement plane and this reduced computational inlet is not assumed.

## Inlet-intensity sensitivity at fixed `mu_t/mu_in = 10`

Changing the prescribed inlet turbulence intensity from `6.5%` to `8.3%` produces a very different result from the viscosity-ratio sweep:

| `Tu_in` | Near-LE median `Tu` | Mean wall temperature | External heat rate | Outlet Mach |
|---:|---:|---:|---:|---:|
| 6.5% | `1.2473%` | `608.879 K` | `28.5483 kW/m` | `0.903351` |
| 8.3% | `1.2370%` | `608.678 K` | `28.5133 kW/m` | `0.903358` |

The two decay curves differ farther upstream but approach and cross before the vane. By the final `2–5 mm` bin, the near-vane turbulence levels are almost the same. Mean wall temperature changes by only `-0.033%`, external heat rate by `-0.122%`, and the suction-side response shifts by one wall-face station.

Detailed outputs are in `tu083_vr10_freestream_decay.csv`, `tu083_vr10_transition_signature.csv`, `tu083_vr10_global_checks.csv`, `tu083_vr10_integral_summary.csv`, `tu065_vs_tu083_vr10_diagnostic_summary.csv` and `b2_two_point_summary.csv`.

## Closure

The sensitivity runs use the same 20-iteration report-definition criterion as the accepted case: external heat rate, mean wall temperature and outlet Mach must each remain within a `0.02%` maximum relative-change window, with continuity below `1e-3`. Mass balance, fluid-solid interface heat mismatch and wall `y+` are checked at closure; the retained cases satisfy the study limits.

For `tu065_vr01`, the final CFF archive does not contain a persisted cooling-hole total Flux Report, so a final solid heat-imbalance value is not reconstructed from that file. Later cases explicitly save the required Flux Reports at closure. The detailed checks remain in the case-specific `*_global_checks.csv` files.

## Conclusion

At fixed `Tu_in = 6.5%`, changing

`mu_t/mu_in: 10 -> 5 -> 1`

changes the near-leading-edge turbulence roughly as

`Tu_2-5mm: 1.247% -> 0.870% -> 0.364%`

and produces large changes in the thermal field and transition-like wall response while outlet Mach moves comparatively little.

By contrast, at fixed `mu_t/mu_in = 10`, changing the documented inlet level from `6.5%` to `8.3%` leaves the near-vane turbulence and thermal solution almost unchanged.

For the tested setup, inlet-to-vane turbulence decay is therefore strongly sensitive to turbulent-viscosity ratio. The study does not identify an optimal ratio, and no coarse or medium Transition SST cases were run, so the response-front locations are treated as fine-grid model diagnostics rather than mesh-independent transition predictions.
