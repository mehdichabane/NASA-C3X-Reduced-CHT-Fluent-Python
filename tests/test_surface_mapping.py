import numpy as np
import pandas as pd
from pathlib import Path
from scripts.common.surface_mapping import read_coordinate_reference, map_by_coordinates
ROOT = Path(__file__).resolve().parents[1]

def test_mapping_ignores_cell_numbers_and_row_order():
    raw = pd.read_csv(ROOT / 'data/fluent_exports/mesh_sensitivity/run145_sst_fine_wall.csv', skipinitialspace=True)
    raw.columns = raw.columns.str.strip()
    reference = read_coordinate_reference(ROOT / 'references/model_inputs/run145_wall_surface_coordinate_reference.csv')
    baseline = map_by_coordinates(raw, reference).sort_values(['x-coordinate', 'y-coordinate'])
    changed = raw.sample(frac=1.0, random_state=19).reset_index(drop=True)
    changed['cellnumber'] = np.arange(900001, 900001 + len(changed))
    remapped = map_by_coordinates(changed, reference).sort_values(['x-coordinate', 'y-coordinate'])
    assert baseline['surface'].tolist() == remapped['surface'].tolist()
    assert baseline['raw_side'].tolist() == remapped['raw_side'].tolist()
    assert remapped['coordinate_mapping_distance_m'].max() < 1e-12
