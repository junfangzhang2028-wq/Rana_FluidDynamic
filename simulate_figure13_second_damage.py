"""Second-damage sweeps anchored at extrema of the first-damage curves.

For each damage size, CC distribution, and damage definition, select the
first-damage start locations giving the minimum and maximum smoothed delta IOP
in the existing Figure 13-style results.  Keep that first arc fixed and sweep
a second arc across the same 60 start locations.  Overlapping arcs are merged.
"""

from argparse import ArgumentParser
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import simulate_figure13_laser_damage as base


OUT_ROOT = base.OUT_ROOT / "second_damage"


def damage_union(first_start, second_start, count):
    first = set(base.damaged_nodes(first_start, count).tolist())
    second = set(base.damaged_nodes(second_start, count).tolist())
    return first, second, first | second


def solve_two_damage(md, dataset, first_start, second_start, count, full_node):
    first, second, nodes = damage_union(first_start, second_start, count)
    rtm = np.repeat(dataset["rtm"] * base.TOTAL_NODES,
                    base.TOTAL_NODES).astype(float)
    rtm[list(nodes)] = np.inf
    kwargs = {"rtm": rtm, "variable_rtm": True, "ccs": dataset["ccs"]}

    if full_node:
        ccs = dataset["ccs"].copy()
        for row in ccs:
            if int(row[0]) in nodes:
                row[1] = 0.0
        gsc = np.repeat(np.nan, base.TOTAL_NODES)
        incident_edges = set()
        for start in (first_start, second_start):
            incident_edges.update(
                (int(start) - 1 + j) % base.TOTAL_NODES
                for j in range(count + 1)
            )
        gsc[list(incident_edges)] = 0.0
        kwargs.update(ccs=ccs, gsc_override=gsc)

    return base.solve_quiet(md, **kwargs), len(second - first), len(nodes)


def solve_two_damage_pressure(md, dataset, first_start, second_start, count,
                              full_node, guess=None):
    """Return the full solution so the next angular position can reuse it."""
    first, second, nodes = damage_union(first_start, second_start, count)
    rtm = np.repeat(dataset["rtm"] * base.TOTAL_NODES,
                    base.TOTAL_NODES).astype(float)
    rtm[list(nodes)] = np.inf
    kwargs = {"rtm": rtm, "variable_rtm": True, "ccs": dataset["ccs"]}
    if full_node:
        ccs = dataset["ccs"].copy()
        for row in ccs:
            if int(row[0]) in nodes:
                row[1] = 0.0
        gsc = np.repeat(np.nan, base.TOTAL_NODES)
        incident_edges = set()
        for start in (first_start, second_start):
            incident_edges.update(
                (int(start) - 1 + j) % base.TOTAL_NODES
                for j in range(count + 1)
            )
        gsc[list(incident_edges)] = 0.0
        kwargs.update(ccs=ccs, gsc_override=gsc)
    with redirect_stdout(StringIO()):
        pressure = md.solve(qt=2.0, mode="constant flow", pev=8.0,
                            guess=guess, **kwargs)
    return np.asarray(pressure), len(second - first), len(nodes)


def choose_anchors(count, dataset_key, variant):
    source = (base.OUT_ROOT / f"{count:03d}_nodes" /
              f"figure13_damage_{count:03d}_nodes.csv")
    df = pd.read_csv(source)
    subset = df[(df["dataset"] == dataset_key) &
                (df["variant"] == variant)].copy()
    if len(subset) != len(base.LOCS):
        raise RuntimeError(f"Unexpected source rows in {source}: {len(subset)}")
    min_row = subset.loc[subset["delta_iop"].idxmin()]
    max_row = subset.loc[subset["delta_iop"].idxmax()]
    return {
        "min": (int(min_row["start_node"]), float(min_row["steady_iop"]),
                float(min_row["delta_iop"])),
        "max": (int(max_row["start_node"]), float(max_row["steady_iop"]),
                float(max_row["delta_iop"])),
    }


def raw_path(size_dir, dataset_key, variant, anchor_kind):
    return size_dir / "raw_arrays" / f"{dataset_key}_{variant}_{anchor_kind}.csv"


def plot_size(size_dir, count, frame, anchors, use_raw=False):
    fig, axes = plt.subplots(3, 4, figsize=(17, 10), dpi=160,
                             sharex=True)
    columns = [("tm_only", "min"), ("tm_only", "max"),
               ("full_node", "min"), ("full_node", "max")]
    titles = ["TM-only: first-damage minimum", "TM-only: first-damage maximum",
              "Full-node: first-damage minimum", "Full-node: first-damage maximum"]
    colors = {"tm_only": "#e62720", "full_node": "#1479b8"}

    for col, title in enumerate(titles):
        axes[0, col].set_title(title, fontsize=10)
    for row, dataset_key in enumerate(["human", "mouse", "even"]):
        baseline = float(frame[frame["dataset"] == dataset_key]["baseline_iop"].iloc[0])
        cc_degrees = base.DATASETS[dataset_key]["ccs"][:, 0] / 50.0 * 15.0
        for col, (variant, anchor_kind) in enumerate(columns):
            ax = axes[row, col]
            sub = frame[(frame["dataset"] == dataset_key) &
                        (frame["variant"] == variant) &
                        (frame["first_anchor_kind"] == anchor_kind)].sort_values("second_start_node")
            curve_column = "total_delta_iop_raw" if use_raw else "total_delta_iop"
            ax.plot(sub["second_angle_deg"], sub[curve_column],
                    color=colors[variant], linewidth=1.7, label="After two damages")
            if use_raw:
                overlap = sub[sub["second_start_node"] == sub["first_start_node"]]
                if len(overlap) != 1:
                    raise RuntimeError("Expected one exact-overlap point for raw baseline")
                first_delta = float(overlap["total_delta_iop_raw"].iloc[0])
            else:
                first_delta = float(sub["first_delta_iop"].iloc[0])
            ax.axhline(0, color="#222222", linestyle="--", linewidth=1.0,
                       label="Initial baseline (no damage)")
            ax.axhline(first_delta, color="#f39c12", linestyle="--", linewidth=1.3,
                       label="Post-first-damage baseline")
            for cc_row, deg in zip(base.DATASETS[dataset_key]["ccs"], cc_degrees):
                ax.axvline(deg, ymin=0, ymax=0.05, color="#777777",
                           linewidth=2.0 if cc_row[1] == 10 else 0.7, alpha=0.7)
            first_start = anchors[(dataset_key, variant, anchor_kind)][0]
            first_angle = first_start / 50.0 * 15.0
            ax.axvline(first_angle, color="#8e44ad", linestyle="-.", linewidth=1.0)
            ax.grid(True, color="#dddddd", linewidth=0.6)
            ax.set_xlim(-5, 360)
            ax.set_xticks(np.arange(0, 361, 60))
            ax.text(0.015, 0.96,
                    f"First start: node {first_start} ({first_angle:.0f}°)\n"
                    f"Initial baseline: {baseline:.3f} mmHg\n"
                    f"Post-first baseline: {baseline + first_delta:.3f} mmHg",
                    transform=ax.transAxes, va="top", fontsize=7.3)
            if col == 0:
                ax.set_ylabel(f"{base.DATASETS[dataset_key]['label']}\nTotal $\\Delta$IOP (mmHg)")
            if row == 2:
                ax.set_xlabel("Second-damage start angle (degrees)")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False)
    data_label = "raw, unsmoothed" if use_raw else "three-point smoothed"
    fig.suptitle(
        f"Second laser-damage distribution: two {count}-node arcs ({data_label})",
        fontsize=16)
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    suffix = "_raw_unsmoothed" if use_raw else ""
    fig.savefig(size_dir / f"figure13_second_damage_{count:03d}_nodes{suffix}.png",
                bbox_inches="tight")
    plt.close(fig)


def run_size(md, count):
    size_dir = OUT_ROOT / f"{count:03d}_nodes"
    size_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    anchor_records = []
    anchor_lookup = {}

    for dataset_key, dataset in base.DATASETS.items():
        baseline = base.solve_quiet(md, rtm=dataset["rtm"], ccs=dataset["ccs"])
        for variant in ("tm_only", "full_node"):
            anchors = choose_anchors(count, dataset_key, variant)
            for anchor_kind, (first_start, first_iop, first_delta) in anchors.items():
                anchor_lookup[(dataset_key, variant, anchor_kind)] = (
                    first_start, first_iop, first_delta)
                anchor_records.append({
                    "dataset": dataset_key, "damage_nodes": count,
                    "variant": variant, "first_anchor_kind": anchor_kind,
                    "first_start_node": first_start,
                    "first_angle_deg": first_start / 50.0 * 15.0,
                    "baseline_iop": baseline, "first_steady_iop": first_iop,
                    "first_delta_iop": first_delta,
                })
                path = raw_path(size_dir, dataset_key, variant, anchor_kind)
                if path.exists():
                    values = np.loadtxt(path, delimiter=",")
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    curve_by_start = {}
                    guess = None
                    nearest = int(np.argmin([
                        min((int(loc) - first_start) % base.TOTAL_NODES,
                            (first_start - int(loc)) % base.TOTAL_NODES)
                        for loc in base.LOCS
                    ]))
                    ordered_locs = np.roll(base.LOCS, -nearest)
                    for second in ordered_locs:
                        pressure, _, _ = solve_two_damage_pressure(
                            md, dataset, first_start, int(second), count,
                            variant == "full_node", guess=guess)
                        curve_by_start[int(second)] = float(pressure[-1])
                        # solve() returns pressures with Pev added; its initial
                        # guess is expressed relative to Pev.
                        guess = pressure - 8.0
                    values = np.asarray([curve_by_start[int(loc)] for loc in base.LOCS])
                    np.savetxt(path, values, delimiter=",")
                smoothed = base.smooth_circular(values)
                for second, raw_iop, total_iop in zip(base.LOCS, values, smoothed):
                    first_nodes, second_nodes, union_nodes = damage_union(
                        first_start, int(second), count)
                    added = len(second_nodes - first_nodes)
                    union_count = len(union_nodes)
                    rows.append({
                        "dataset": dataset_key, "damage_nodes_each_arc": count,
                        "variant": variant, "first_anchor_kind": anchor_kind,
                        "first_start_node": first_start,
                        "first_angle_deg": first_start / 50.0 * 15.0,
                        "second_start_node": int(second),
                        "second_angle_deg": int(second) / 50.0 * 15.0,
                        "unique_nodes_after_two_damages": union_count,
                        "new_nodes_added_by_second_damage": added,
                        "baseline_iop": baseline, "first_steady_iop": first_iop,
                        "first_delta_iop": first_delta,
                        "second_steady_iop_raw": raw_iop,
                        "second_increment_iop_raw": raw_iop - first_iop,
                        "total_delta_iop_raw": raw_iop - baseline,
                        "second_steady_iop": total_iop,
                        "second_increment_iop": total_iop - first_iop,
                        "total_delta_iop": total_iop - baseline,
                    })
                print(f"completed {count} / {dataset_key} / {variant} / {anchor_kind}")

    frame = pd.DataFrame(rows)
    frame.to_csv(size_dir / f"figure13_second_damage_{count:03d}_nodes.csv",
                 index=False)
    pd.DataFrame(anchor_records).to_csv(
        size_dir / f"first_damage_anchors_{count:03d}_nodes.csv", index=False)
    plot_size(size_dir, count, frame, anchor_lookup)
    plot_size(size_dir, count, frame, anchor_lookup, use_raw=True)


def main():
    parser = ArgumentParser()
    parser.add_argument("--damage-sizes", nargs="+", type=int,
                        default=[5, 25, 50, 100])
    args = parser.parse_args()
    md = base.import_solver()
    for count in args.damage_sizes:
        run_size(md, count)
    print(f"Wrote second-damage outputs to {OUT_ROOT}")


if __name__ == "__main__":
    main()
