"""Create compact presentation figures from direct Fluent contour exports."""
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "data/fluent_exports/figure_sources"
FLOW_OUTPUT_DIR = ROOT / "results/figures/flow_fields"
SOLID_OUTPUT_DIR = ROOT / "results/figures/solid_temperature"

FLOW_CASES = {
    "absolute_pressure": (
        SOURCE_DIR / "run145_sst_absolute_pressure_contour_fluent_raw.png",
        FLOW_OUTPUT_DIR / "run145_sst_absolute_pressure_contour.png",
    ),
    "mach": (
        SOURCE_DIR / "run145_sst_mach_contour_fluent_raw.png",
        FLOW_OUTPUT_DIR / "run145_sst_mach_contour.png",
    ),
}
SOLID_SOURCE = SOURCE_DIR / "run145_sst_solid_temperature_contour_fluent_raw.png"
SOLID_OUTPUT = SOLID_OUTPUT_DIR / "run145_sst_solid_temperature_contour_fluent.png"


def crop_fraction(image, left: float, top: float, right: float, bottom: float):
    height, width = image.shape[:2]
    return image[
        int(top * height) : int(bottom * height),
        int(left * width) : int(right * width),
    ]


def label_boundaries(axis: plt.Axes) -> None:
    axis.text(0.04, 0.88, "inlet", transform=axis.transAxes, fontsize=8.5)
    axis.text(0.73, 0.07, "outlet", transform=axis.transAxes, fontsize=8.5)
    axis.annotate(
        "",
        xy=(0.58, 0.40),
        xytext=(0.25, 0.70),
        xycoords="axes fraction",
        arrowprops={"arrowstyle": "->", "linewidth": 1.0, "color": "0.15"},
    )


def render_flow(source: Path, output: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    image = mpimg.imread(source)
    legend = crop_fraction(image, 0.015, 0.16, 0.19, 0.82)
    field = crop_fraction(image, 0.35, 0.045, 0.66, 0.965)

    figure, (legend_axis, field_axis) = plt.subplots(
        1,
        2,
        figsize=(5.5, 5.4),
        gridspec_kw={"width_ratios": (0.78, 1.55)},
        layout="constrained",
    )
    legend_axis.imshow(legend)
    legend_axis.axis("off")
    field_axis.imshow(field)
    field_axis.axis("off")
    label_boundaries(field_axis)

    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220)
    plt.close(figure)


def render_solid(source: Path, output: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    image = mpimg.imread(source)
    legend = crop_fraction(image, 0.015, 0.16, 0.19, 0.82)
    field = crop_fraction(image, 0.35, 0.045, 0.66, 0.96)

    figure, (legend_axis, field_axis) = plt.subplots(
        1,
        2,
        figsize=(5.2, 5.6),
        gridspec_kw={"width_ratios": (0.78, 1.42)},
        layout="constrained",
    )
    legend_axis.imshow(legend)
    legend_axis.axis("off")
    field_axis.imshow(field)
    field_axis.axis("off")

    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220)
    plt.close(figure)


def main() -> None:
    for source, output in FLOW_CASES.values():
        render_flow(source, output)
        print(f"Wrote {output}")
    render_solid(SOLID_SOURCE, SOLID_OUTPUT)
    print(f"Wrote {SOLID_OUTPUT}")


if __name__ == "__main__":
    main()
