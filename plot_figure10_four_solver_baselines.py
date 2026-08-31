"""Generate four Figure 10 variants for old/new solvers and baseline handling.

The legacy commented experiment in Modified/offline/outputs_trial.py used the
old iStent inject parameters and saved only post-stent IOP arrays. This script
regenerates those calculations in a controlled way:

1. Old solver, legacy Rtm=6.71, computed no-stent baseline.
2. Current solver, legacy Rtm=6.71, computed no-stent baseline.
3. Old solver, Rtm calibrated so no-stent baseline IOP is 25 mmHg.
4. Current solver, Rtm calibrated so no-stent baseline IOP is 25 mmHg.

No baseline bar is hard-coded except as the calibration target in cases 3-4.
"""

from __future__ import annotations

import csv
import contextlib
import io
import os
import sys
import tempfile
import zlib
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
GIT_DIR = ROOT / ".git"
MODIFIED_ROOT = ROOT / "m-johnson2-aqueous-outflow-8fb729748300_Modified"
OUT_DIR = ROOT / "paper_reproduction_outputs" / "figure10_four_solver_baselines"

INITIAL_COMMIT = "29f1821696a370b1934dd66964c86885d6573b71"
OLD_SOLVER_BASE = "m-johnson2-aqueous-outflow-8fb729748300_Modified/offline"

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

LEGACY_RTM = 6.71
TARGET_BASELINE_IOP = 25.0
QT = 2.0
PEV = 8.0
START_NODES = np.linspace(50, 250, 10)
N_REPEATS = 2
STENT_SPACING_NODES = 300


def read_git_object(sha: str) -> Tuple[str, bytes]:
    raw = zlib.decompress((GIT_DIR / "objects" / sha[:2] / sha[2:]).read_bytes())
    header, data = raw.split(b"\0", 1)
    obj_type = header.split(b" ")[0].decode("ascii")
    return obj_type, data


def tree_for_commit(commit_sha: str) -> str:
    obj_type, data = read_git_object(commit_sha)
    if obj_type != "commit":
        raise ValueError(f"{commit_sha} is a {obj_type}, not a commit")
    return data.splitlines()[0].decode("ascii").split()[1]


def parse_tree(tree_sha: str) -> Dict[str, str]:
    obj_type, data = read_git_object(tree_sha)
    if obj_type != "tree":
        raise ValueError(f"{tree_sha} is a {obj_type}, not a tree")

    entries: Dict[str, str] = {}
    i = 0
    while i < len(data):
        space = data.index(b" ", i)
        nul = data.index(b"\0", space + 1)
        name = data[space + 1 : nul].decode(errors="surrogateescape")
        entries[name] = data[nul + 1 : nul + 21].hex()
        i = nul + 21
    return entries


def git_blob_at(commit_sha: str, repo_path: str) -> bytes:
    sha = tree_for_commit(commit_sha)
    parts = repo_path.split("/")
    for part in parts[:-1]:
        sha = parse_tree(sha)[part]
    blob_sha = parse_tree(sha)[parts[-1]]
    obj_type, data = read_git_object(blob_sha)
    if obj_type != "blob":
        raise ValueError(f"{repo_path} resolved to a {obj_type}, not a blob")
    return data


def clear_offline_modules() -> None:
    for key in list(sys.modules):
        if key == "offline" or key.startswith("offline."):
            sys.modules.pop(key, None)


def solve_iop(md, rtm: float, stents) -> float:
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        pressure = md.solve(
            qt=QT,
            mode="constant flow",
            geometry="ellipse",
            stents=stents,
            rtm=rtm,
            pev=PEV,
            max_error=1e-4,
        )
    return float(pressure[-1])


def make_stents(md, start: int, count: int):
    if count == 0:
        return None
    return [
        (start + STENT_SPACING_NODES * k, md.Stent(**LEGACY_STENT_PARAMS))
        for k in range(count)
    ]


def calibrate_rtm(md, target_iop: float = TARGET_BASELINE_IOP) -> float:
    lo = 0.1
    hi = 12.0

    for _ in range(60):
        mid = (lo + hi) / 2.0
        iop = solve_iop(md, mid, None)
        if iop < target_iop:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def run_sweep(md, rtm: float) -> Tuple[float, Dict[int, np.ndarray]]:
    baseline = solve_iop(md, rtm, None)
    arrays: Dict[int, np.ndarray] = {}

    for count in range(1, 5):
        values = np.zeros((len(START_NODES), N_REPEATS), dtype=float)
        for repeat in range(N_REPEATS):
            for i, start_node in enumerate(START_NODES):
                start = int(start_node)
                values[i, repeat] = solve_iop(md, rtm, make_stents(md, start, count))
        arrays[count] = values

    return baseline, arrays


def summarize_rows(
    solver_label: str,
    baseline_mode: str,
    rtm: float,
    baseline: float,
    arrays: Dict[int, np.ndarray],
) -> List[dict]:
    rows = [
        {
            "solver": solver_label,
            "baseline_mode": baseline_mode,
            "count": 0,
            "label": "Baseline",
            "rtm": rtm,
            "mean_iop": baseline,
            "std_iop": 0.0,
            "min_iop": baseline,
            "max_iop": baseline,
        }
    ]
    for count in range(1, 5):
        values = arrays[count]
        rows.append(
            {
                "solver": solver_label,
                "baseline_mode": baseline_mode,
                "count": count,
                "label": str(count),
                "rtm": rtm,
                "mean_iop": float(np.mean(values)),
                "std_iop": float(np.std(values)),
                "min_iop": float(np.min(values)),
                "max_iop": float(np.max(values)),
            }
        )
    return rows


def write_raw_arrays(
    solver_slug: str,
    baseline_slug: str,
    arrays: Dict[int, np.ndarray],
) -> None:
    raw_dir = OUT_DIR / "raw_arrays" / f"{solver_slug}_{baseline_slug}"
    raw_dir.mkdir(parents=True, exist_ok=True)
    for count, values in arrays.items():
        np.savetxt(raw_dir / f"iop_istent_pos{count}.csv", values, delimiter=",")


def plot_case(
    rows: List[dict],
    solver_label: str,
    baseline_mode: str,
    solver_slug: str,
    baseline_slug: str,
) -> Path:
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

    rtm = rows[0]["rtm"]
    baseline = rows[0]["mean_iop"]
    caption = (
        f"{solver_label}; {baseline_mode}. "
        f"Rtm={rtm:.6f}; computed no-stent baseline={baseline:.4f} mmHg. "
        "Legacy commented-code iStent inject parameters are used."
    )
    fig.subplots_adjust(bottom=0.34, left=0.2, right=0.96, top=0.96)
    fig.text(0.02, 0.03, caption, ha="left", va="bottom", fontsize=6.2, wrap=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"figure10_{solver_slug}_{baseline_slug}.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def write_summary(all_rows: Iterable[dict]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "figure10_four_solver_baselines_summary.csv"
    fieldnames = [
        "solver",
        "baseline_mode",
        "count",
        "label",
        "rtm",
        "mean_iop",
        "std_iop",
        "min_iop",
        "max_iop",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    return path


def run_case(md, solver_label: str, solver_slug: str) -> Tuple[List[dict], List[Path]]:
    outputs: List[Path] = []
    all_rows: List[dict] = []

    cases = [
        ("computed baseline from legacy Rtm", "legacy_rtm_computed_baseline", LEGACY_RTM),
        (
            "Rtm calibrated to 25 mmHg baseline",
            "calibrated_rtm_baseline_25",
            calibrate_rtm(md, TARGET_BASELINE_IOP),
        ),
    ]

    for baseline_mode, baseline_slug, rtm in cases:
        print(f"Running {solver_label}: {baseline_mode} (Rtm={rtm:.8f})")
        baseline, arrays = run_sweep(md, rtm)
        rows = summarize_rows(solver_label, baseline_mode, rtm, baseline, arrays)
        write_raw_arrays(solver_slug, baseline_slug, arrays)
        outputs.append(plot_case(rows, solver_label, baseline_mode, solver_slug, baseline_slug))
        all_rows.extend(rows)

    return all_rows, outputs


def with_old_solver():
    with tempfile.TemporaryDirectory() as td:
        temp_root = Path(td)
        pkg = temp_root / "offline"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        for name in ["solver.py", "gauss_seidel.py"]:
            data = git_blob_at(INITIAL_COMMIT, f"{OLD_SOLVER_BASE}/{name}")
            (pkg / name).write_bytes(data)

        old_path = list(sys.path)
        sys.path.insert(0, str(temp_root))
        try:
            from offline import solver as md  # pylint: disable=import-outside-toplevel

            return run_case(md, "Old solver", "old_solver")
        finally:
            clear_offline_modules()
            sys.path[:] = old_path


def with_current_solver():
    old_path = list(sys.path)
    old_cwd = os.getcwd()
    sys.path.insert(0, str(MODIFIED_ROOT))
    os.chdir(str(MODIFIED_ROOT))
    try:
        from offline import solver as md  # pylint: disable=import-outside-toplevel

        return run_case(md, "Current solver", "current_solver")
    finally:
        clear_offline_modules()
        sys.path[:] = old_path
        os.chdir(old_cwd)


def main() -> None:
    all_rows: List[dict] = []
    all_outputs: List[Path] = []

    rows, outputs = with_old_solver()
    all_rows.extend(rows)
    all_outputs.extend(outputs)

    rows, outputs = with_current_solver()
    all_rows.extend(rows)
    all_outputs.extend(outputs)

    summary_path = write_summary(all_rows)
    print(f"Wrote {summary_path}")
    for path in all_outputs:
        print(f"Wrote {path}")

    print("\nSummary:")
    for row in all_rows:
        print(
            f"{row['solver']} | {row['baseline_mode']} | {row['label']}: "
            f"{row['mean_iop']:.4f} +/- {row['std_iop']:.4f} mmHg "
            f"(Rtm={row['rtm']:.6f})"
        )


if __name__ == "__main__":
    main()
