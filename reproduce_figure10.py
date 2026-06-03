from __future__ import annotations

import contextlib
import csv
import io
import json
import os
import sys
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = Path(__file__).resolve().parent
PROJECT_DIR = REPO_ROOT / "m-johnson2-aqueous-outflow-8fb729748300_Modified"
OUTPUT_DIR = REPO_ROOT / "paper_reproduction_outputs" / "figure10"

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

os.chdir(PROJECT_DIR)

from offline import outputs_trial as ot  # noqa: E402
from offline import solver as md  # noqa: E402


TARGET_BASELINE_IOP = 25.0
QT = 2.0
PEV = 8.0
STENT_SPACING_NODES = 300  # 90 degrees for 1200 SC nodes.
START_NODES = np.linspace(50, 250, 10).astype(int)


def build_istent_inject(ginlet: float) -> md.Stent:
    """iStent inject parameters from Mark's note."""
    return md.Stent(
        name="iStent inject",
        length=230.0,
        loc_inlet=115.0,
        w=50.0,
        hd=50.0,
        h_after=150.0,
        g_inlet=ginlet,
        two_way=True,
        geometry="ellipse",
        l_before=0,
        l_after=0,
    )


def solve_quiet(**kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return ot.solve_cf(**kwargs)


def solve_iop(rtm: float, stents=None) -> float:
    return float(
        solve_quiet(
            qt=QT,
            pev=PEV,
            rtm=rtm,
            stents=stents,
        )["iop"]
    )


def calibrate_rtm(target_iop: float) -> float:
    low = 0.5
    high = 12.0

    for _ in range(24):
        mid = (low + high) / 2.0
        iop = solve_iop(mid)
        if iop < target_iop:
            low = mid
        else:
            high = mid

    return (low + high) / 2.0


def stents_for_count(start_node: int, count: int, ginlet: float):
    stent = build_istent_inject(ginlet)
    return [
        ((start_node + STENT_SPACING_NODES * index) % (md.N * md.M), stent)
        for index in range(count)
    ]


def safe_float_label(value: float) -> str:
    return str(value).replace("-", "m").replace(".", "p")


def run_figure10(ginlet: float = 42.15):
    output_dir = OUTPUT_DIR / f"ginlet_{safe_float_label(ginlet)}"
    output_dir.mkdir(parents=True, exist_ok=True)

    rtm = calibrate_rtm(TARGET_BASELINE_IOP)
    baseline_iop = solve_iop(rtm)

    raw_rows = []
    summary_rows = [
        {
            "condition": "Baseline",
            "stent_count": 0,
            "mean_iop": baseline_iop,
            "std_iop": 0.0,
            "n_positions": 1,
        }
    ]

    means = [baseline_iop]
    stds = [0.0]

    for count in range(1, 5):
        iops = []
        for start_node in START_NODES:
            iop = solve_iop(rtm, stents=stents_for_count(int(start_node), count, ginlet))
            iops.append(iop)
            raw_rows.append(
                {
                    "stent_count": count,
                    "start_node": int(start_node),
                    "start_degrees": float(start_node / (md.N * md.M) * 360.0),
                    "iop": iop,
                }
            )

        mean_iop = float(np.mean(iops))
        std_iop = float(np.std(iops, ddof=1))
        means.append(mean_iop)
        stds.append(std_iop)
        summary_rows.append(
            {
                "condition": str(count),
                "stent_count": count,
                "mean_iop": mean_iop,
                "std_iop": std_iop,
                "n_positions": len(iops),
            }
        )

    raw_csv = output_dir / "figure10_raw_positions.csv"
    with raw_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["stent_count", "start_node", "start_degrees", "iop"])
        writer.writeheader()
        writer.writerows(raw_rows)

    summary_csv = output_dir / "figure10_summary.csv"
    with summary_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["condition", "stent_count", "mean_iop", "std_iop", "n_positions"],
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    metadata = {
        "target_baseline_iop": TARGET_BASELINE_IOP,
        "baseline_iop": baseline_iop,
        "calibrated_rtm": rtm,
        "qt": QT,
        "pev": PEV,
        "stent_spacing_nodes": STENT_SPACING_NODES,
        "stent_spacing_degrees": 90.0,
        "start_nodes": START_NODES.tolist(),
        "stent_parameters": {
            "length_um": 230.0,
            "inlet_location_um": 115.0,
            "height_um": 50.0,
            "width_um": 50.0,
            "post_stent_canal_height_um": 150.0,
            "ginlet": ginlet,
            "bidirectional": True,
            "channel_geometry": "ellipse",
        },
    }
    metadata_json = output_dir / "figure10_metadata.json"
    metadata_json.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    labels = ["Baseline", "1", "2", "3", "4"]
    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(4.8, 6.2))
    ax.bar(x, means, yerr=stds, color="black", edgecolor="black", capsize=3, width=0.36)
    ax.set_ylim(0, 30)
    ax.set_ylabel("IOP (mmHg)", fontsize=14, fontweight="bold")
    ax.set_xlabel("# of iStent injects", fontsize=14, fontweight="bold", labelpad=18)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=12, fontweight="bold")
    ax.tick_params(axis="both", width=2, length=7, labelsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(2.4)
    ax.spines["bottom"].set_linewidth(2.4)
    ax.grid(False)
    fig.tight_layout()

    figure_path = output_dir / "figure10_iStent_inject_count.png"
    fig.savefig(figure_path, dpi=300)
    plt.close(fig)

    return {
        "figure": str(figure_path),
        "summary_csv": str(summary_csv),
        "raw_csv": str(raw_csv),
        "metadata_json": str(metadata_json),
        "summary": summary_rows,
        "metadata": metadata,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reproduce manuscript Figure 10 for iStent inject count.")
    parser.add_argument("--ginlet", type=float, default=42.15, help="Finite inlet conductance to use.")
    args = parser.parse_args()
    result = run_figure10(ginlet=args.ginlet)
    print(json.dumps(result, indent=2))
