"""Reproduce the proposal Figure 13-style stent-location sweep.

The legacy exploratory code lives inside
``m-johnson2-aqueous-outflow-8fb729748300_Modified/offline/outputs_trial.py``.
It saved precomputed sweeps for a single iStent inject placed at different
circumferential positions using even, mouse, and human collector-channel
distributions. This script turns those legacy CSVs into clean figures.
"""

from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
OFFLINE_DIR = ROOT / "m-johnson2-aqueous-outflow-8fb729748300_Modified" / "offline"
OUT_DIR = ROOT / "paper_reproduction_outputs" / "figure13_proposal"

BASELINE_IOP = 25.0
EVEN_REFERENCE_IOP = 18.04
KERNEL_SIZE = 3

DATASETS = {
    "Mouse digital-twin CC distribution": {
        "csv": "iop_inject_pos_mouse.csv",
        "color": "#1f77b4",
    },
    "Human donor CC distribution": {
        "csv": "iop_inject_pos_human.csv",
        "color": "#d62728",
    },
    "Even CC distribution": {
        "csv": "iop_inject_poseven.csv",
        "color": "#2ca02c",
    },
}


def smooth_circular(values, kernel_size=KERNEL_SIZE):
    """Match the circular moving-average smoothing used in outputs_trial.py."""
    kernel = np.ones(kernel_size, dtype=float) / kernel_size
    circular = np.insert(values, 0, values[-1])
    circular = np.append(circular, values[0])
    return np.convolve(circular, kernel, mode="valid")


def load_dataset(csv_name):
    path = OFFLINE_DIR / csv_name
    data = np.genfromtxt(str(path), delimiter=",")
    if data.ndim != 2:
        raise ValueError("Expected a 2D CSV for {0}, got shape {1}".format(path, data.shape))

    mean_iop = data[:, :10].mean(axis=1)
    smoothed_iop = smooth_circular(mean_iop)
    stent_nodes = np.linspace(0, 1180, data.shape[0])
    degrees = stent_nodes / 50.0 * 360.0 / 24.0
    reduction = BASELINE_IOP - smoothed_iop
    return degrees, smoothed_iop, reduction, data


def load_cc_nodes():
    # These arrays are copied from the legacy Figure 13-like block in outputs_trial.py.
    ccs_mouse = np.array([
        1069, 1091, 1115, 1150, 1163, 1189, 3, 13, 50, 116, 124, 149,
        189, 314, 387, 411, 445, 471, 496, 505, 533, 555, 575, 603,
        639, 659, 683, 713, 726, 762, 798, 853, 922, 947,
    ])
    ccs_human = np.array([
        1, 46, 95, 170, 264, 348, 374, 383, 408, 486, 518, 542, 636,
        672, 681, 709, 717, 763, 779, 812, 822, 830, 963, 999, 1081,
        1092, 1100, 1129, 1144,
    ])
    return {
        "Mouse digital-twin CC distribution": ccs_mouse,
        "Human donor CC distribution": ccs_human,
    }


def nodes_to_degrees(nodes):
    return nodes / 50.0 * 360.0 / 24.0


def style_axes(ax):
    ax.set_xlim(-5, 360)
    ax.set_xticks(np.arange(0, 361, 60))
    ax.grid(True, color="#d8d8d8", linewidth=0.8, alpha=0.75)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_iop(results):
    fig, ax = plt.subplots(figsize=(9.5, 5.3), dpi=160)
    for label, res in results.items():
        ax.plot(res["degrees"], res["iop"], linewidth=2.2, color=res["color"], label=label)

    ax.axhline(BASELINE_IOP, color="black", linewidth=1.4, linestyle="--", label="Baseline IOP = 25 mmHg")
    ax.axhline(EVEN_REFERENCE_IOP, color="#2ca02c", linewidth=1.2, linestyle=":", label="Even-distribution reference")

    cc_nodes = load_cc_nodes()
    for label, nodes in cc_nodes.items():
        color = results[label]["color"]
        for deg in nodes_to_degrees(nodes):
            ax.axvline(deg, ymin=0.0, ymax=0.08, color=color, alpha=0.55, linewidth=1.0)

    style_axes(ax)
    ax.set_ylim(10, 30)
    ax.set_title("Proposal Figure 13 Reproduction: IOP vs Stent Placement")
    ax.set_xlabel("Degree (stent placement)")
    ax.set_ylabel("Post-stent IOP (mmHg)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "figure13_iop_vs_stent_placement.png")
    plt.close(fig)


def plot_reduction(results):
    fig, ax = plt.subplots(figsize=(9.5, 5.3), dpi=160)
    for label, res in results.items():
        ax.plot(res["degrees"], res["reduction"], linewidth=2.2, color=res["color"], label=label)

    cc_nodes = load_cc_nodes()
    for label, nodes in cc_nodes.items():
        color = results[label]["color"]
        for deg in nodes_to_degrees(nodes):
            ax.axvline(deg, ymin=0.0, ymax=0.08, color=color, alpha=0.55, linewidth=1.0)

    style_axes(ax)
    ax.set_ylim(0, 12)
    ax.set_title("Proposal Figure 13 Reproduction: IOP Reduction vs Stent Placement")
    ax.set_xlabel("Degree (stent placement)")
    ax.set_ylabel("IOP reduction from 25 mmHg baseline (mmHg)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "figure13_iop_reduction_vs_stent_placement.png")
    plt.close(fig)


def write_summary(results):
    rows = []
    for label, res in results.items():
        iop = res["iop"]
        reduction = res["reduction"]
        rows.append({
            "dataset": label,
            "source_csv": res["csv"],
            "min_iop": np.min(iop),
            "mean_iop": np.mean(iop),
            "max_iop": np.max(iop),
            "min_reduction": np.min(reduction),
            "mean_reduction": np.mean(reduction),
            "max_reduction": np.max(reduction),
            "reduction_range": np.max(reduction) - np.min(reduction),
        })

    summary = pd.DataFrame(rows)
    summary.to_csv(OUT_DIR / "figure13_summary.csv", index=False)
    return summary


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    for label, meta in DATASETS.items():
        degrees, iop, reduction, raw = load_dataset(meta["csv"])
        results[label] = {
            "csv": meta["csv"],
            "color": meta["color"],
            "degrees": degrees,
            "iop": iop,
            "reduction": reduction,
            "raw_shape": raw.shape,
        }

    plot_iop(results)
    plot_reduction(results)
    summary = write_summary(results)

    print("Wrote outputs to {0}".format(OUT_DIR))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
