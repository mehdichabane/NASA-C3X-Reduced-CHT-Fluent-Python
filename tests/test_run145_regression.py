import numpy as np
import pandas as pd

from scripts.common.surface_mapping import read_coordinate_reference
from scripts.comparison.compare_run145 import (
    NASA_PRESSURE,
    NASA_THERMAL,
    NASA_UNCERTAINTY,
    cfd_profile,
    pressure_comparison,
    read_csv,
    thermal_comparison,
)
from scripts.postprocess.build_comparison_profiles import REFERENCE, SOURCES, rebuild

EXPECTED_MAE = {
    ("SST", "pressure ratio", "pressure"): 0.007100123391993277,
    ("SST", "pressure ratio", "suction"): 0.02332799371289168,
    ("SST", "wall temperature", "pressure"): 8.887096957375554,
    ("SST", "wall temperature", "suction"): 12.998667905063853,
    ("SST", "heat-transfer coefficient", "pressure"): 46.95389547960131,
    ("SST", "heat-transfer coefficient", "suction"): 84.31954635524973,
    ("Transition SST", "pressure ratio", "pressure"): 0.006201084590902762,
    ("Transition SST", "pressure ratio", "suction"): 0.02356898607967708,
    ("Transition SST", "wall temperature", "pressure"): 39.36568013032755,
    ("Transition SST", "wall temperature", "suction"): 41.72347795370152,
    ("Transition SST", "heat-transfer coefficient", "pressure"): 294.65776586899807,
    ("Transition SST", "heat-transfer coefficient", "suction"): 281.01023076182787,
}


def test_run145_comparison_regression_from_raw_wall_exports() -> None:
    reference = read_coordinate_reference(REFERENCE)
    model_names = {"sst": "SST", "transition_sst": "Transition SST"}
    profiles: dict[tuple[str, str], pd.DataFrame] = {}

    for source_name, source in SOURCES.items():
        rebuilt = rebuild(source, reference)
        model = model_names[source_name]
        for surface in ("pressure", "suction"):
            profiles[(model, surface)] = cfd_profile(rebuilt, surface)

    nasa_pressure = read_csv(NASA_PRESSURE)
    nasa_thermal = read_csv(NASA_THERMAL)
    uncertainty = read_csv(NASA_UNCERTAINTY)
    _, pressure_rows = pressure_comparison(nasa_pressure, profiles)
    _, thermal_rows = thermal_comparison(nasa_thermal, uncertainty, profiles)
    summary = pd.DataFrame(pressure_rows + thermal_rows)

    for (model, quantity, surface), expected in EXPECTED_MAE.items():
        match = summary.loc[
            (summary["model"] == model)
            & (summary["quantity"] == quantity)
            & (summary["surface"] == surface),
            "mae",
        ]
        assert len(match) == 1
        assert np.isclose(float(match.iloc[0]), expected, rtol=2e-6, atol=2e-8)
