from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "scripts/geometry/build_periodic_passage.py",
    "scripts/postprocess/analyze_convergence.py",
    "scripts/postprocess/analyze_residuals.py",
    "scripts/postprocess/analyze_transition_sst.py",
    "scripts/postprocess/reconstruct_temperature_gradient.py",
    "scripts/postprocess/analyze_mesh_sensitivity.py",
    "scripts/postprocess/plot_mesh_quality_distribution.py",
    "scripts/postprocess/crop_flow_field_figures.py",
    "scripts/postprocess/build_comparison_profiles.py",
    "scripts/verification/check_mesh_summary.py",
    "scripts/verification/check_global_balances.py",
    "scripts/verification/check_sensitivity_studies.py",
    "scripts/verification/plot_wall_yplus.py",
    "scripts/comparison/compare_run145.py",
]

def main() -> None:
    for script in SCRIPTS:
        print(f"Running {script}", flush=True)
        subprocess.run([sys.executable, script], cwd=ROOT, check=True)
    print(f"Completed {len(SCRIPTS)} analysis and verification stages.")

if __name__ == "__main__":
    main()
