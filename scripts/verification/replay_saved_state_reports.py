from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_REPORTS = (
    "fine_external_heat_rate",
    "fine_wall_temperature_avg",
    "fine_mach_outlet",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Open a saved Fluent case/data pair through PyFluent and recompute "
            "existing scalar report definitions. This is a saved-state audit, "
            "not a replay from initialization."
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


def main() -> None:
    args = parse_args()
    case_file = args.case_file.expanduser().resolve()
    if not case_file.is_file():
        raise SystemExit(f"Case file does not exist: {case_file}")
    if not case_file.name.endswith(".cas.h5"):
        raise SystemExit("Expected a Fluent .cas.h5 file.")

    try:
        import ansys.fluent.core as pyfluent
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "PyFluent is required for this optional solver-side audit. "
            "Install ansys-fluent-core in an environment that can launch a "
            "licensed Fluent installation."
        ) from exc

    session = pyfluent.launch_fluent()
    try:
        session.settings.file.read_case_data(file_name=str(case_file))
        computed = session.settings.solution.report_definitions.compute(
            report_defs=list(args.report)
        )
        payload = {
            "case_file": str(case_file),
            "report_definitions": list(args.report),
            "computed": json_ready(computed),
            "scope": (
                "saved-state report recomputation only; no initialization, "
                "iteration replay, mesh regeneration or equivalence claim"
            ),
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
