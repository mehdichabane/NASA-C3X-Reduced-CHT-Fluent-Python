from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]

def test_all_three_meshes_have_committed_quality_metrics():
    data = pd.read_csv(ROOT / 'data/fluent_exports/mesh_sensitivity/mesh_quality_all_grids.csv')
    global_rows = data[data.scope == 'global'].set_index('mesh')
    assert set(global_rows.index) == {'coarse', 'medium', 'fine'}
    assert (global_rows.minimum_orthogonal_quality > 0).all()
    assert (global_rows.maximum_equiangle_skewness < 1).all()
    assert abs(global_rows.loc['fine', 'minimum_orthogonal_quality'] - 0.12858908347404827) < 1e-12
    assert abs(global_rows.loc['fine', 'maximum_equiangle_skewness'] - 0.8025744851335743) < 1e-12
