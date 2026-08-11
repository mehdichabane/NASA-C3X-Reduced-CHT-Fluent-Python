from scripts.verification.replay_saved_state_reports import (
    FLUENT_PRODUCT_VERSION,
    fluent_version_text,
    launch_saved_state_session,
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


def test_saved_state_audit_pins_fluent_release_dimension_and_precision() -> None:
    fake = _FakePyFluent()
    session = launch_saved_state_session(fake)

    assert session == "session"
    assert fake.kwargs == {
        "product_version": "26.1.0",
        "dimension": "two",
        "precision": "double",
    }
    assert FLUENT_PRODUCT_VERSION == "26.1.0"


def test_fluent_version_text_handles_enum_like_values() -> None:
    class _Version:
        value = "26.1.0"

    assert fluent_version_text(_Version()) == "26.1.0"
    assert fluent_version_text("26.1.0") == "26.1.0"
