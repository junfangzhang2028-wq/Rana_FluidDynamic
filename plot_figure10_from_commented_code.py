"""Plot manuscript Figure 10 from the legacy commented iStent inject data.

The original project keeps the Figure 10 workflow as a commented experiment in
Modified/offline/outputs_trial.py. That block generated iop_istent_pos1.csv
through iop_istent_pos4.csv for one to four iStent injects placed 90 degrees
apart. This script turns those saved arrays into a clean, reproducible figure.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
LEGACY_DATA_DIR = (
    ROOT
    / "m-johnson2-aqueous-outflow-8fb729748300_Modified"
    / "offline"
)
OUT_DIR = ROOT / "paper_reproduction_outputs" / "figure10_commented_code"


def load_legacy_iop_arrays() -> list[np.ndarray]:
    arrays = []
    for count in range(1, 5):
        path = LEGACY_DATA_DIR / f"iop_istent_pos{count}.csv"
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {path}. This file is produced by the commented "
                "Figure 10 block in Modified/offline/outputs_trial.py."
            )
        arrays.append(np.genfromtxt(path, delimiter=",", dtype=float))
    return arrays


def summarize(arrays: list[np.ndarray]) -> list[dict[str, float]]:
    rows = [{"label": "Baseline", "count": 0, "mean_iop": 25.0, "std_iop": 0.0}]
    for count, values in enumerate(arrays, start=1):
        rows.append(
            {
                "label": str(count),
                "count": count,
                "mean_iop": float(np.mean(values)),
                "std_iop": float(np.std(values)),
            }
        )
    return rows


def write_summary(rows: list[dict[str, float]]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "figure10_commented_code_summary.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["label", "count", "mean_iop", "std_iop"])
        writer.writeheader()
        writer.writerows(rows)
    return path


def plot(rows: list[dict[str, float]]) -> Path:
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
        "Figure 10. Comparison of predicted IOP using one, two, three, and four "
        "iStent injects inserted into Schlemm canal 90 degrees apart, from a "
        "baseline pressure of 25 mm Hg. Error bars are standard deviations."
    )
    fig.subplots_adjust(bottom=0.34, left=0.2, right=0.96, top=0.96)
    fig.text(0.02, 0.03, caption, ha="left", va="bottom", fontsize=6.2, wrap=True)

    path = OUT_DIR / "figure10_commented_code.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def main() -> None:
    arrays = load_legacy_iop_arrays()
    rows = summarize(arrays)
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
