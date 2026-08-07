import numpy as np
from scripts.comparison.compare_run145 import error_metrics

def test_error_metrics_known_values():
    experimental = np.array([1.0, 2.0, 4.0])
    predicted = np.array([2.0, 1.0, 5.0])
    values = error_metrics(experimental, predicted)
    assert values['mean_bias'] == 1 / 3
    assert values['mae'] == 1.0
    assert np.isclose(values['rmse'], 1.0)
    assert np.isclose(values['mape_percent'], (1 + 0.5 + 0.25) / 3 * 100)
