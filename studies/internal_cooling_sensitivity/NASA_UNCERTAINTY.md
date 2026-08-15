# Internal-HTC +/-3% sensitivity

NASA-CR-168015 reports an estimated `+/-3%` uncertainty for the radial
cooling-hole heat-transfer-coefficient calculation used in the experimental
thermal reduction. I already had Fluent sensitivity cases at `h/h0 = 0.95`,
`1.00` and `1.05`, so I used those solved cases to estimate the response to a
`+/-3%` change instead of running another pair of cases.

The source value is transcribed in
[`references/experimental_data/c3x_experimental_uncertainty_summary.csv`](../../references/experimental_data/c3x_experimental_uncertainty_summary.csv)
from Hylton et al., NASA-CR-168015 (1983).

## Calculation

For each response `Y`, I take the slope through the two central sensitivity
cases:

```text
dY / d(+1% h) = [Y(1.05 h0) - Y(0.95 h0)] / 10
```

and apply it around the baseline:

```text
Y(h0 +/- 3%) = Y(h0) +/- 3 * dY/d(+1% h)
```

The existing five-point `h` sweep is close to linear over
`h/h0 = 0.90 ... 1.10` (`R2` is about `0.999` for the main thermal responses),
so this local interpolation is adequate for the small `+/-3%` step. The table is
rebuilt by
[`scripts/postprocess/build_nasa_informed_cooling_envelope.py`](../../scripts/postprocess/build_nasa_informed_cooling_envelope.py)
and written to
[`nasa_informed_internal_htc_envelope.csv`](nasa_informed_internal_htc_envelope.csv).

## Result

| Quantity | Baseline | `h - 3%` | `h + 3%` | Half-width |
|---|---:|---:|---:|---:|
| Mean external wall temperature | `655.619 K` | `657.354 K` | `653.884 K` | `1.735 K` |
| External heat-transfer rate | `35.820 kW/m` | `35.267 kW/m` | `36.372 kW/m` | `0.552 kW/m` |
| Wall-temperature bias, pressure side | `+8.887 K` | `+10.947 K` | `+6.827 K` | `2.060 K` |
| Wall-temperature bias, suction side | `+12.999 K` | `+14.582 K` | `+11.416 K` | `1.583 K` |
| Wall-temperature MAPE, pressure side | `1.448%` | `1.760%` | `1.136%` | `0.312` percentage point |
| Wall-temperature MAPE, suction side | `2.005%` | `2.243%` | `1.766%` | `0.238` percentage point |

The wall-temperature bias stays positive on both surfaces across this range, so
the `+/-3%` internal-HTC change does not remove the SST/NASA temperature
difference.

This is an interpolation of the existing `h` sensitivity study, not a new
Fluent run. The `Tbulk +/-5 K` and `+/-10 K` cases remain separate sensitivity
cases because the retained NASA record does not give an equivalent quantitative
uncertainty for those coolant temperatures. NASA Table VI already supplies the
experimental external-HTC uncertainty used for the comparison error bars, so the
internal `+/-3%` term is not added to those intervals again.
