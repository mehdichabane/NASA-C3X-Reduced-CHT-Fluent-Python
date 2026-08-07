from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "geometry/spaceclaim_imports/c3x_periodic_passage_boundary_mm.txt"

PITCH_MM = 117.730
X_INLET_MM = -58.574
X_OUTLET_MM = 195.401
Y_UPPER_INLET_MM = 283.7248
Y_LOWER_OUTLET_MM = -203.1280


def passage_points() -> list[tuple[float, float]]:
    y_lower_inlet = Y_UPPER_INLET_MM - PITCH_MM
    y_upper_outlet = Y_LOWER_OUTLET_MM + PITCH_MM
    return [
        (X_INLET_MM, Y_UPPER_INLET_MM),
        (X_OUTLET_MM, y_upper_outlet),
        (X_OUTLET_MM, Y_LOWER_OUTLET_MM),
        (X_INLET_MM, y_lower_inlet),
        (X_INLET_MM, Y_UPPER_INLET_MM),
    ]


def main() -> None:
    points = passage_points()
    inlet_pitch = points[0][1] - points[3][1]
    outlet_pitch = points[1][1] - points[2][1]

    if abs(inlet_pitch - PITCH_MM) > 1e-9 or abs(outlet_pitch - PITCH_MM) > 1e-9:
        raise RuntimeError("The periodic boundaries do not preserve the pitch.")

    lines = ["3d=false", "polyline=true", "fit=false"]
    lines.extend(f"0,{x:.9f},{y:.9f}" for x, y in points)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="ascii")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
