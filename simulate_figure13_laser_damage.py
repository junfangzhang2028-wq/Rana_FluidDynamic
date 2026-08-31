"""Figure 13-style sweep for local laser damage.

Two damage models are evaluated for contiguous arcs of 1, 5, 25, or 100 SC
nodes:

1. ``tm_only``: disconnect only each damaged node's TM--SC branch (Rtm=inf).
2. ``full_node``: additionally disconnect collector-channel branches located
   on damaged nodes and every circumferential SC edge incident to a damaged
   node (Gsc=0).  Hydraulically isolated SC pressure unknowns are pinned by the
   small solver guard documented in ``offline/solver.py``; the pin adds no flow
   path.

Damage is placed at the same 60 start locations used by the proposal Figure 13
sweep.  The finite-conductance iStent inject curve is retained as a reference.
"""

from argparse import ArgumentParser
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import importlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
MODIFIED_ROOT = ROOT / "m-johnson2-aqueous-outflow-8fb729748300_Modified"
OUT_ROOT = ROOT / "paper_reproduction_outputs" / "figure13_laser_damage"
TOTAL_NODES = 1200
LOCS = np.linspace(0, 1180, 60).astype(int)

CCS_EVEN = np.array([(i, 1.0) for i in range(0, 1200, 40)], dtype=float)
CCS_MOUSE = np.array([
    (1069, 1), (1091, 1), (1115, 1), (1150, 1), (1163, 1), (1189, 1),
    (3, 1), (13, 1), (50, 1), (116, 1), (124, 10), (149, 1), (189, 1),
    (314, 1), (387, 1), (411, 1), (445, 1), (471, 10), (496, 1),
    (505, 1), (533, 1), (555, 1), (575, 1), (603, 1), (639, 1),
    (659, 1), (683, 1), (713, 1), (726, 1), (762, 1), (798, 1),
    (853, 1), (922, 1), (947, 1)], dtype=float)
CCS_HUMAN = np.array([
    (1, 1), (46, 1), (95, 1), (170, 1), (264, 1), (348, 1), (374, 1),
    (383, 1), (408, 1), (486, 1), (518, 10), (542, 1), (636, 1),
    (672, 1), (681, 1), (709, 1), (717, 1), (763, 10), (779, 1),
    (812, 1), (822, 1), (830, 1), (963, 1), (999, 1), (1081, 1),
    (1092, 1), (1100, 1), (1129, 1), (1144, 1)], dtype=float)

DATASETS = {
    "human": {"label": "Human donor CC distribution", "ccs": CCS_HUMAN, "rtm": 5.226},
    "mouse": {"label": "Mouse digital-twin CC distribution", "ccs": CCS_MOUSE, "rtm": 5.558},
    "even": {"label": "Even CC distribution", "ccs": CCS_EVEN, "rtm": 6.33},
}


def import_solver():
    sys.path.insert(0, str(MODIFIED_ROOT))
    try:
        return importlib.import_module("offline.solver")
    finally:
        sys.path.remove(str(MODIFIED_ROOT))


def make_stent(md):
    return md.Stent(name="iStent inject", length=145.0, loc_inlet=75.0,
                    w=50.0, hd=50.0, h_after=150.0,
                    g_inlet=42.15134797, l_after=0, l_before=0)


def damaged_nodes(start, count):
    return np.array([(int(start) + j) % TOTAL_NODES for j in range(count)], dtype=int)


def solve_quiet(md, **kwargs):
    with redirect_stdout(StringIO()):
        pressure = md.solve(qt=2.0, mode="constant flow", pev=8.0, **kwargs)
    return float(pressure[-1])


def solve_damage(md, dataset, start, count, full_node):
    nodes = damaged_nodes(start, count)
    rtm = np.repeat(dataset["rtm"] * TOTAL_NODES, TOTAL_NODES).astype(float)
    rtm[nodes] = np.inf
    kwargs = {"rtm": rtm, "variable_rtm": True, "ccs": dataset["ccs"]}

    if full_node:
        node_set = set(nodes.tolist())
        # A zero multiplier preserves the original CC-count denominator while
        # removing flow through a CC located on a damaged node.
        ccs = dataset["ccs"].copy()
        for row in ccs:
            if int(row[0]) in node_set:
                row[1] = 0.0
        gsc = np.repeat(np.nan, TOTAL_NODES)
        # Segment e connects node e to e+1.  Remove every edge incident to the
        # damaged arc: start-1 through start+count-1, with circular indexing.
        incident_edges = {(int(start) - 1 + j) % TOTAL_NODES for j in range(count + 1)}
        gsc[list(incident_edges)] = 0.0
        kwargs.update(ccs=ccs, gsc_override=gsc)

    return solve_quiet(md, **kwargs)


def cache_path(out_dir, dataset_key, variant):
    return out_dir / "raw_arrays" / f"{dataset_key}_{variant}.csv"


def compute_curve(path, compute):
    if path.exists():
        return np.loadtxt(path, delimiter=",")
    path.parent.mkdir(parents=True, exist_ok=True)
    values = np.array([compute(loc) for loc in LOCS], dtype=float)
    np.savetxt(path, values, delimiter=",")
    return values


def smooth_circular(values):
    """Match the proposal Figure 13 circular three-point moving average."""
    values = np.asarray(values, dtype=float)
    return (np.roll(values, 1) + values + np.roll(values, -1)) / 3.0


def plot_result(out_dir, count, results):
    fig, axes = plt.subplots(3, 3, figsize=(15.5, 10.0), dpi=160, sharex=True)
    degrees = LOCS / 50.0 * 360.0 / 24.0
    column_titles = [
        "Finite-conductance stent",
        f"TM disconnected from {count} SC node{'s' if count != 1 else ''} ($R_{{TM}} \\to \\infty$)",
        f"{count} SC node{'s' if count != 1 else ''} fully removed",
    ]
    colors = ["#2ca02c", "#e62720", "#1479b8"]

    for col, title in enumerate(column_titles):
        axes[0, col].set_title(title, fontsize=10)
    for row, key in enumerate(["human", "mouse", "even"]):
        result = results[key]
        baseline = result["baseline"]
        curves = [smooth_circular(result["stent"] - baseline),
                  smooth_circular(result["tm_only"] - baseline),
                  smooth_circular(result["full_node"] - baseline)]
        for col, curve in enumerate(curves):
            ax = axes[row, col]
            ax.plot(degrees, curve, color=colors[col], linewidth=1.7)
            ax.axhline(0, color="#333333", linestyle="--", linewidth=0.8)
            ax.grid(True, color="#dddddd", linewidth=0.6)
            ax.set_xlim(-5, 360)
            ax.set_xticks(np.arange(0, 361, 60))
            cc_degrees = DATASETS[key]["ccs"][:, 0] / 50.0 * 360.0 / 24.0
            for cc_loc, deg in zip(DATASETS[key]["ccs"], cc_degrees):
                lw = 2.0 if cc_loc[1] == 10 else 0.7
                ax.axvline(deg, ymin=0, ymax=0.06, color="#666666", linewidth=lw, alpha=0.7)
            if col == 0:
                ax.set_ylabel("$\\Delta$IOP (mmHg)")
                ax.text(0.01, 0.89, f"{DATASETS[key]['label']}\nBaseline {baseline:.3f} mmHg",
                        transform=ax.transAxes, fontsize=7.5, va="top")
            if row == 2:
                ax.set_xlabel("Figure 13 placement angle (degrees)")
        axes[row, 0].set_ylim(-12.5, 1.3)

    fig.suptitle(f"Figure 13-style laser damage sweep: {count}-node arc", fontsize=16, y=0.995)
    fig.text(0.5, 0.012, "|  CC location      ||  10x-conductance CC", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.025, 1, 0.97))
    fig.savefig(out_dir / f"figure13_damage_{count:03d}_nodes.png", bbox_inches="tight")
    plt.close(fig)


def run_size(md, count):
    out_dir = OUT_ROOT / f"{count:03d}_nodes"
    out_dir.mkdir(parents=True, exist_ok=True)
    stent = make_stent(md)
    results = {}
    rows = []

    for key, dataset in DATASETS.items():
        baseline = solve_quiet(md, rtm=dataset["rtm"], ccs=dataset["ccs"])
        stent_curve = compute_curve(cache_path(OUT_ROOT, key, "stent"),
            lambda loc: solve_quiet(md, rtm=dataset["rtm"], ccs=dataset["ccs"], stents=[(int(loc), stent)]))
        tm_curve = compute_curve(cache_path(out_dir, key, "tm_only"),
            lambda loc: solve_damage(md, dataset, loc, count, False))
        full_curve = compute_curve(cache_path(out_dir, key, "full_node"),
            lambda loc: solve_damage(md, dataset, loc, count, True))
        results[key] = {"baseline": baseline, "stent": stent_curve,
                        "tm_only": tm_curve, "full_node": full_curve}
        smooth_stent = smooth_circular(stent_curve)
        smooth_tm = smooth_circular(tm_curve)
        smooth_full = smooth_circular(full_curve)
        for loc, s, tm, full, ss, stm, sfull in zip(
                LOCS, stent_curve, tm_curve, full_curve,
                smooth_stent, smooth_tm, smooth_full):
            rows.extend([
                {"dataset": key, "damage_nodes": count, "start_node": loc,
                 "angle_deg": loc / 50 * 15, "variant": "stent", "baseline_iop": baseline,
                 "steady_iop_raw": s, "delta_iop_raw": s - baseline,
                 "steady_iop": ss, "delta_iop": ss - baseline},
                {"dataset": key, "damage_nodes": count, "start_node": loc,
                 "angle_deg": loc / 50 * 15, "variant": "tm_only", "baseline_iop": baseline,
                 "steady_iop_raw": tm, "delta_iop_raw": tm - baseline,
                 "steady_iop": stm, "delta_iop": stm - baseline},
                {"dataset": key, "damage_nodes": count, "start_node": loc,
                 "angle_deg": loc / 50 * 15, "variant": "full_node", "baseline_iop": baseline,
                 "steady_iop_raw": full, "delta_iop_raw": full - baseline,
                 "steady_iop": sfull, "delta_iop": sfull - baseline},
            ])
        print(f"completed {count} nodes / {key}")

    pd.DataFrame(rows).to_csv(out_dir / f"figure13_damage_{count:03d}_nodes.csv", index=False)
    plot_result(out_dir, count, results)


def main():
    parser = ArgumentParser()
    parser.add_argument("--damage-sizes", nargs="+", type=int, default=[5, 25, 100])
    args = parser.parse_args()
    if any(n < 1 or n >= TOTAL_NODES for n in args.damage_sizes):
        parser.error("damage sizes must be between 1 and 1199 nodes")
    md = import_solver()
    for count in args.damage_sizes:
        run_size(md, count)
    print(f"Wrote outputs to {OUT_ROOT}")


if __name__ == "__main__":
    main()
