from __future__ import annotations

import argparse
import json
import os
import sys
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List

import matplotlib


matplotlib.use("Agg")
import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parent
PROJECT_DIR = REPO_ROOT / "m-johnson2-aqueous-outflow-8fb729748300_Modified"

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

os.chdir(PROJECT_DIR)

import offline.outputs_trial as ot
import offline.solver as md


def round_float(value: Any, digits: int = 6) -> Any:
    if isinstance(value, float):
        return round(value, digits)
    return value


def simplify_solution(solution: Dict[str, Any]) -> Dict[str, Any]:
    keys = ("iop", "flowrate", "resistance", "facility")
    return {key: round_float(float(solution[key])) for key in keys if key in solution}


def ensure_output_dirs(base_dir: Path) -> Dict[str, Path]:
    figures_dir = base_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    return {"base": base_dir, "figures": figures_dir}


def save_current_figure(figures_dir: Path, stem: str, dpi: int) -> str | None:
    fig_numbers = plt.get_fignums()
    if not fig_numbers:
        return None

    fig = plt.figure(fig_numbers[-1])
    with suppress(Exception):
        fig.tight_layout()

    output_path = figures_dir / f"{stem}.png"
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    return str(output_path)


def run_plot_task(
    label: str,
    stem: str,
    figures_dir: Path,
    dpi: int,
    task: Callable[[], Any],
) -> Dict[str, Any]:
    plt.close("all")
    try:
        result = task()
        figure_path = save_current_figure(figures_dir, stem, dpi)
        return {
            "status": "ok",
            "label": label,
            "figure": figure_path,
            "result": simplify_solution(result) if isinstance(result, dict) else None,
        }
    except Exception as exc:
        return {
            "status": "failed",
            "label": label,
            "figure": None,
            "error": str(exc),
        }
    finally:
        plt.close("all")


def run_metric_task(label: str, task: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
    try:
        result = task()
        return {
            "status": "ok",
            "label": label,
            "result": simplify_solution(result),
        }
    except Exception as exc:
        return {
            "status": "failed",
            "label": label,
            "error": str(exc),
        }


def build_istent() -> md.Stent:
    return md.Stent(
        name="iStent (R)",
        length=1000.0,
        loc_inlet=0.0,
        w=120.0,
        hd=60.0,
        two_way=True,
        l_before=0,
        l_after=0,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the currently reproducible core paper/model figures and cases."
    )
    parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / "paper_reproduction_outputs"),
        help="Directory to store figures and summary files.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="DPI to use when saving figures.",
    )
    args = parser.parse_args()

    output_dirs = ensure_output_dirs(Path(args.output_dir))
    figures_dir = output_dirs["figures"]

    summary: Dict[str, Any] = {
        "generated_at": datetime.now().isoformat(),
        "project_dir": str(PROJECT_DIR),
        "output_dir": str(output_dirs["base"]),
        "notes": [
            "This script uses offline.outputs_trial because offline.outputs depends on missing ComparisonData files.",
            "Tasks are best-effort: failures are recorded in the summary instead of stopping the whole run.",
        ],
        "metrics": {},
        "plots": {},
    }

    baseline_cp7 = run_metric_task(
        "baseline_constant_pressure_iop7",
        lambda: ot.solve_cp(iop=7.0),
    )
    summary["metrics"]["baseline_constant_pressure_iop7"] = baseline_cp7

    baseline_cf = run_metric_task(
        "baseline_constant_flow_qt2_pev8",
        lambda: ot.solve_cf(qt=2.0, pev=8.0),
    )
    summary["metrics"]["baseline_constant_flow_qt2_pev8"] = baseline_cf

    summary["metrics"]["trabeculotomy_1h_iop7"] = run_metric_task(
        "trabeculotomy_1h_iop7",
        lambda: ot.solve_trabeculotomy(
            iop=7.0, hours=1, mode="constant pressure", show_height=False
        ),
    )
    summary["metrics"]["trabeculotomy_4h_iop7"] = run_metric_task(
        "trabeculotomy_4h_iop7",
        lambda: ot.solve_trabeculotomy(
            iop=7.0, hours=4, mode="constant pressure", show_height=False
        ),
    )
    summary["metrics"]["trabeculotomy_12h_iop7"] = run_metric_task(
        "trabeculotomy_12h_iop7",
        lambda: ot.solve_trabeculotomy(
            iop=7.0, hours=12, mode="constant pressure", show_height=False
        ),
    )
    summary["metrics"]["yag_2holes_qt2"] = run_metric_task(
        "yag_2holes_qt2",
        lambda: ot.solve_yag_holes(qt=2.0, n=2, mode="constant flow"),
    )
    summary["metrics"]["istent_single_qt2_pev8"] = run_metric_task(
        "istent_single_qt2_pev8",
        lambda: ot.solve_cf(qt=2.0, pev=8.0, stents=[(0, build_istent())]),
    )

    plot_tasks = [
        (
            "baseline_pr_curve",
            "01_baseline_pr_curve",
            lambda: ot.plot_pr_curve(),
        ),
        (
            "baseline_pr_curve_normalized",
            "02_baseline_pr_curve_normalized",
            lambda: ot.plot_pr_curve(normalized=True),
        ),
        (
            "baseline_pressure_distribution",
            "03_baseline_pressure_distribution",
            lambda: ot.plot_pressure_dist(iop=7.0, mode="constant pressure"),
        ),
        (
            "baseline_height_distribution",
            "04_baseline_height_distribution",
            lambda: ot.plot_height_dist(iop=7.0, show_p=False),
        ),
        (
            "baseline_collector_channel_flow",
            "05_baseline_collector_channel_flow",
            lambda: ot.plot_jcc(iop=7.0, mode="constant pressure"),
        ),
        (
            "trabeculotomy_facility_change_iop7",
            "06_trabeculotomy_facility_change_iop7",
            lambda: ot.plot_dc_trab(iop=7),
        ),
        (
            "yag_holes_iop_effect",
            "07_yag_holes_iop_effect",
            lambda: ot.plot_iop_change_yag(qt=2.0),
        ),
        (
            "nonuniform_cc_pr_curve",
            "08_nonuniform_cc_pr_curve",
            lambda: ot.plot_pr_curve_nonuniform(),
        ),
        (
            "weak_tm_nonuniform_effect",
            "09_weak_tm_nonuniform_effect",
            lambda: ot.plot_weak_tm_nonuniform(),
        ),
        (
            "istent_pressure_distribution",
            "10_istent_pressure_distribution",
            lambda: ot.plot_pressure_dist(
                qt=2.0,
                mode="constant flow",
                pev=8.0,
                stents=[(0, build_istent())],
            ),
        ),
        (
            "istent_height_distribution",
            "11_istent_height_distribution",
            lambda: ot.plot_height_dist(
                qt=2.0,
                mode="constant flow",
                show_p=False,
                pev=8.0,
                stents=[(0, build_istent())],
            ),
        ),
        (
            "istent_collector_channel_flow",
            "12_istent_collector_channel_flow",
            lambda: ot.plot_jcc(
                qt=2.0,
                mode="constant flow",
                pev=8.0,
                stents=[(0, build_istent())],
            ),
        ),
    ]

    for label, stem, task in plot_tasks:
        summary["plots"][label] = run_plot_task(
            label=label,
            stem=stem,
            figures_dir=figures_dir,
            dpi=args.dpi,
            task=task,
        )

    ok_plot_count = sum(
        1 for value in summary["plots"].values() if value.get("status") == "ok"
    )
    failed_plot_count = sum(
        1 for value in summary["plots"].values() if value.get("status") == "failed"
    )
    ok_metric_count = sum(
        1 for value in summary["metrics"].values() if value.get("status") == "ok"
    )
    failed_metric_count = sum(
        1 for value in summary["metrics"].values() if value.get("status") == "failed"
    )

    summary["counts"] = {
        "ok_plots": ok_plot_count,
        "failed_plots": failed_plot_count,
        "ok_metrics": ok_metric_count,
        "failed_metrics": failed_metric_count,
    }

    summary_path = output_dirs["base"] / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Saved summary to: {summary_path}")
    print(f"Saved figures to: {figures_dir}")
    print(json.dumps(summary["counts"], indent=2))


if __name__ == "__main__":
    main()
