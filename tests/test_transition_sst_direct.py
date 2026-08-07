from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
TRANSITION_DIR = ROOT / 'data/fluent_exports/transition_sst'

def metric_value(frame: pd.DataFrame, name: str) -> float:
    values = frame.loc[frame['metric'] == name, 'value']
    assert len(values) == 1
    return float(values.iloc[0])

def test_direct_transition_wall_export_matches_fluent_reports():
    wall = pd.read_csv(
        TRANSITION_DIR
        / "run145_transition_sst_fine_wall_direct_fluent_iter556.csv",
        skipinitialspace=True,
    )
    wall.columns = wall.columns.astype(str).str.strip()
    checks = pd.read_csv(TRANSITION_DIR / 'run145_transition_sst_global_checks.csv')
    monitors = pd.read_csv(TRANSITION_DIR / 'run145_transition_sst_convergence_monitors.csv')
    assert len(wall) == 819
    assert not wall.isna().any().any()
    assert wall['cellnumber'].is_unique
    area = wall['face-area-magnitude'].to_numpy(float)
    integrated_heat = float(np.sum(wall['heat-flux'].to_numpy(float) * area))
    area_temperature = float(np.sum(wall['temperature'].to_numpy(float) * area) / area.sum())
    area_yplus = float(np.sum(wall['y-plus'].to_numpy(float) * area) / area.sum())
    assert abs(integrated_heat - metric_value(checks, 'heat_rate_wall_vane_shadow')) < 0.01
    assert abs(area_temperature - float(monitors.iloc[-1]['mean_wall_temperature_K'])) < 0.001
    assert abs(area_yplus - metric_value(checks, 'wall_yplus_area_average')) < 1e-06

def test_transition_final_window_and_global_checks_pass():
    monitors = pd.read_csv(TRANSITION_DIR / 'run145_transition_sst_convergence_monitors.csv')
    checks = pd.read_csv(TRANSITION_DIR / 'run145_transition_sst_global_checks.csv')
    residuals = pd.read_csv(TRANSITION_DIR / 'run145_transition_sst_residuals_full.csv')
    assert int(monitors.iloc[0]['iteration']) == 236
    assert int(monitors.iloc[-1]['iteration']) == 556
    assert int(residuals.iloc[-1]['iteration']) == 556
    window = monitors.loc[monitors['iteration'].between(537, 556)]
    assert len(window) == 20
    for column in ('external_heat_rate_W_per_m', 'outlet_mach', 'mean_wall_temperature_K'):
        relative_span = (window[column].max() - window[column].min()) / abs(window[column].mean()) * 100.0
        assert relative_span < 0.02
    assert metric_value(checks, 'mass_imbalance_percent') < 0.01
    assert metric_value(checks, 'interface_mismatch_percent') < 0.01
    assert metric_value(checks, 'solid_heat_imbalance_percent') < 0.05
    assert metric_value(checks, 'wall_yplus_max') < 1.0
