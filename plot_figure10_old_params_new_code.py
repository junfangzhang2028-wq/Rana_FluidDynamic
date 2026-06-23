"""Re-run Figure 10 using legacy iStent inject parameters on the current solver.

This mirrors the commented Figure 10 experiment in
Modified/offline/outputs_trial.py, but it calls the current
Modified/offline/solver.py instead of using the saved legacy CSV files.
"""

from __future__ import annotations

import csv
import contextlib
import io
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
MODIFIED_ROOT = ROOT / "m-johnson2-aqueous-outflow-8fb729748300_Modified"
OUT_DIR = ROOT / "paper_reproduction_outputs" / "figure10_old_params_new_code"

LEGACY_STENT_PARAMS = {
    "name": "iStent inject",
    "length": 145.0,
    "loc_inlet": 75.0,
    "w": 50.0,
    "hd": 50.0,
    "h_after": 150.0,
    "g_inlet": 42.15134797,
    "l_after": 0,
    "l_before": 0,
}
RTM = 6.71
QT = 2.0
PEV = 8.0
START_NODES = np.linspace(50, 250, 10)
N_REPEATS = 2
STENT_SPACING_NODES = 300


def import_current_solver():
    sys.path.insert(0, str(MODIFIED_ROOT))
    os.chdir(str(MODIFIED_ROOT))
    from offline import solver as md  # pylint: disable=import-outside-toplevel

    return md


def solve_iop(md, stents):
    # The solver prints a verbose summary; keep this script output focused.
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        pressure = md.solve(
            qt=QT,
            mode="constant flow",
            geometry="ellipse",
            stents=stents,
            rtm=RTM,
            pev=PEV,
            max_error=1e-4,
        )
    return float(pressure[-1])


def run_sweep(md):
    baseline = solve_iop(md, None)
    arrays = {}
    for count in range(1, 5):
        values = np.zeros((len(START_NODES), N_REPEATS), dtype=float)
        for repeat in range(N_REPEATS):
            for i, start_node in enumerate(START_NODES):
                start = int(start_node)
                stents = [
                    (start + STENT_SPACING_NODES * k, md.Stent(**LEGACY_STENT_PARAMS))
                    for k in range(count)
                ]
                values[i, repeat] = solve_iop(md, stents)
        arrays[count] = values
    return baseline, arrays


def summarize(baseline, arrays):
    rows = [{"label": "Baseline", "count": 0, "mean_iop": baseline, "std_iop": 0.0}]
    for count in range(1, 5):
        values = arrays[count]
        rows.append(
            {
                "label": str(count),
                "count": count,
                "mean_iop": float(np.mean(values)),
                "std_iop": float(np.std(values)),
            }
        )
    return rows


def save_raw_arrays(arrays):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for count, values in arrays.items():
        np.savetxt(OUT_DIR / f"iop_istent_pos{count}_new_code.csv", values, delimiter=",")


def write_summary(rows):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "figure10_old_params_new_code_summary.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["label", "count", "mean_iop", "std_iop"])
        writer.writeheader()
        writer.writerows(rows)
    return path


def plot(rows):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    labels = [row["label"] for row in rows]
    means = np.array([row["mean_iop"] for row in rows], dtype=float)
    stds = np.array([row["std_iop"] for row in rows], dtype=float)
    x = np.arange(len(rows))

    fig, ax = plt.subplots(figsize=(4.1, 5.2), dpi=220)
    ax.bar(x, means, yerr=stds, color="black", edgecolor="black", capsize=3, width=0.58)
    ax.set_ylabel("IOP (mmHg)", fontweight="bold")
    ax.set_xlabel("# of iStent injects", fontweight="bold", labelpad=12)
    ax.set_ylim(0, 30)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontweight="bold")
    ax.set_yticks(np.arange(0, 31, 10))
    ax.set_yticks(np.arange(0, 31, 5), minor=True)
    ax.tick_params(axis="both", which="major", width=1.8, length=6)
    ax.tick_params(axis="y", which="minor", width=1.2, length=3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(1.8)
    ax.spines["bottom"].set_linewidth(1.8)

    caption = (
        "Figure 10 re-run with legacy commented-code iStent inject parameters "
        "on the current finite-inlet solver. Error bars are standard deviations "
        "over the original start-node sweep."
    )
    fig.subplots_adjust(bottom=0.34, left=0.2, right=0.96, top=0.96)
    fig.text(0.02, 0.03, caption, ha="left", va="bottom", fontsize=6.2, wrap=True)

    path = OUT_DIR / "figure10_old_params_new_code.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def main():
    md = import_current_solver()
    baseline, arrays = run_sweep(md)
    rows = summarize(baseline, arrays)
    save_raw_arrays(arrays)
    summary_path = write_summary(rows)
    figure_path = plot(rows)
    print(f"Wrote {figure_path}")
    print(f"Wrote {summary_path}")
    for row in rows:
        print(
            f"{row['label']}: "
            f"{row['mean_iop']:.4f} +/- {row['std_iop']:.4f} mmHg"
        )


if __name__ == "__main__":
    main()
