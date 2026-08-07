from pathlib import Path
from scripts.postprocess.build_comparison_profiles import rebuild
from scripts.common.surface_mapping import read_coordinate_reference
ROOT = Path(__file__).resolve().parents[1]

def test_both_models_rebuild_from_source_like_exports():
    reference = read_coordinate_reference(ROOT / 'references/model_inputs/run145_wall_surface_coordinate_reference.csv')
    files = [
        ROOT / "data/fluent_exports/mesh_sensitivity/run145_sst_fine_wall.csv",
        ROOT
        / "data/fluent_exports/transition_sst/"
        "run145_transition_sst_fine_wall_direct_fluent_iter556.csv",
    ]
    for source in files:
        result = rebuild(source, reference)
        assert len(result) == 819
        assert set(result['surface']) == {'pressure', 'suction'}
        assert result['coordinate_mapping_distance_m'].max() < 2e-07
        assert result['x_over_c'].between(0, 1).all()
