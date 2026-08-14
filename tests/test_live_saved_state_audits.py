import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "results" / "processed" / "verification" / "live_saved_state_audits"
MANIFEST = ROOT / "fluent" / "restart_manifest.csv"
EXPECTED_REPORTS = [
    "fine_external_heat_rate",
    "fine_wall_temperature_avg",
    "fine_mach_outlet",
]
EXPECTED_SCOPE = (
    "saved-state report recomputation only; no initialization, iteration replay, "
    "mesh regeneration or equivalence claim"
)


def manifest_rows() -> dict[str, dict[str, str]]:
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        return {row["mesh"]: row for row in csv.DictReader(handle)}


def load_audit(name: str) -> dict[str, object]:
    return json.loads((AUDIT_DIR / name).read_text(encoding="utf-8"))


def assert_common_audit_fields(payload: dict[str, object]) -> None:
    assert payload["requested_fluent_version"] == "26.1.0"
    assert payload["actual_fluent_version"] == "26.1.0"
    assert payload["dimension"] == "2D"
    assert payload["precision"] == "double"
    assert payload["ui_mode"] == "no_gui"
    assert payload["report_definitions"] == EXPECTED_REPORTS
    assert payload["scope"] == EXPECTED_SCOPE

    computed = payload["computed"]
    assert isinstance(computed, list)
    assert [next(iter(item)) for item in computed] == EXPECTED_REPORTS


def test_fine_sst_live_audit_matches_restart_manifest() -> None:
    payload = load_audit("run145_sst_fine_saved_state_audit.json")
    row = manifest_rows()["fine"]
    assert_common_audit_fields(payload)

    assert Path(str(payload["case_file"])).name == row["case_file"]
    assert Path(str(payload["data_file"])).name == row["data_file"]
    assert payload["case_sha256"] == row["sha256_case"]
    assert payload["data_sha256"] == row["sha256_data"]


def test_transition_sst_live_audit_matches_restart_manifest() -> None:
    payload = load_audit("run145_transition_sst_fine_saved_state_audit.json")
    row = manifest_rows()["transition_sst_fine"]
    assert_common_audit_fields(payload)

    assert Path(str(payload["case_file"])).name == row["case_file"]
    assert Path(str(payload["data_file"])).name == row["data_file"]
    assert payload["case_sha256"] == row["sha256_case"]
    assert payload["data_sha256"] == row["sha256_data"]
