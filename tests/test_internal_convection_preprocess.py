from __future__ import annotations
import pandas as pd
import pytest
from scripts.preprocess.build_internal_convection_inputs import (
    OUTPUT_PATH,
    build_internal_convection_table,
    check_against_committed,
)

def test_internal_convection_formulas_and_ten_passage_assembly() -> None:
    committed = pd.read_csv(OUTPUT_PATH)
    by_temperature = {float(row.T_coolant_K): row for row in committed.itertuples(index=False)}

    def committed_property_provider(temperature_k: float, pressure_pa: float) -> tuple[float, float, float, float, str]:
        row = by_temperature[temperature_k]
        assert pressure_pa == pytest.approx(101325.0)
        return (float(row.cp_J_kgK), float(row.mu_Pa_s), float(row.k_air_W_mK), float(row.Pr), '8.0.0')
    generated = build_internal_convection_table(committed_property_provider)
    assert generated['hole_no'].tolist() == list(range(1, 11))
    assert generated['boundary_name'].tolist()[-1] == 'cooling_hole_10'
    assert generated['Nu_D'].tolist() == pytest.approx(committed['Nu_D'].tolist(), rel=5e-09)
    assert generated['h_W_m2K'].tolist() == pytest.approx(committed['h_W_m2K'].tolist(), rel=5e-09)

def test_coolprop_8_reproduces_all_ten_committed_coefficients() -> None:
    pytest.importorskip('CoolProp')
    generated = build_internal_convection_table()
    committed = pd.read_csv(OUTPUT_PATH)
    check_against_committed(generated, committed)
