"""Rebuild the combined summary for the four Figure 10 baseline variants."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "paper_reproduction_outputs" / "figure10_four_solver_baselines"
RAW_DIR = OUT_DIR / "raw_arrays"

CASES = [
    ("Old solver", "computed baseline from legacy Rtm", "old_solver_legacy_rtm_computed_baseline", 6.71, None),
    ("Old solver", "Rtm calibrated to 25 mmHg baseline", "old_solver_calibrated_rtm_baseline_25", None, 25.0),
    ("Current solver", "computed baseline from legacy Rtm", "current_solver_legacy_rtm_computed_baseline", 6.71, None),
    ("Current solver", "Rtm calibrated to 25 mmHg baseline", "current_solver_calibrated_rtm_baseline_25", None, 25.0),
]


def infer_rtm_and_baseline(case_slug: str, rtm_hint, baseline_hint):
    # The calibrated old/current cases use the same no-stent solve for this
    # model. Keep the calibrated Rtm explicit so the summary is standalone.
    calibrated_rtm = 6.159302562983
    if rtm_hint is not None:
        rtm = rtm_hint
    else:
        rtm = calibrated_rtm

    if baseline_hint is not None:
        baseline = baseline_hint
    elif "legacy_rtm" in case_slug:
        baseline = 26.288635910694
    else:
        baseline = 25.0
    return rtm, baseline


def main():
    rows = []
    for solver, baseline_mode, slug, rtm_hint, baseline_hint in CASES:
        rtm, baseline = infer_rtm_and_baseline(slug, rtm_hint, baseline_hint)
        rows.append(
            {
                "solver": solver,
                "baseline_mode": baseline_mode,
                "count": 0,
                "label": "Baseline",
                "rtm": rtm,
                "mean_iop": baseline,
                "std_iop": 0.0,
                "min_iop": baseline,
                "max_iop": baseline,
            }
        )
        for count in range(1, 5):
            values = np.genfromtxt(RAW_DIR / slug / f"iop_istent_pos{count}.csv", delimiter=",")
            rows.append(
                {
                    "solver": solver,
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

    path = OUT_DIR / "figure10_four_solver_baselines_summary.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "solver",
                "baseline_mode",
                "count",
                "label",
                "rtm",
                "mean_iop",
                "std_iop",
                "min_iop",
                "max_iop",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {path}")
    for row in rows:
        print(
            "{solver} | {baseline_mode} | {label}: "
            "{mean_iop:.4f} +/- {std_iop:.4f} mmHg (Rtm={rtm:.6f})".format(**row)
        )


if __name__ == "__main__":
    main()
