"""Recompute proposal Figure 13 with the old and current solvers.

This script uses the parameters recovered from the legacy block in
``Modified/offline/outputs_trial.py``:

* iStent inject: length 145 um, inlet 75 um, 50x50 um channel,
  post-stent canal height 150 um, Ginlet 42.15134797.
* constant flow: Qt = 2.0 uL/min, Pev = 8.0 mmHg.
* three collector-channel layouts: even, mouse digital-twin, and human donor.

It recomputes the stent-location sweep with both the original solver and the
current modified solver, then compares those results to the historical CSVs
that were likely used for the proposal figure.
"""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import importlib
import sys

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
ORIGINAL_ROOT = ROOT / "m-johnson2-aqueous-outflow-8fb729748300_Original"
MODIFIED_ROOT = ROOT / "m-johnson2-aqueous-outflow-8fb729748300_Modified"
OFFLINE_DIR = MODIFIED_ROOT / "offline"
OUT_DIR = ROOT / "paper_reproduction_outputs" / "figure13_old_new_recomputed"

BASELINE_IOP = 25.0
PROPOSAL_MIN_REDUCTION = 4.2
PROPOSAL_MAX_REDUCTION = 10.0
KERNEL_SIZE = 3


CCS_EVEN = np.array([
    (0, 1.0), (40, 1.0), (80, 1.0), (120, 1.0), (160, 1.0), (200, 1.0),
    (240, 1.0), (280, 1.0), (320, 1.0), (360, 1.0), (400, 1.0),
    (440, 1.0), (480, 1.0), (520, 1.0), (560, 1.0), (600, 1.0),
    (640, 1.0), (680, 1.0), (720, 1.0), (760, 1.0), (800, 1.0),
    (840, 1.0), (880, 1.0), (920, 1.0), (960, 1.0), (1000, 1.0),
    (1040, 1.0), (1080, 1.0), (1120, 1.0), (1160, 1.0),
], dtype=float)

CCS_MOUSE = np.array([
    (1069, 1.0), (1091, 1.0), (1115, 1.0), (1150, 1.0), (1163, 1.0),
    (1189, 1.0), (3, 1.0), (13, 1.0), (50, 1.0), (116, 1.0),
    (124, 10.0), (149, 1.0), (189, 1.0), (314, 1.0), (387, 1.0),
    (411, 1.0), (445, 1.0), (471, 10.0), (496, 1.0), (505, 1.0),
    (533, 1.0), (555, 1.0), (575, 1.0), (603, 1.0), (639, 1.0),
    (659, 1.0), (683, 1.0), (713, 1.0), (726, 1.0), (762, 1.0),
    (798, 1.0), (853, 1.0), (922, 1.0), (947, 1.0),
], dtype=float)

CCS_HUMAN = np.array([
    (1, 1.0), (46, 1.0), (95, 1.0), (170, 1.0), (264, 1.0),
    (348, 1.0), (374, 1.0), (383, 1.0), (408, 1.0), (486, 1.0),
    (518, 10.0), (542, 1.0), (636, 1.0), (672, 1.0), (681, 1.0),
    (709, 1.0), (717, 1.0), (763, 10.0), (779, 1.0), (812, 1.0),
    (822, 1.0), (830, 1.0), (963, 1.0), (999, 1.0), (1081, 1.0),
    (1092, 1.0), (1100, 1.0), (1129, 1.0), (1144, 1.0),
], dtype=float)

DATASETS = {
    "even": {
        "label": "Even CC distribution",
        "ccs": CCS_EVEN,
        # The legacy save block used cases["No Surgery (iStent)"] for
        # iop_inject_poseven.csv, not cases["No Surgery (iStent inject2)"].
        "rtm": 6.33,
        "historical_csv": "iop_inject_poseven.csv",
        "cache_csv": "even_rtm6p33.csv",
    },
    "mouse": {
        "label": "Mouse digital-twin CC distribution",
        "ccs": CCS_MOUSE,
        "rtm": 5.558,
        "historical_csv": "iop_inject_pos_mouse.csv",
        "cache_csv": "mouse.csv",
    },
    "human": {
        "label": "Human donor CC distribution",
        "ccs": CCS_HUMAN,
        "rtm": 5.226,
        "historical_csv": "iop_inject_pos_human.csv",
        "cache_csv": "human.csv",
    },
}

SOLVERS = {
    "old_solver": {
        "label": "Old solver",
        "root": ORIGINAL_ROOT,
        "color": "#4d4d4d",
    },
    "current_solver": {
        "label": "Current solver",
        "root": MODIFIED_ROOT,
        "color": "#d62728",
    },
}


def import_solver(project_root):
    for name in list(sys.modules):
        if name == "offline" or name.startswith("offline."):
            del sys.modules[name]
    sys.path.insert(0, str(project_root))
    try:
        return importlib.import_module("offline.solver")
    finally:
        sys.path.remove(str(project_root))


def make_stent(md):
    return md.Stent(
        name="iStent inject",
        length=145.0,
        loc_inlet=75.0,
        w=50.0,
        hd=50.0,
        h_after=150,
        g_inlet=42.15134797,
        l_after=0,
        l_before=0,
    )


def solve_iop(md, stent, loc, dataset):
    with redirect_stdout(StringIO()):
        pressure = md.solve(
            qt=2.0,
            mode="constant flow",
            pev=8.0,
            rtm=dataset["rtm"],
            ccs=dataset["ccs"],
            stents=[(int(loc), stent)],
        )
    return float(pressure[-1])


def recompute_solver_dataset(solver_key, dataset_key):
    csv_path = OUT_DIR / "raw_arrays" / solver_key / DATASETS[dataset_key]["cache_csv"]
    if csv_path.exists():
        return np.genfromtxt(str(csv_path), delimiter=",")

    md = import_solver(SOLVERS[solver_key]["root"])
    stent = make_stent(md)
    locs = np.linspace(0, 1180, 60)
    values = np.zeros((len(locs), 10), dtype=float)

    for i, loc in enumerate(locs):
        iop = solve_iop(md, stent, loc, DATASETS[dataset_key])
        values[i, :] = iop
        print("{0} {1}: {2:02d}/{3} loc={4:.1f} IOP={5:.6f}".format(
            solver_key, dataset_key, i + 1, len(locs), loc, iop
        ))

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(str(csv_path), values, delimiter=",")
    return values


def load_historical(dataset_key):
    return np.genfromtxt(str(OFFLINE_DIR / DATASETS[dataset_key]["historical_csv"]), delimiter=",")


def smooth_circular(values):
    kernel = np.ones(KERNEL_SIZE, dtype=float) / KERNEL_SIZE
    circular = np.insert(values, 0, values[-1])
    circular = np.append(circular, values[0])
    return np.convolve(circular, kernel, mode="valid")


def processed_iop(raw):
    return smooth_circular(raw[:, :10].mean(axis=1))


def degrees_for(raw):
    locs = np.linspace(0, 1180, raw.shape[0])
    return locs / 50.0 * 360.0 / 24.0


def write_summary(all_results):
    rows = []
    for dataset_key, variants in all_results.items():
        hist_iop = variants["historical_csv"]["iop"]
        hist_reduction = BASELINE_IOP - hist_iop
        for variant_key, result in variants.items():
            iop = result["iop"]
            reduction = BASELINE_IOP - iop
            rows.append({
                "dataset": DATASETS[dataset_key]["label"],
                "variant": result["label"],
                "rtm": DATASETS[dataset_key]["rtm"],
                "min_iop": np.min(iop),
                "mean_iop": np.mean(iop),
                "max_iop": np.max(iop),
                "min_reduction": np.min(reduction),
                "mean_reduction": np.mean(reduction),
                "max_reduction": np.max(reduction),
                "reduction_range": np.max(reduction) - np.min(reduction),
                "max_abs_iop_delta_vs_historical": np.max(np.abs(iop - hist_iop)),
                "mean_abs_iop_delta_vs_historical": np.mean(np.abs(iop - hist_iop)),
                "proposal_min_reduction": PROPOSAL_MIN_REDUCTION,
                "proposal_max_reduction": PROPOSAL_MAX_REDUCTION,
            })
        # Keep these variables used explicitly for readability in future edits.
        _ = hist_reduction

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "figure13_old_new_recomputed_summary.csv", index=False)
    return df


def plot_dataset_comparison(dataset_key, variants, mode):
    fig, ax = plt.subplots(figsize=(9.5, 5.3), dpi=160)
    degrees = variants["historical_csv"]["degrees"]

    if mode == "reduction":
        transform = lambda x: BASELINE_IOP - x
        ylabel = "IOP reduction from 25 mmHg baseline (mmHg)"
        title_suffix = "IOP Reduction"
        ax.axhspan(
            PROPOSAL_MIN_REDUCTION,
            PROPOSAL_MAX_REDUCTION,
            color="#f5d76e",
            alpha=0.18,
            label="Proposal text range: 4.2-10 mmHg",
        )
    else:
        transform = lambda x: x
        ylabel = "Post-stent IOP (mmHg)"
        title_suffix = "Post-stent IOP"
        ax.axhline(BASELINE_IOP, color="black", linestyle="--", linewidth=1.0, label="Baseline IOP = 25")

    styles = {
        "historical_csv": ("#1f77b4", "-", "Historical CSV"),
        "old_solver": ("#4d4d4d", "--", "Old solver recomputed"),
        "current_solver": ("#d62728", "-.", "Current solver recomputed"),
    }

    for key in ["historical_csv", "old_solver", "current_solver"]:
        color, linestyle, label = styles[key]
        ax.plot(degrees, transform(variants[key]["iop"]), color=color, linestyle=linestyle, linewidth=2.0, label=label)

    cc_degrees = DATASETS[dataset_key]["ccs"][:, 0] / 50.0 * 360.0 / 24.0
    for deg in cc_degrees:
        ax.axvline(deg, ymin=0.0, ymax=0.06, color="#7f7f7f", alpha=0.35, linewidth=0.8)

    ax.set_xlim(-5, 360)
    ax.set_xticks(np.arange(0, 361, 60))
    if mode == "reduction":
        ax.set_ylim(0, 12)
    else:
        ax.set_ylim(10, 30)
    ax.grid(True, color="#dddddd", linewidth=0.8, alpha=0.75)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlabel("Degree (stent placement)")
    ax.set_ylabel(ylabel)
    ax.set_title("{0}: {1}".format(DATASETS[dataset_key]["label"], title_suffix))
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "figure13_{0}_{1}_comparison.png".format(dataset_key, mode))
    plt.close(fig)


def plot_overview(all_results):
    fig, axes = plt.subplots(3, 1, figsize=(9.5, 10.5), dpi=160, sharex=True)
    for ax, dataset_key in zip(axes, ["human", "mouse", "even"]):
        variants = all_results[dataset_key]
        degrees = variants["historical_csv"]["degrees"]
        ax.axhspan(PROPOSAL_MIN_REDUCTION, PROPOSAL_MAX_REDUCTION, color="#f5d76e", alpha=0.14)
        ax.plot(degrees, BASELINE_IOP - variants["historical_csv"]["iop"], color="#1f77b4", linewidth=2.0, label="Historical CSV")
        ax.plot(degrees, BASELINE_IOP - variants["old_solver"]["iop"], color="#4d4d4d", linestyle="--", linewidth=1.8, label="Old solver")
        ax.plot(degrees, BASELINE_IOP - variants["current_solver"]["iop"], color="#d62728", linestyle="-.", linewidth=1.8, label="Current solver")
        ax.set_ylim(0, 12)
        ax.set_xlim(-5, 360)
        ax.grid(True, color="#dddddd", linewidth=0.8, alpha=0.75)
        ax.set_ylabel("IOP reduction (mmHg)")
        ax.set_title(DATASETS[dataset_key]["label"], fontsize=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    axes[-1].set_xlabel("Degree (stent placement)")
    axes[-1].set_xticks(np.arange(0, 361, 60))
    axes[0].legend(loc="upper right", fontsize=8)
    fig.suptitle("Proposal Figure 13 Recomputed: Historical CSV vs Old/New Solvers", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "figure13_reduction_overview_old_new_vs_historical.png")
    plt.close(fig)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_results = {}

    for dataset_key in ["even", "mouse", "human"]:
        historical_raw = load_historical(dataset_key)
        all_results[dataset_key] = {
            "historical_csv": {
                "label": "Historical CSV",
                "degrees": degrees_for(historical_raw),
                "iop": processed_iop(historical_raw),
            }
        }
        for solver_key in ["old_solver", "current_solver"]:
            raw = recompute_solver_dataset(solver_key, dataset_key)
            all_results[dataset_key][solver_key] = {
                "label": SOLVERS[solver_key]["label"],
                "degrees": degrees_for(raw),
                "iop": processed_iop(raw),
            }

    for dataset_key, variants in all_results.items():
        plot_dataset_comparison(dataset_key, variants, "reduction")
        plot_dataset_comparison(dataset_key, variants, "iop")

    plot_overview(all_results)
    summary = write_summary(all_results)
    print("Wrote outputs to {0}".format(OUT_DIR))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
