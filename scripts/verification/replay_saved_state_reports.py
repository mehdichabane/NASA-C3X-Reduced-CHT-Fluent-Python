from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

FLUENT_PRODUCT_VERSION = "26.1.0"
FLUENT_UI_MODE = "no_gui"
DEFAULT_REPORTS = (
    "fine_external_heat_rate",
    "fine_wall_temperature_avg",
    "fine_mach_outlet",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Open a saved Fluent 26.1 case/data pair through PyFluent and "
            "recompute existing scalar report definitions for a saved-state audit."
        )
    )
    parser.add_argument(
        "case_file",
        type=Path,
        help=(
            "Path to the .cas.h5 file. The matching .dat.h5 file must remain "
            "beside it with the corresponding Fluent filename."
        ),
    )
    parser.add_argument(
        "--report",
        nargs="+",
        default=list(DEFAULT_REPORTS),
        help="Existing Fluent report-definition names to compute.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path. Results are always printed to stdout.",
    )
    return parser.parse_args()


def json_ready(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return str(value)


def fluent_version_text(value: Any) -> str:
    """Return the underlying Fluent version string for enum- or string-like values."""
    return str(getattr(value, "value", value))


def matching_data_file(case_file: Path) -> Path:
    """Return the conventional matching Fluent data-file path for a CFF case file."""
    if not case_file.name.endswith(".cas.h5"):
        raise ValueError("Expected a Fluent .cas.h5 filename.")
    return case_file.with_name(
        case_file.name.removesuffix(".cas.h5") + ".dat.h5"
    )


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a local file without loading it all into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def launch_saved_state_session(pyfluent: Any) -> Any:
    """Launch the same Fluent release, dimension and precision used by the benchmark."""
    return pyfluent.launch_fluent(
        product_version=FLUENT_PRODUCT_VERSION,
        dimension=pyfluent.Dimension.TWO,
        precision=pyfluent.Precision.DOUBLE,
        ui_mode=FLUENT_UI_MODE,
    )


def main() -> None:
    args = parse_args()
    case_file = args.case_file.expanduser().resolve()
    if not case_file.is_file():
        raise SystemExit(f"Case file does not exist: {case_file}")
    if not case_file.name.endswith(".cas.h5"):
        raise SystemExit("Expected a Fluent .cas.h5 file.")

    data_file = matching_data_file(case_file)
    if not data_file.is_file():
        raise SystemExit(
            "Matching Fluent data file does not exist beside the case file: "
            f"{data_file}"
        )

    try:
        import ansys.fluent.core as pyfluent
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "PyFluent is required for this optional solver-side audit. "
            "Install the pinned requirements-fluent.txt dependency in an "
            "environment that can launch a licensed Fluent 26.1 installation."
        ) from exc

    session = launch_saved_state_session(pyfluent)
    try:
        actual_version = session.get_fluent_version()
        actual_version_text = fluent_version_text(actual_version)
        if actual_version_text != FLUENT_PRODUCT_VERSION:
            raise RuntimeError(
                "Unexpected Fluent version: "
                f"requested {FLUENT_PRODUCT_VERSION}, got {actual_version_text}."
            )

        session.settings.file.read_case_data(file_name=str(case_file))
        computed = session.settings.solution.report_definitions.compute(
            report_defs=list(args.report)
        )
        payload = {
            "case_file": case_file.name,
            "data_file": data_file.name,
            "case_sha256": sha256_file(case_file),
            "data_sha256": sha256_file(data_file),
            "requested_fluent_version": FLUENT_PRODUCT_VERSION,
            "actual_fluent_version": actual_version_text,
            "dimension": "2D",
            "precision": "double",
            "ui_mode": FLUENT_UI_MODE,
            "report_definitions": list(args.report),
            "computed": json_ready(computed),
            "audit_type": "saved-state report recomputation",
        }
        rendered = json.dumps(payload, indent=2, sort_keys=True)
        print(rendered)
        if args.output is not None:
            output = args.output.expanduser().resolve()
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered + "\n", encoding="utf-8")
    finally:
        session.exit()


if __name__ == "__main__":
    main()
