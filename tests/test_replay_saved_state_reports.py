from pathlib import Path

from scripts.verification.replay_saved_state_reports import (
    FLUENT_PRODUCT_VERSION,
    FLUENT_UI_MODE,
    fluent_version_text,
    launch_saved_state_session,
    matching_data_file,
    sha256_file,
)


class _FakeDimension:
    TWO = "two"


class _FakePrecision:
    DOUBLE = "double"


class _FakePyFluent:
    Dimension = _FakeDimension
    Precision = _FakePrecision

    def __init__(self) -> None:
        self.kwargs: dict[str, object] | None = None

    def launch_fluent(self, **kwargs: object) -> str:
        self.kwargs = kwargs
        return "session"


def test_saved_state_audit_pins_fluent_release_dimension_precision_and_ui() -> None:
    fake = _FakePyFluent()
    session = launch_saved_state_session(fake)

    assert session == "session"
    assert fake.kwargs == {
        "product_version": "26.1.0",
        "dimension": "two",
        "precision": "double",
        "ui_mode": "no_gui",
    }
    assert FLUENT_PRODUCT_VERSION == "26.1.0"
    assert FLUENT_UI_MODE == "no_gui"


def test_fluent_version_text_handles_enum_like_values() -> None:
    class _Version:
        value = "26.1.0"

    assert fluent_version_text(_Version()) == "26.1.0"
    assert fluent_version_text("26.1.0") == "26.1.0"


def test_matching_data_file_uses_standard_cff_pair_name() -> None:
    case_file = Path("fine.cas.h5")
    assert matching_data_file(case_file) == Path("fine.dat.h5")


def test_sha256_file_records_input_identity(tmp_path: Path) -> None:
    path = tmp_path / "sample.dat.h5"
    path.write_bytes(b"NASA C3X")
    assert sha256_file(path) == "05b0bedee1ece789f956bc968f119cb9742bdd14973266beb2156a1893057010"
