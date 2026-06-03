from __future__ import annotations

import contextlib
import csv
import io
import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = Path(__file__).resolve().parent
PROJECT_DIR = REPO_ROOT / "m-johnson2-aqueous-outflow-8fb729748300_Modified"
OUTPUT_DIR = REPO_ROOT / "paper_reproduction_outputs" / "figure10" / "legacy_bug"

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

os.chdir(PROJECT_DIR)

from offline import outputs_trial as ot  # noqa: E402
from offline import solver as md  # noqa: E402


TARGET_BASELINE_IOP = 25.0
QT = 2.0
PEV = 8.0
STENT_SPACING_NODES = 300

# With Mark's loc_inlet=115 um, the inlet discretizes to index 3.
# These starts deliberately sweep the inlet across a collector channel at node 40.
START_NODES = np.arange(34, 42)


def solve_quiet(**kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return ot.solve_cf(**kwargs)


def solve_iop(rtm: float, stents=None) -> float:
    return float(solve_quiet(qt=QT, pev=PEV, rtm=rtm, stents=stents)["iop"])


def calibrate_rtm(target_iop: float) -> float:
    low = 0.5
    high = 12.0
    for _ in range(24):
        mid = (low + high) / 2.0
        if solve_iop(mid) < target_iop:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def build_stent(ginlet: float) -> md.Stent:
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


def stents_for_count(start_node: int, count: int, ginlet: float):
    stent = build_stent(ginlet)
    return [
        ((start_node + STENT_SPACING_NODES * index) % (md.N * md.M), stent)
        for index in range(count)
    ]


def compute_series(rtm: float, ginlet: float):
    rows = []
    means = []
    stds = []
    for count in range(1, 5):
        iops = []
        for start_node in START_NODES:
            iop = solve_iop(rtm, stents_for_count(int(start_node), count, ginlet))
            iops.append(iop)
            rows.append(
                {
                    "ginlet": ginlet,
                    "stent_count": count,
                    "start_node": int(start_node),
                    "inlet_node": int(start_node + int(115.0 / md.dx)),
                    "iop": iop,
                }
            )
        means.append(float(np.mean(iops)))
        stds.append(float(np.std(iops, ddof=1)))
    return means, stds, rows


def label_bars(ax, xs, means, stds):
    for x, mean, std in zip(xs, means, stds):
        ax.text(
            x,
            mean + std + 0.35,
            f"{mean:.2f}\n±{std:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )


def plot_single(baseline_iop: float, legacy_means, legacy_stds, output_path: Path):
    labels = ["Baseline", "1", "2", "3", "4"]
    means = [baseline_iop] + legacy_means
    stds = [0.0] + legacy_stds
    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(5.2, 6.4))
    ax.bar(x, means, yerr=stds, color="black", edgecolor="black", capsize=4, width=0.38)
    label_bars(ax, x[1:], legacy_means, legacy_stds)
    ax.set_ylim(0, 30)
    ax.set_ylabel("IOP (mmHg)", fontsize=14, fontweight="bold")
    ax.set_xlabel("# of iStent injects", fontsize=14, fontweight="bold", labelpad=18)
    ax.set_title("Legacy bug mode: ideal inlet / CC-overlap sweep", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=12, fontweight="bold")
    ax.tick_params(axis="both", width=2, length=7, labelsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(2.4)
    ax.spines["bottom"].set_linewidth(2.4)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def plot_comparison(baseline_iop: float, legacy, fixed, output_path: Path):
    counts = np.arange(1, 5)
    width = 0.34
    fig, ax = plt.subplots(figsize=(7.0, 5.6))
    ax.axhline(baseline_iop, color="#777777", linewidth=1.4, linestyle="--", label="Baseline 25 mmHg")
    ax.bar(
        counts - width / 2,
        legacy[0],
        yerr=legacy[1],
        width=width,
        color="black",
        edgecolor="black",
        capsize=4,
        label="Legacy bug (Ginlet=0 ideal inlet)",
    )
    ax.bar(
        counts + width / 2,
        fixed[0],
        yerr=fixed[1],
        width=width,
        color="#2f8f83",
        edgecolor="#1d5f57",
        capsize=4,
        label="Fixed finite inlet (Ginlet=0.3)",
    )
    label_bars(ax, counts - width / 2, legacy[0], legacy[1])
    label_bars(ax, counts + width / 2, fixed[0], fixed[1])
    ax.set_ylim(0, 30)
    ax.set_ylabel("IOP (mmHg)", fontsize=13, fontweight="bold")
    ax.set_xlabel("# of iStent injects", fontsize=13, fontweight="bold")
    ax.set_xticks(counts)
    ax.set_xticklabels([str(value) for value in counts], fontsize=11, fontweight="bold")
    ax.legend(frameon=False, fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rtm = calibrate_rtm(TARGET_BASELINE_IOP)
    baseline_iop = solve_iop(rtm)

    legacy_means, legacy_stds, legacy_rows = compute_series(rtm=rtm, ginlet=0.0)
    fixed_means, fixed_stds, fixed_rows = compute_series(rtm=rtm, ginlet=0.3)

    raw_csv = OUTPUT_DIR / "legacy_vs_fixed_raw.csv"
    with raw_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["ginlet", "stent_count", "start_node", "inlet_node", "iop"])
        writer.writeheader()
        writer.writerows(legacy_rows + fixed_rows)

    summary = {
        "baseline_iop": baseline_iop,
        "calibrated_rtm": rtm,
        "start_nodes": START_NODES.tolist(),
        "legacy_bug_ginlet_0": [
            {"stent_count": count, "mean_iop": mean, "std_iop": std}
            for count, mean, std in zip(range(1, 5), legacy_means, legacy_stds)
        ],
        "fixed_ginlet_0p3": [
            {"stent_count": count, "mean_iop": mean, "std_iop": std}
            for count, mean, std in zip(range(1, 5), fixed_means, fixed_stds)
        ],
    }
    summary_json = OUTPUT_DIR / "legacy_vs_fixed_summary.json"
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    legacy_figure = OUTPUT_DIR / "figure10_legacy_bug_std.png"
    comparison_figure = OUTPUT_DIR / "figure10_legacy_bug_vs_fixed_std.png"
    plot_single(baseline_iop, legacy_means, legacy_stds, legacy_figure)
    plot_comparison(baseline_iop, (legacy_means, legacy_stds), (fixed_means, fixed_stds), comparison_figure)

    result = {
        "legacy_figure": str(legacy_figure),
        "comparison_figure": str(comparison_figure),
        "raw_csv": str(raw_csv),
        "summary_json": str(summary_json),
        "summary": summary,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
