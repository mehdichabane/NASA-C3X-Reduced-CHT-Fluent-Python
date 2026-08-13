from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL_INPUTS = ROOT / "references/model_inputs"


def test_archived_thermophysical_values_have_qualified_matches() -> None:
    provenance = pd.read_csv(MODEL_INPUTS / "material_property_provenance.csv")
    rows = provenance.set_index(["domain", "property"])

    expected = {
        ("solid", "density"): 8030.0,
        ("solid", "specific_heat"): 473.0,
        ("hot_gas", "molecular_weight"): 28.96,
        ("hot_gas", "specific_heat"): 1075.0,
        ("hot_gas", "dynamic_viscosity"): 3.33e-05,
        ("hot_gas", "thermal_conductivity"): 0.05234,
    }
    for key, value in expected.items():
        assert np.isclose(float(rows.loc[key, "case_value"]), value, rtol=0.0, atol=1e-12)
        assert "match" in rows.loc[key, "independent_literature_status"].lower()


def test_hot_gas_conductivity_matches_published_cp_mu_pr_triple() -> None:
    cp = 1075.0
    mu = 3.33e-05
    pr = 0.684
    implied_k = cp * mu / pr

    assert np.isclose(implied_k, 0.05233552631578947, rtol=0.0, atol=1e-15)
    assert round(implied_k, 5) == 0.05234


def test_source_scope_is_not_overextended() -> None:
    matches = pd.read_csv(MODEL_INPUTS / "thermophysical_literature_matches.csv")
    rows = matches.set_index(["domain", "property"])

    density_note = rows.loc[("solid", "density"), "scope_note"].lower()
    conductivity_note = rows.loc[("solid", "thermal_conductivity_intercept"), "scope_note"].lower()
    gas_k_note = rows.loc[("hot_gas", "thermal_conductivity"), "scope_note"].lower()

    assert "density only" in density_note
    assert "restricted to conductivity" in conductivity_note
    assert "does not directly tabulate" in gas_k_note
