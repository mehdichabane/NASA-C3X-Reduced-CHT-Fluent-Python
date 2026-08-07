from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/fluent_exports/mesh_sensitivity/mesh_quality_distribution_all_grids.csv'

def test_committed_mesh_quality_distribution_is_complete_and_consistent():
    data = pd.read_csv(SOURCE).set_index('mesh')
    assert set(data.index) == {'coarse', 'medium', 'fine'}
    expected = {
        "coarse": {
            "cells": 14657,
            "oq": 19,
            "skew": 0,
            "ar100": 4198,
            "ar500": 1403,
            "ar1000": 243,
        },
        "medium": {
            "cells": 23781,
            "oq": 14,
            "skew": 0,
            "ar100": 5177,
            "ar500": 927,
            "ar1000": 0,
        },
        "fine": {
            "cells": 44760,
            "oq": 0,
            "skew": 1,
            "ar100": 6552,
            "ar500": 0,
            "ar1000": 0,
        },
    }
    columns = {
        "oq": "orthogonal_quality_below_0p1_count",
        "skew": "skewness_above_0p75_count",
        "ar100": "aspect_ratio_above_100_count",
        "ar500": "aspect_ratio_above_500_count",
        "ar1000": "aspect_ratio_above_1000_count",
    }
    for mesh, values in expected.items():
        row = data.loc[mesh]
        assert int(row['cells']) == values['cells']
        for label, column in columns.items():
            assert int(row[column]) == values[label]
            percent_column = column.replace('_count', '_percent')
            assert abs(float(row[percent_column]) - 100.0 * values[label] / values['cells']) < 1e-12
        for prefix in ('minimum_orthogonal_quality', 'maximum_equiangle_skewness', 'maximum_fluent_aspect_ratio'):
            assert 1 <= int(row[f'{prefix}_cell']) <= values['cells']
            assert str(row[f'{prefix}_zone']).strip()
