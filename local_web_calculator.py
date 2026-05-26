from __future__ import annotations

import contextlib
import io
import json
import os
import socket
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import numpy as np


REPO_ROOT = Path(__file__).resolve().parent
PROJECT_DIR = REPO_ROOT / "m-johnson2-aqueous-outflow-8fb729748300_Modified"

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

os.chdir(PROJECT_DIR)

from offline import outputs_trial as ot
from offline import solver as md


def build_istent(
    name: str = "iStent (R)",
    length: float = 1000.0,
    loc_inlet: float = 0.0,
    width: float = 120.0,
    height: float = 60.0,
    n_windows: int = 0,
    l_window: float | None = None,
    h_window: float | None = None,
    l_spine: float | None = None,
    h_spine: float | None = None,
    two_way: bool = True,
    l_before: float = 0.0,
    l_after: float = 0.0,
    h_after: float | None = None,
    g_inlet: float = 0.0,
    geometry: str = "ellipse",
) -> md.Stent:
    return md.Stent(
        name=name,
        length=length,
        loc_inlet=loc_inlet,
        w=width,
        hd=height,
        n_windows=n_windows,
        l_window=l_window,
        h_window=h_window,
        l_spine=l_spine,
        h_spine=h_spine,
        two_way=two_way,
        l_before=l_before,
        l_after=l_after,
        h_after=h_after,
        g_inlet=g_inlet,
        geometry=geometry,
    )


def finite_float(value, default=None):
    if value in ("", None):
        return default
    return float(value)


def finite_int(value, default=None):
    if value in ("", None):
        return default
    return int(float(value))


def finite_bool(value, default=False):
    if value in ("", None):
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def parse_ranges(text) -> list[tuple[int, int]]:
    if not text:
        return []
    ranges = []
    for chunk in str(text).replace(";", ",").split(","):
        part = chunk.strip()
        if not part:
            continue
        if "-" in part:
            left, right = part.split("-", 1)
            start = int(float(left.strip()))
            end = int(float(right.strip()))
        elif ":" in part:
            left, right = part.split(":", 1)
            start = int(float(left.strip()))
            end = int(float(right.strip()))
        else:
            start = end = int(float(part))
        if end < start:
            start, end = end, start
        ranges.append((start, end))
    return ranges


def parse_int_list(text) -> list[int]:
    if not text:
        return []
    values = []
    for chunk in str(text).replace(";", ",").split(","):
        part = chunk.strip()
        if part:
            values.append(int(float(part)))
    return values


def parse_ccs(text, max_nodes=None):
    if not text:
        return None

    ccs = []
    for chunk in str(text).replace(";", ",").split(","):
        part = chunk.strip()
        if not part:
            continue

        if ":" in part:
            loc_text, ratio_text = part.split(":", 1)
        elif "=" in part:
            loc_text, ratio_text = part.split("=", 1)
        else:
            loc_text, ratio_text = part, "1"

        loc = int(float(loc_text.strip()))
        ratio = float(ratio_text.strip())
        if loc < 0:
            raise ValueError("Collector channel node indexes must be non-negative.")
        if max_nodes is not None and loc >= max_nodes:
            raise ValueError(f"Collector channel node {loc} is outside the current 0-{max_nodes - 1} node range.")
        if ratio <= 0:
            raise ValueError("Collector channel conductance ratios must be greater than zero.")
        ccs.append((loc, ratio))

    if not ccs:
        return None

    return np.array(ccs, dtype=md.dt)


def parse_segment_profile(text, expected_count, label, allow_zero=True):
    if not text or not str(text).strip():
        return None

    chunks = []
    for chunk in str(text).replace(";", ",").replace("\n", ",").split(","):
        part = chunk.strip()
        if part:
            chunks.append(part)

    if not chunks:
        return None

    keyed = any((":" in chunk or "=" in chunk) for chunk in chunks)
    values = [None] * expected_count

    if keyed:
        for chunk in chunks:
            if ":" in chunk:
                idx_text, value_text = chunk.split(":", 1)
            elif "=" in chunk:
                idx_text, value_text = chunk.split("=", 1)
            else:
                raise ValueError(f"{label} profile mixes keyed and unkeyed values.")

            idx = int(float(idx_text.strip()))
            if idx < 1 or idx > expected_count:
                raise ValueError(f"{label} segment {idx} is outside the valid 1-{expected_count} range.")
            value = float(value_text.strip())
            if value < 0 or (not allow_zero and value == 0):
                comparator = "greater than zero" if not allow_zero else "zero or greater"
                raise ValueError(f"{label} values must be {comparator}.")
            values[idx - 1] = value

        missing = [str(i + 1) for i, value in enumerate(values) if value is None]
        if missing:
            raise ValueError(f"{label} profile is missing segment(s): {', '.join(missing)}.")
    else:
        raw_values = [float(chunk) for chunk in chunks]
        for value in raw_values:
            if value < 0 or (not allow_zero and value == 0):
                comparator = "greater than zero" if not allow_zero else "zero or greater"
                raise ValueError(f"{label} values must be {comparator}.")

        if len(raw_values) == 1:
            values = raw_values * expected_count
        elif len(raw_values) == expected_count:
            values = raw_values
        else:
            raise ValueError(
                f"{label} profile needs either 1 value or exactly {expected_count} values; got {len(raw_values)}."
            )

    return values


def expand_tm_profile(values, total_nodes):
    expanded = np.zeros(total_nodes, dtype=md.dt)
    count = len(values)
    for idx, resistance in enumerate(values):
        start = int(round(idx * total_nodes / count))
        end = int(round((idx + 1) * total_nodes / count))
        segment_len = max(1, end - start)
        expanded[start:end] = resistance * segment_len
    return expanded


def expand_sc_profile(values, total_nodes):
    expanded = np.zeros(total_nodes, dtype=md.dt)
    count = len(values)
    for idx, height in enumerate(values):
        start = int(round(idx * total_nodes / count))
        end = int(round((idx + 1) * total_nodes / count))
        expanded[start:end] = height
    return expanded


def parse_node_value_overrides(text, max_nodes, label, allow_zero=False):
    if not text or not str(text).strip():
        return []

    overrides = []
    for chunk in str(text).replace(";", ",").replace("\n", ",").split(","):
        part = chunk.strip()
        if not part:
            continue

        if ":" in part:
            range_text, value_text = part.split(":", 1)
        elif "=" in part:
            range_text, value_text = part.split("=", 1)
        else:
            raise ValueError(f"{label} overrides must use node:value or start-end:value format.")

        range_text = range_text.strip()
        value = float(value_text.strip())
        if value < 0 or (not allow_zero and value == 0):
            comparator = "greater than zero" if not allow_zero else "zero or greater"
            raise ValueError(f"{label} override values must be {comparator}.")

        if "-" in range_text:
            left, right = range_text.split("-", 1)
            start = int(float(left.strip()))
            end = int(float(right.strip()))
        else:
            start = end = int(float(range_text))

        if end < start:
            start, end = end, start
        if start < 0 or end < 0:
            raise ValueError(f"{label} override node indexes must be non-negative.")
        if max_nodes is not None and end >= max_nodes:
            raise ValueError(f"{label} override {start}-{end} is outside the current 0-{max_nodes - 1} node range.")
        overrides.append((start, end, value))

    return overrides


def apply_node_value_overrides(base_values, overrides):
    values = np.array(base_values, dtype=md.dt, copy=True)
    for start, end, value in overrides:
        values[start:end + 1] = value
    return values


def parse_full_value_array(text, expected_count, label, allow_zero=True):
    if not text or not str(text).strip():
        return None

    values = []
    for chunk in str(text).replace(";", ",").replace("\n", ",").split(","):
        part = chunk.strip()
        if not part:
            continue
        value = float(part)
        if value < 0 or (not allow_zero and value == 0):
            comparator = "greater than zero" if not allow_zero else "zero or greater"
            raise ValueError(f"{label} values must be {comparator}.")
        values.append(value)

    if not values:
        return None

    if len(values) == 1:
        values = values * expected_count
    elif len(values) != expected_count:
        raise ValueError(f"{label} needs either 1 value or exactly {expected_count} values; got {len(values)}.")

    return np.array(values, dtype=md.dt)


def parse_value_array_or_overrides(text, expected_count, label, allow_zero=True):
    if not text or not str(text).strip():
        return None, []

    chunks = [
        part.strip()
        for part in str(text).replace(";", ",").replace("\n", ",").split(",")
        if part.strip()
    ]
    keyed = any((":" in chunk or "=" in chunk) for chunk in chunks)
    if keyed:
        return None, parse_node_value_overrides(text, expected_count, label, allow_zero=allow_zero)
    return parse_full_value_array(text, expected_count, label, allow_zero=allow_zero), []


def stent_from_payload(payload: dict) -> md.Stent:
    return build_istent(
        name=str(payload.get("stent_name") or "Custom stent"),
        length=finite_float(payload.get("stent_length"), 1000.0),
        loc_inlet=finite_float(payload.get("stent_loc_inlet"), 0.0),
        width=finite_float(payload.get("stent_width"), 120.0),
        height=finite_float(payload.get("stent_height"), 60.0),
        n_windows=finite_int(payload.get("stent_n_windows"), 0) or 0,
        l_window=finite_float(payload.get("stent_l_window"), None),
        h_window=finite_float(payload.get("stent_h_window"), None),
        l_spine=finite_float(payload.get("stent_l_spine"), None),
        h_spine=finite_float(payload.get("stent_h_spine"), None),
        two_way=finite_bool(payload.get("stent_two_way"), True),
        l_before=finite_float(payload.get("stent_l_before"), 0.0),
        l_after=finite_float(payload.get("stent_l_after"), 0.0),
        h_after=finite_float(payload.get("stent_h_after"), None),
        g_inlet=finite_float(payload.get("stent_g_inlet"), 0.0),
        geometry=str(payload.get("stent_geometry") or payload.get("geometry") or "ellipse"),
    )


def parse_stent_nodes(text, payload: dict) -> list[tuple[int, md.Stent]]:
    return [(node, stent_from_payload(payload)) for node in parse_int_list(text)]


def default_trabeculotomies(hours: int) -> list[tuple[int, int]]:
    if hours == 1:
        return [(550, 650)]
    if hours == 4:
        return [(100, 200), (400, 500), (700, 800), (1000, 1100)]
    if hours == 12:
        return [(0, 1199)]
    if hours == 0:
        return []
    raise ValueError("Hours must be one of 0, 1, 4, or 12.")


def default_yag_holes(count: int) -> list[int]:
    defaults = {
        0: [],
        1: [600],
        2: [300, 900],
        3: [200, 600, 1000],
        4: [150, 450, 750, 1050],
        5: [120, 360, 600, 840, 1080],
        6: [100, 300, 500, 700, 900, 1100],
    }
    if count not in defaults:
        raise ValueError("Invalid value of n. Use explicit hole nodes for more than 6 holes.")
    return defaults[count]


def estimate_rtm_from_baseline_iop(target_iop: float, base_kwargs: dict) -> float:
    pev = float(base_kwargs.get("pev", 8.0))
    if target_iop <= pev:
        raise ValueError("Baseline IOP must be greater than episcleral venous pressure.")

    solve_kwargs = dict(base_kwargs)
    solve_kwargs.pop("rtm", None)
    solve_kwargs.pop("ccs", None)
    solve_kwargs.pop("trabeculotomies", None)
    solve_kwargs.pop("sinusotomies", None)
    solve_kwargs.pop("yag_holes", None)
    solve_kwargs.pop("stents", None)

    def solve_iop(rtm_value: float) -> float:
        with contextlib.redirect_stdout(io.StringIO()):
            result = ot.solve_cf(qt=2.0, rtm=rtm_value, **solve_kwargs)
        return float(result["iop"])

    low = 0.05
    high = 8.0
    low_iop = solve_iop(low)
    high_iop = solve_iop(high)

    if target_iop <= low_iop:
        return low

    expand_count = 0
    while high_iop < target_iop and expand_count < 8:
        high *= 1.75
        high_iop = solve_iop(high)
        expand_count += 1

    if high_iop < target_iop:
        raise ValueError("Could not match the requested baseline IOP with a reasonable Rtm range.")

    for _ in range(28):
        mid = 0.5 * (low + high)
        mid_iop = solve_iop(mid)
        if mid_iop < target_iop:
            low = mid
        else:
            high = mid

    return round(0.5 * (low + high), 4)


def solution_to_jsonable(solution: dict, stents=None, ccs=None, meta=None) -> dict:
    pressure = [float(v) for v in solution.get("pressure", [])]
    jcc = [float(v) for v in solution.get("jcc", [])]
    iop = float(solution.get("iop", 0.0))
    meta = dict(meta or {})

    heights = []
    for i, p in enumerate(pressure):
        heights.append(float(md.get_h(p, iop, i)))

    if stents:
        for loc, stent in stents:
            end = min(len(heights), loc + len(stent) + 1)
            for i in range(max(0, loc), end):
                stent_i = max(0, i - loc)
                heights[i] = float(stent.h[min(stent_i, len(stent.h) - 1)])

    x_pressure = [float(i * md.dx / 1000.0) for i in range(len(pressure))]
    if ccs is not None and len(ccs) == len(jcc):
        x_jcc = [int(loc) for loc in ccs[:, 0]]
        jcc_x_title = "Collector channel node"
    else:
        x_jcc = list(range(len(jcc)))
        jcc_x_title = "Collector channel index"

    meta["total_nodes"] = len(pressure)
    meta["collector_channel_count"] = len(jcc)
    if ccs is not None:
        meta["ccs"] = [{"loc": int(loc), "ratio": float(ratio)} for loc, ratio in ccs]
    if stents:
        meta["stents"] = [
            {
                "loc": int(loc),
                "name": str(stent),
                "span_nodes": int(len(stent) + 1),
                "inlet_index": int(getattr(stent, "loc_inlet", 0)),
                "two_way": bool(getattr(stent, "two_way", False)),
            }
            for loc, stent in stents
        ]

    return {
        "metrics": {
            "iop": float(solution.get("iop", 0.0)),
            "flowrate": float(solution.get("flowrate", 0.0)),
            "resistance": float(solution.get("resistance", 0.0)),
            "facility": float(solution.get("facility", 0.0)),
        },
        "series": {
            "pressure": {"x": x_pressure, "y": pressure},
            "height": {"x": x_pressure, "y": heights},
            "jcc": {"x": x_jcc, "y": jcc, "x_title": jcc_x_title},
        },
        "meta": meta,
    }


def solve_payload(payload: dict) -> dict:
    mode = payload.get("mode", "constant flow")
    surgery = payload.get("surgery", "None")
    geometry = payload.get("geometry", "ellipse")
    meta = {}

    kwargs = {
        "geometry": geometry,
        "pev": finite_float(payload.get("pev"), 8.0),
    }

    optional_float_keys = ("etm", "h0", "hs", "rcc", "qu", "beta", "max_error")
    for key in optional_float_keys:
        value = finite_float(payload.get(key), None)
        if value is not None:
            kwargs[key] = value

    n_value = finite_float(payload.get("n"), None)
    if n_value is not None:
        kwargs["n"] = int(n_value)
    m_value = finite_float(payload.get("m"), None)
    if m_value is not None:
        kwargs["m"] = int(m_value)

    if payload.get("unconventional", False):
        kwargs["unconventional"] = True

    total_nodes = int(kwargs.get("n", 30)) * int(kwargs.get("m", 40))
    max_nodes = total_nodes

    rtm_node_values = parse_full_value_array(
        payload.get("rtm_node_values"),
        total_nodes,
        "TM full node array",
        allow_zero=False,
    )
    variable_rtm_profile = parse_segment_profile(payload.get("rtm_profile"), 12, "TM resistance", allow_zero=False)
    if rtm_node_values is not None:
        kwargs["variable_rtm"] = True
        kwargs["rtm"] = rtm_node_values
        meta["rtm_source"] = "tm_node_array"
        meta["tm_node_count"] = len(rtm_node_values)
    elif variable_rtm_profile is not None:
        kwargs["variable_rtm"] = True
        kwargs["rtm"] = expand_tm_profile(variable_rtm_profile, total_nodes)
        meta["rtm_source"] = "tm_profile"
        meta["tm_profile_segments"] = len(variable_rtm_profile)

    manual_rtm = finite_float(payload.get("rtm"), None)
    auto_rtm = finite_bool(payload.get("auto_rtm"), False)
    if rtm_node_values is None and variable_rtm_profile is None and auto_rtm and mode == "constant flow":
        baseline_iop = finite_float(payload.get("iop"), 15.09)
        derived_rtm = estimate_rtm_from_baseline_iop(baseline_iop, kwargs)
        kwargs["rtm"] = derived_rtm
        meta["rtm_source"] = "baseline_iop"
        meta["baseline_iop"] = baseline_iop
        meta["rtm_used"] = derived_rtm
    elif rtm_node_values is None and variable_rtm_profile is None and manual_rtm is not None:
        kwargs["rtm"] = manual_rtm
        meta["rtm_source"] = "manual"
        meta["rtm_used"] = manual_rtm

    h0_node_values = parse_full_value_array(
        payload.get("h0_node_values"),
        total_nodes,
        "SC full node array",
        allow_zero=True,
    )
    variable_h0_profile = parse_segment_profile(
        payload.get("h0_profile"),
        int(kwargs.get("n", 30)),
        "SC height",
        allow_zero=True,
    )
    if h0_node_values is not None:
        kwargs["variable_h0"] = True
        kwargs["h0"] = h0_node_values
        meta["h0_source"] = "sc_node_array"
        meta["sc_node_count"] = len(h0_node_values)
    elif variable_h0_profile is not None:
        kwargs["variable_h0"] = True
        kwargs["h0"] = expand_sc_profile(variable_h0_profile, total_nodes)
        meta["h0_source"] = "sc_profile"
        meta["sc_profile_segments"] = len(variable_h0_profile)

    tm_node_overrides = parse_node_value_overrides(
        payload.get("rtm_node_overrides"),
        max_nodes=total_nodes,
        label="TM resistance",
        allow_zero=False,
    )
    if tm_node_overrides:
        if kwargs.get("variable_rtm") and kwargs.get("rtm") is not None:
            tm_base = np.array(kwargs["rtm"], dtype=md.dt, copy=True)
        elif kwargs.get("rtm") is not None:
            tm_base = np.repeat(float(kwargs["rtm"]) * total_nodes, total_nodes).astype(md.dt)
        else:
            tm_base = np.repeat(2.0 * total_nodes, total_nodes).astype(md.dt)
        kwargs["variable_rtm"] = True
        kwargs["rtm"] = apply_node_value_overrides(tm_base, tm_node_overrides)
        meta["rtm_override_count"] = len(tm_node_overrides)
        meta["rtm_overrides"] = [
            {"start": int(start), "end": int(end), "value": float(value)}
            for start, end, value in tm_node_overrides
        ]

    h0_node_overrides = parse_node_value_overrides(
        payload.get("h0_node_overrides"),
        max_nodes=total_nodes,
        label="SC height",
        allow_zero=True,
    )
    if h0_node_overrides:
        if kwargs.get("variable_h0") and kwargs.get("h0") is not None:
            h0_base = np.array(kwargs["h0"], dtype=md.dt, copy=True)
        elif kwargs.get("h0") is not None:
            h0_base = np.repeat(float(kwargs["h0"]), total_nodes).astype(md.dt)
        else:
            h0_base = np.repeat(20.0, total_nodes).astype(md.dt)
        kwargs["variable_h0"] = True
        kwargs["h0"] = apply_node_value_overrides(h0_base, h0_node_overrides)
        meta["h0_override_count"] = len(h0_node_overrides)
        meta["h0_overrides"] = [
            {"start": int(start), "end": int(end), "value": float(value)}
            for start, end, value in h0_node_overrides
        ]

    gsc_multiplier_values, gsc_multiplier_overrides = parse_value_array_or_overrides(
        payload.get("gsc_multiplier"),
        total_nodes,
        "SC conductance multiplier",
        allow_zero=True,
    )
    if gsc_multiplier_values is not None:
        kwargs["gsc_multiplier"] = gsc_multiplier_values
        meta["gsc_multiplier_source"] = "full_array"
        meta["gsc_multiplier_count"] = len(gsc_multiplier_values)
    elif gsc_multiplier_overrides:
        gsc_multiplier_base = np.repeat(1.0, total_nodes).astype(md.dt)
        kwargs["gsc_multiplier"] = apply_node_value_overrides(gsc_multiplier_base, gsc_multiplier_overrides)
        meta["gsc_multiplier_source"] = "override_ranges"
        meta["gsc_multiplier_override_count"] = len(gsc_multiplier_overrides)

    gsc_override_values, gsc_override_overrides = parse_value_array_or_overrides(
        payload.get("gsc_override"),
        total_nodes,
        "SC conductance override",
        allow_zero=True,
    )
    if gsc_override_values is not None:
        kwargs["gsc_override"] = gsc_override_values
        meta["gsc_override_source"] = "full_array"
        meta["gsc_override_count"] = len(gsc_override_values)
    elif gsc_override_overrides:
        gsc_override_base = np.repeat(np.nan, total_nodes).astype(md.dt)
        kwargs["gsc_override"] = apply_node_value_overrides(gsc_override_base, gsc_override_overrides)
        meta["gsc_override_source"] = "override_ranges"
        meta["gsc_override_range_count"] = len(gsc_override_overrides)

    stents = None
    ccs = parse_ccs(payload.get("ccs"), max_nodes=max_nodes)
    explicit_trabeculotomies = parse_ranges(payload.get("trabeculotomies"))
    explicit_sinusotomies = parse_ranges(payload.get("sinusotomies"))
    explicit_yag_holes = parse_int_list(payload.get("yag_holes_list"))
    stent_nodes_text = payload.get("stent_nodes")
    if not stent_nodes_text and surgery == "iStent":
        stent_nodes_text = payload.get("stent_node", "0")
    explicit_stents = parse_stent_nodes(stent_nodes_text, payload)

    if explicit_trabeculotomies:
        meta["trabeculotomies"] = [{"start": int(start), "end": int(end)} for start, end in explicit_trabeculotomies]
        meta["trabeculotomy_source"] = "explicit"
    elif surgery == "Trabeculotomy":
        default_trab = default_trabeculotomies(int(finite_float(payload.get("trab_hours"), 1)))
        meta["trabeculotomies"] = [{"start": int(start), "end": int(end)} for start, end in default_trab]
        meta["trabeculotomy_source"] = "default_hours"

    if explicit_sinusotomies:
        meta["sinusotomies"] = [{"start": int(start), "end": int(end)} for start, end in explicit_sinusotomies]

    if explicit_yag_holes:
        meta["yag_holes"] = [int(node) for node in explicit_yag_holes]
        meta["yag_source"] = "explicit"
    elif surgery == "YAG holes":
        default_holes = default_yag_holes(int(finite_float(payload.get("yag_holes"), 2)))
        meta["yag_holes"] = [int(node) for node in default_holes]
        meta["yag_source"] = "default_count"

    if explicit_stents:
        meta["stent_count"] = len(explicit_stents)

    if explicit_sinusotomies:
        kwargs["sinusotomies"] = explicit_sinusotomies

    if ccs is not None:
        kwargs["ccs"] = ccs

    if explicit_stents:
        stents = explicit_stents
        kwargs["stents"] = stents

    with contextlib.redirect_stdout(io.StringIO()):
        if surgery == "Trabeculotomy":
            trab_kwargs = dict(kwargs)
            if explicit_trabeculotomies:
                trab_kwargs["trabeculotomies"] = explicit_trabeculotomies
            solution = ot.solve_trabeculotomy(
                iop=finite_float(payload.get("iop"), 7.0),
                qt=finite_float(payload.get("qt"), 2.0),
                hours=int(finite_float(payload.get("trab_hours"), 1)),
                mode=mode,
                show_height=False,
                **trab_kwargs,
            )
        elif surgery == "YAG holes":
            yag_kwargs = dict(kwargs)
            if explicit_yag_holes:
                yag_kwargs["holes"] = explicit_yag_holes
            yag_kwargs.pop("n", None)
            solution = ot.solve_yag_holes(
                iop=finite_float(payload.get("iop"), 7.0),
                qt=finite_float(payload.get("qt"), 2.0),
                n=int(finite_float(payload.get("yag_holes"), 2)),
                mode=mode,
                **yag_kwargs,
            )
        elif mode == "constant pressure":
            if explicit_trabeculotomies:
                kwargs["trabeculotomies"] = explicit_trabeculotomies
            if explicit_yag_holes:
                kwargs["yag_holes"] = explicit_yag_holes
            solution = ot.solve_cp(iop=finite_float(payload.get("iop"), 7.0), **kwargs)
        else:
            if explicit_trabeculotomies:
                kwargs["trabeculotomies"] = explicit_trabeculotomies
            if explicit_yag_holes:
                kwargs["yag_holes"] = explicit_yag_holes
            solution = ot.solve_cf(qt=finite_float(payload.get("qt"), 2.0), **kwargs)

    return solution_to_jsonable(solution, stents=stents, ccs=ccs, meta=meta)


def build_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Aqueous Outflow Local Calculator</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      --bg: #f4f7f2;
      --panel: #ffffff;
      --ink: #1e2521;
      --muted: #647067;
      --line: #d8dfd7;
      --accent: #147c72;
      --accent-dark: #0b5f58;
      --warn: #8a4b12;
      --soft-green: #dcece8;
      --soft-orange: #f1dfcf;
      --tm-low: #f1dece;
      --tm-high: #9a4f18;
      --sc-low: #eff5ea;
      --sc-high: #147c72;
      --trab: #1a9b73;
      --sinus: #d9782b;
      --stent: #2075b8;
      --yag: #bf3f6d;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Segoe UI", "Aptos", sans-serif;
      color: var(--ink);
      background:
        linear-gradient(135deg, rgba(20,124,114,0.10), rgba(136,164,92,0.10)),
        var(--bg);
    }
    .app {
      display: grid;
      grid-template-columns: 360px minmax(0, 1fr);
      min-height: 100vh;
    }
    aside {
      padding: 16px 16px 14px;
      border-right: 1px solid var(--line);
      background: rgba(255,255,255,0.84);
      display: flex;
      flex-direction: column;
      gap: 12px;
      min-height: 100vh;
    }
    .aside-scroll {
      flex: 1 1 auto;
      overflow-y: auto;
      padding-right: 4px;
    }
    .aside-actions {
      flex: 0 0 auto;
      padding-top: 10px;
      border-top: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(255,255,255,0), rgba(255,255,255,0.82) 28%, rgba(255,255,255,0.96));
    }
    main {
      display: grid;
      grid-template-rows: auto 1fr;
      min-width: 0;
      min-height: 0;
      padding: 18px;
      gap: 14px;
    }
    .dashboard {
      display: grid;
      grid-template-columns: 440px minmax(0, 1fr);
      gap: 14px;
      min-height: 0;
    }
    .visual-stack {
      display: grid;
      grid-template-rows: minmax(0, auto) minmax(0, auto);
      gap: 14px;
      min-height: 0;
      align-content: start;
    }
    h1 {
      margin: 0 0 6px;
      font-size: 22px;
      font-weight: 700;
    }
    .sub {
      margin: 0 0 18px;
      color: var(--muted);
      line-height: 1.45;
      font-size: 13px;
    }
    .panel {
      margin-bottom: 10px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: rgba(255,255,255,0.76);
      overflow: hidden;
      box-shadow: 0 6px 16px rgba(23, 44, 36, 0.03);
    }
    .panel summary {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      list-style: none;
      cursor: pointer;
      padding: 12px 14px;
      user-select: none;
      background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(247,250,246,0.88));
    }
    .panel summary::-webkit-details-marker {
      display: none;
    }
    .panel[open] summary {
      border-bottom: 1px solid var(--line);
    }
    .panel-head {
      min-width: 0;
    }
    .panel-head h2 {
      margin: 0 0 10px;
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: var(--muted);
    }
    .panel-head h2 {
      margin: 0;
      line-height: 1.2;
    }
    .panel-head p {
      margin: 5px 0 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }
    .panel-toggle {
      color: var(--muted);
      font-size: 12px;
      letter-spacing: .08em;
      text-transform: uppercase;
      flex: 0 0 auto;
    }
    .section-body {
      padding: 12px 14px 14px;
    }
    label {
      display: block;
      margin: 9px 0 5px;
      font-size: 13px;
      color: var(--muted);
    }
    input, select {
      width: 100%;
      height: 36px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 0 10px;
      color: var(--ink);
      background: white;
      font-size: 14px;
    }
    textarea {
      width: 100%;
      min-height: 54px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 10px;
      color: var(--ink);
      background: white;
      font: 14px "Segoe UI", "Aptos", sans-serif;
      resize: vertical;
    }
    .hint {
      margin-top: 5px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }
    .checkline {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 10px;
      color: var(--ink);
      font-size: 14px;
    }
    .checkline input {
      width: 16px;
      height: 16px;
    }
    button {
      width: 100%;
      height: 40px;
      border: 0;
      border-radius: 6px;
      margin-top: 14px;
      background: var(--accent);
      color: #fff;
      font-weight: 650;
      cursor: pointer;
    }
    button:hover { background: var(--accent-dark); }
    .solve-button {
      margin-top: 0;
      height: 44px;
      border-radius: 10px;
      font-size: 15px;
    }
    .grid2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .compact-label {
      margin-top: 6px;
    }
    .subtle-divider {
      height: 1px;
      margin: 12px 0 6px;
      background: linear-gradient(90deg, rgba(216,223,215,0.18), rgba(216,223,215,0.85), rgba(216,223,215,0.18));
    }
    .card {
      border: 1px solid var(--line);
      border-radius: 10px;
      background:
        linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,251,247,0.96));
      overflow: hidden;
      box-shadow: 0 10px 28px rgba(23, 44, 36, 0.04);
    }
    .card-head {
      padding: 14px 16px 10px;
      border-bottom: 1px solid rgba(216,223,215,0.8);
      background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(244,247,242,0.78));
    }
    .card-head h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 700;
    }
    .card-head p {
      margin: 5px 0 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
    }
    .ring-frame {
      padding: 12px 14px 14px;
    }
    .ring {
      display: block;
      width: 100%;
      height: auto;
    }
    .setup-summary,
    .solution-info,
    .solution-note {
      margin-top: 10px;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.76);
      font-size: 13px;
      line-height: 1.45;
    }
    .setup-summary {
      display: grid;
      gap: 4px;
    }
    .solution-info {
      display: grid;
      gap: 6px;
    }
    .solution-row {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      font-size: 13px;
    }
    .solution-row span:first-child {
      color: var(--muted);
    }
    .solution-note {
      color: var(--muted);
    }
    .legend {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px 12px;
      margin-top: 10px;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: var(--muted);
    }
    .swatch {
      width: 13px;
      height: 13px;
      border-radius: 999px;
      border: 1px solid rgba(0,0,0,0.08);
      flex: 0 0 auto;
    }
    .metrics {
      display: grid;
      grid-template-columns: repeat(4, minmax(120px, 1fr));
      gap: 10px;
    }
    .metric {
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.88);
    }
    .metric span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }
    .metric b {
      font-size: 22px;
      font-weight: 700;
    }
    .plot-wrap {
      min-height: 0;
      display: flex;
      flex-direction: column;
    }
    #plot {
      width: 100%;
      min-height: 720px;
      height: calc(100vh - 200px);
    }
    .status {
      min-height: 20px;
      margin-top: 10px;
      color: var(--warn);
      font-size: 13px;
      line-height: 1.35;
    }
    .hidden {
      display: none !important;
    }
    .ring-label {
      font-size: 12px;
      fill: var(--muted);
    }
    .ring-title {
      font-size: 14px;
      font-weight: 700;
      fill: var(--ink);
    }
    .anatomy-label {
      font-size: 10px;
      font-weight: 700;
      letter-spacing: .03em;
      fill: #47524c;
      text-transform: uppercase;
    }
    .anatomy-label-side {
      font-size: 9.5px;
      font-weight: 700;
      letter-spacing: .03em;
      fill: #47524c;
      text-transform: uppercase;
    }
    .anatomy-divider {
      stroke: rgba(71, 82, 76, 0.34);
      stroke-width: 1.4;
      stroke-dasharray: 4 4;
    }
    .anatomy-sector {
      opacity: 0.48;
    }
    .hoverable {
      cursor: pointer;
      transition: opacity 0.15s ease, stroke-width 0.15s ease;
    }
    .hoverable:hover {
      opacity: 0.86;
    }
    @media (max-width: 900px) {
      .app { grid-template-columns: 1fr; }
      aside { border-right: 0; border-bottom: 1px solid var(--line); }
      .metrics { grid-template-columns: 1fr 1fr; }
      .dashboard { grid-template-columns: 1fr; }
      #plot { min-height: 520px; height: 520px; }
      .legend { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <div class="aside-scroll">
        <h1>Aqueous Outflow Model</h1>
        <p class="sub">Pure local calculator. The browser talks to this Python server, and the server calls the local solver.</p>

        <details class="panel" id="panel_solver" open>
          <summary>
            <div class="panel-head">
              <h2>Solver</h2>
              <p>Mode, pressure-flow target, and baseline resistance.</p>
            </div>
            <span class="panel-toggle">Core</span>
          </summary>
          <div class="section-body">
            <label>Mode</label>
            <select id="mode">
              <option value="constant flow">constant flow</option>
              <option value="constant pressure">constant pressure</option>
            </select>
            <div class="grid2">
              <div>
                <label>Geometry</label>
                <select id="geometry">
                  <option value="ellipse">ellipse</option>
                  <option value="rectangle">rectangle</option>
                </select>
              </div>
              <div>
                <label>Eye</label>
                <select id="eye_side">
                  <option value="right">Right Eye (OD)</option>
                  <option value="left">Left Eye (OS)</option>
                </select>
              </div>
            </div>
            <div class="grid2">
              <div>
                <label id="iop_label">Baseline IOP</label>
                <input id="iop" type="number" step="0.1" value="15.09" />
              </div>
              <div><label>Qt</label><input id="qt" type="number" step="0.1" value="2.0" /></div>
            </div>
            <div id="iop_hint" class="hint">In constant flow mode, this is used to estimate baseline TM resistance when Auto RTM is enabled.</div>
            <div class="grid2">
              <div><label>Pev</label><input id="pev" type="number" step="0.1" value="8.0" /></div>
              <div><label>Rtm</label><input id="rtm" type="number" step="0.1" placeholder="default" /></div>
            </div>
            <div class="checkline"><input id="auto_rtm" type="checkbox" checked /><span>Auto RTM from baseline IOP</span></div>
            <div class="hint">Matches the online calculator idea: infer Rtm from a baseline eye with no surgeries and default CC distribution.</div>
          </div>
        </details>

        <details class="panel" id="panel_intervention" open>
          <summary>
            <div class="panel-head">
              <h2>Intervention</h2>
              <p>Collector-channel layout and surgery-specific inputs.</p>
            </div>
            <span class="panel-toggle">Main</span>
          </summary>
          <div class="section-body">
            <label>Surgery</label>
            <select id="surgery">
              <option>None</option>
              <option>Trabeculotomy</option>
              <option>YAG holes</option>
              <option>iStent</option>
            </select>
            <div id="surgery_defaults" class="grid2">
              <div id="trab_hours_wrap">
                <label>Trab hours</label>
                <select id="trab_hours">
                  <option>1</option>
                  <option>4</option>
                  <option>12</option>
                </select>
              </div>
              <div id="yag_count_wrap">
                <label>YAG holes</label><input id="yag_holes" type="number" step="1" value="2" />
              </div>
            </div>
            <input id="stent_node" type="hidden" value="0" />

            <label>Trabeculotomy ranges</label>
            <textarea id="trabeculotomies" placeholder="Example: 0-99, 300-399"></textarea>
            <div id="trabeculotomy_hint" class="hint">Ranges are SC node indexes. Leave blank to use Trab hours when Surgery is Trabeculotomy.</div>

            <label>Sinusotomy ranges</label>
            <textarea id="sinusotomies" placeholder="Example: 120-180, 620-700"></textarea>
            <div class="hint">Sinusotomy ranges can be combined with any selected surgery.</div>

            <label>YAG hole nodes</label>
            <input id="yag_holes_list" type="text" placeholder="Example: 0, 200, 400" />
            <div id="yag_nodes_hint" class="hint">Leave blank to use the YAG hole count above when Surgery is YAG holes.</div>

            <label>iStent nodes</label>
            <input id="stent_nodes" type="text" placeholder="Example: 0, 300, 600" />
            <div id="stent_nodes_hint" class="hint">Each node gets the stent model configured below. If Surgery is iStent and this is blank, node 0 is used.</div>
          </div>
        </details>

        <details class="panel" id="panel_constants">
          <summary>
            <div class="panel-head">
              <h2>Constants</h2>
              <p>Equivalent to the online app's Edit Constants drawer.</p>
            </div>
            <span class="panel-toggle">Advanced</span>
          </summary>
          <div class="section-body">
            <div class="grid2">
              <div><label>N collector channels</label><input id="n" type="number" step="1" value="30" /></div>
              <div><label>M nodes per CC</label><input id="m" type="number" step="1" value="40" /></div>
            </div>
            <div class="grid2">
              <div><label>Etm</label><input id="etm" type="number" step="0.1" value="13" /></div>
              <div><label>h0 (um)</label><input id="h0" type="number" step="0.1" value="20" /></div>
            </div>
            <div class="grid2">
              <div><label>hs (um)</label><input id="hs" type="number" step="0.1" value="3.0" /></div>
              <div><label>Rcc override</label><input id="rcc" type="number" step="0.1" placeholder="auto" /></div>
            </div>
            <div class="grid2">
              <div><label>Qu</label><input id="qu" type="number" step="0.01" value="0.28" /></div>
              <div><label>max error</label><input id="max_error" type="number" step="0.00001" value="0.0001" /></div>
            </div>
            <div class="grid2">
              <div><label>Stent beta</label><input id="beta" type="number" step="0.1" placeholder="1.0" /></div>
              <div class="checkline"><input id="unconventional" type="checkbox" /><span>Use unconventional flow</span></div>
            </div>
          </div>
        </details>

        <details class="panel" id="panel_profiles">
          <summary>
            <div class="panel-head">
              <h2>Segment Profiles</h2>
              <p>Clock-hour TM resistance and segment-wise SC baseline height.</p>
            </div>
            <span class="panel-toggle">Advanced</span>
          </summary>
          <div class="section-body">
            <label>TM resistance profile</label>
            <textarea id="rtm_profile" placeholder="Examples: 24 or 24,24,24,... (12 values) or 1:24, 2:30, ..., 12:24"></textarea>
            <div class="hint">Takes 12 clock-hour values. If provided, this overrides scalar RTM and auto RTM.</div>
            <div class="subtle-divider"></div>
            <label>TM full node array</label>
            <textarea id="rtm_node_values" placeholder="Examples: 2400 or 2400,2400,... (N*M values)"></textarea>
            <div class="hint">Direct local TM resistor values for every SC node. Use 1 value to repeat uniformly or exactly N*M values to import a fully non-uniform TM map.</div>
            <div class="subtle-divider"></div>
            <label>SC baseline height profile</label>
            <textarea id="h0_profile" placeholder="Examples: 20 or 20,20,20,... (N values) or 1:20, 2:18, ..., N:20"></textarea>
            <div class="hint">Takes N segment values, where N is the current collector-channel count. If provided, this overrides scalar h0.</div>
            <div class="subtle-divider"></div>
            <label>SC full node array</label>
            <textarea id="h0_node_values" placeholder="Examples: 20 or 20,20,... (N*M values)"></textarea>
            <div class="hint">Direct baseline SC height at every node. Use 1 value to repeat uniformly or exactly N*M values for a fully non-uniform SC baseline map.</div>
            <div class="subtle-divider"></div>
            <label>TM node resistance overrides</label>
            <textarea id="rtm_node_overrides" placeholder="Examples: 120:2400, 121-140:3200"></textarea>
            <div class="hint">Format is node:value or start-end:value. Values are local per-node TM resistors, so these apply after auto RTM, scalar RTM, or the 12-segment TM profile.</div>
            <div class="subtle-divider"></div>
            <label>SC node height overrides</label>
            <textarea id="h0_node_overrides" placeholder="Examples: 120:20, 121-140:14"></textarea>
            <div class="hint">Use this to locally change the SC baseline height at arbitrary nodes. This is the closest direct way to modify local SC circumferential resistance in the current solver.</div>
            <div class="subtle-divider"></div>
            <label>SC conductance multiplier</label>
            <textarea id="gsc_multiplier" placeholder="Examples: 1.0 or 1.0,1.0,... (N*M values) or 120:0.5, 121-140:2.0"></textarea>
            <div class="hint">Applies a multiplicative factor to each circumferential SC segment conductance between node i and i+1. Accepts either 1/exact N*M values or segment:value overrides.</div>
            <div class="subtle-divider"></div>
            <label>SC conductance override</label>
            <textarea id="gsc_override" placeholder="Examples: 0.002 or 0.002,0.002,... (N*M values) or 120:0.0, 121-140:0.003"></textarea>
            <div class="hint">Directly replaces the computed conductance of selected SC segments. Segment i means the link between node i and node i+1. This overrides the height-based conductance calculation for those segments.</div>
          </div>
        </details>

        <details class="panel" id="panel_ccs">
          <summary>
            <div class="panel-head">
              <h2>Collector Channels</h2>
              <p>Manual non-uniform distribution, closer to the online editor.</p>
            </div>
            <span class="panel-toggle">Advanced</span>
          </summary>
          <div class="section-body">
            <label>Manual CC distribution</label>
            <textarea id="ccs" placeholder="Example: 0:1, 40:1, 80:0.5, 120:2"></textarea>
            <div class="hint">Format is node:relative conductance. Use commas or semicolons. Leave blank for the uniform default from N and M.</div>
            <div class="hint">If only a node is provided, ratio defaults to 1; for example 0, 40, 80.</div>
          </div>
        </details>

        <details class="panel" id="panel_stent">
          <summary>
            <div class="panel-head">
              <h2>Stent Editor</h2>
              <p>Custom geometry for iStent-style local simulations.</p>
            </div>
            <span class="panel-toggle">Advanced</span>
          </summary>
          <div class="section-body">
            <label>Name</label>
            <input id="stent_name" type="text" value="Custom iStent" />
            <div class="grid2">
              <div><label>Length (um)</label><input id="stent_length" type="number" step="10" value="1000" /></div>
              <div><label>Inlet offset (um)</label><input id="stent_loc_inlet" type="number" step="10" value="0" /></div>
            </div>
            <div class="grid2">
              <div><label>Width (um)</label><input id="stent_width" type="number" step="1" value="120" /></div>
              <div><label>Height (um)</label><input id="stent_height" type="number" step="1" value="60" /></div>
            </div>
            <div class="grid2">
              <div><label>Before dilation nodes</label><input id="stent_l_before" type="number" step="1" value="0" /></div>
              <div><label>After dilation nodes</label><input id="stent_l_after" type="number" step="1" value="0" /></div>
            </div>
            <div class="grid2">
              <div><label>After height (um)</label><input id="stent_h_after" type="number" step="1" placeholder="same as height" /></div>
              <div><label>Inlet conductance</label><input id="stent_g_inlet" type="number" step="0.001" value="0" /></div>
            </div>
            <div class="grid2">
              <div>
                <label>Stent geometry</label>
                <select id="stent_geometry">
                  <option value="">same as solver</option>
                  <option value="ellipse">ellipse</option>
                  <option value="rectangle">rectangle</option>
                </select>
              </div>
              <div class="checkline"><input id="stent_two_way" type="checkbox" checked /><span>Two-way inlet</span></div>
            </div>
            <div class="subtle-divider"></div>
            <label>Windowed stent options</label>
            <div class="grid2">
              <div><label class="compact-label">Number of windows</label><input id="stent_n_windows" type="number" step="1" value="0" /></div>
              <div><label class="compact-label">Window length (um)</label><input id="stent_l_window" type="number" step="10" placeholder="required if windows > 0" /></div>
            </div>
            <div class="grid2">
              <div><label>Window height (um)</label><input id="stent_h_window" type="number" step="1" placeholder="required if windows > 0" /></div>
              <div><label>Spine length (um)</label><input id="stent_l_spine" type="number" step="10" placeholder="required if windows > 0" /></div>
            </div>
            <label>Spine height (um)</label>
            <input id="stent_h_spine" type="number" step="1" placeholder="required if windows > 0" />
            <div class="hint">For a simple iStent, leave window count at 0. For devices with windows/spines, fill all windowed stent fields.</div>
          </div>
        </details>

        <details class="panel" id="panel_plot" open>
          <summary>
            <div class="panel-head">
              <h2>Plot</h2>
              <p>Choose which profile is shown in the line chart.</p>
            </div>
            <span class="panel-toggle">View</span>
          </summary>
          <div class="section-body">
            <label>Plot type</label>
            <select id="plot_type">
              <option value="pressure">Pressure distribution</option>
              <option value="height">Canal height</option>
              <option value="jcc">Collector channel flow</option>
            </select>
            <div id="status" class="status"></div>
          </div>
        </details>
      </div>

      <div class="aside-actions">
        <button id="solveBtn" class="solve-button">Solve locally</button>
      </div>
    </aside>

    <main>
      <div class="metrics">
        <div class="metric"><span>IOP</span><b id="m_iop">-</b></div>
        <div class="metric"><span>Flow rate</span><b id="m_flowrate">-</b></div>
        <div class="metric"><span>Resistance</span><b id="m_resistance">-</b></div>
        <div class="metric"><span>Facility</span><b id="m_facility">-</b></div>
      </div>
      <div class="dashboard">
        <div class="visual-stack">
          <section class="card">
            <div class="card-head">
              <h3>Setup Ring</h3>
              <p>Local circular preview of the current collector-channel layout, segment profiles, and interventions.</p>
            </div>
            <div class="ring-frame">
              <svg id="setup_svg" class="ring" viewBox="0 0 420 420"></svg>
              <div id="setup_summary" class="setup-summary"></div>
              <div class="legend">
                <div class="legend-item"><span class="swatch" style="background: var(--trab);"></span><span>Trabeculotomy</span></div>
                <div class="legend-item"><span class="swatch" style="background: var(--sinus);"></span><span>Sinusotomy</span></div>
                <div class="legend-item"><span class="swatch" style="background: var(--stent);"></span><span>Stent span</span></div>
                <div class="legend-item"><span class="swatch" style="background: var(--yag);"></span><span>YAG hole</span></div>
              </div>
            </div>
          </section>

          <section class="card">
            <div class="card-head">
              <h3>Solution Ring</h3>
              <p>Pressure heatmap, canal-height ring, and collector-channel flow from the latest local solve.</p>
            </div>
            <div class="ring-frame">
              <svg id="solution_svg" class="ring" viewBox="0 0 520 420"></svg>
              <div id="solution_note" class="solution-note">Waiting for the first solve.</div>
              <div id="solution_info" class="solution-info">Hover the pressure ring or a collector channel to inspect local values.</div>
            </div>
          </section>
        </div>

        <section class="card plot-wrap">
          <div class="card-head">
            <h3>Profiles</h3>
            <p>Line plots for circumferential pressure, canal height, and collector-channel flow.</p>
          </div>
          <div id="plot"></div>
        </section>
      </div>
    </main>
  </div>

  <script>
    const $ = (id) => document.getElementById(id);
    let lastResult = null;
    let lastSolvedPayload = null;
    let resultDirty = false;

    function payload() {
      return {
        mode: $("mode").value,
        geometry: $("geometry").value,
        iop: $("iop").value,
        qt: $("qt").value,
        pev: $("pev").value,
        rtm: $("rtm").value,
        auto_rtm: $("auto_rtm").checked,
        n: $("n").value,
        m: $("m").value,
        etm: $("etm").value,
        h0: $("h0").value,
        h0_profile: $("h0_profile").value,
        hs: $("hs").value,
        rcc: $("rcc").value,
        qu: $("qu").value,
        max_error: $("max_error").value,
        beta: $("beta").value,
        unconventional: $("unconventional").checked,
        ccs: $("ccs").value,
        rtm_profile: $("rtm_profile").value,
        rtm_node_values: $("rtm_node_values").value,
        rtm_node_overrides: $("rtm_node_overrides").value,
        h0_node_values: $("h0_node_values").value,
        h0_node_overrides: $("h0_node_overrides").value,
        gsc_multiplier: $("gsc_multiplier").value,
        gsc_override: $("gsc_override").value,
        surgery: $("surgery").value,
        trab_hours: $("trab_hours").value,
        trabeculotomies: $("trabeculotomies").value,
        sinusotomies: $("sinusotomies").value,
        yag_holes: $("yag_holes").value,
        yag_holes_list: $("yag_holes_list").value,
        stent_node: $("stent_node").value,
        stent_nodes: $("stent_nodes").value,
        stent_name: $("stent_name").value,
        stent_length: $("stent_length").value,
        stent_loc_inlet: $("stent_loc_inlet").value,
        stent_width: $("stent_width").value,
        stent_height: $("stent_height").value,
        stent_l_before: $("stent_l_before").value,
        stent_l_after: $("stent_l_after").value,
        stent_h_after: $("stent_h_after").value,
        stent_g_inlet: $("stent_g_inlet").value,
        stent_geometry: $("stent_geometry").value,
        stent_two_way: $("stent_two_way").checked,
        stent_n_windows: $("stent_n_windows").value,
        stent_l_window: $("stent_l_window").value,
        stent_h_window: $("stent_h_window").value,
        stent_l_spine: $("stent_l_spine").value,
        stent_h_spine: $("stent_h_spine").value,
      };
    }

    function numberValue(value, fallback = null) {
      const num = Number(value);
      return Number.isFinite(num) ? num : fallback;
    }

    function fmt(value) {
      if (!Number.isFinite(value)) return "-";
      return Number(value).toPrecision(5);
    }

    function eyeLabels() {
      const rightEye = $("eye_side").value !== "left";
      return {
        eye: rightEye ? "Right Eye (OD)" : "Left Eye (OS)",
        left: rightEye ? "Temporal" : "Nasal",
        right: rightEye ? "Nasal" : "Temporal",
      };
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");
    }

    function clamp(value, low, high) {
      return Math.min(high, Math.max(low, value));
    }

    function hexToRgb(hex) {
      const clean = String(hex).replace("#", "");
      return {
        r: Number.parseInt(clean.slice(0, 2), 16),
        g: Number.parseInt(clean.slice(2, 4), 16),
        b: Number.parseInt(clean.slice(4, 6), 16),
      };
    }

    function mixColors(a, b, t) {
      const left = hexToRgb(a);
      const right = hexToRgb(b);
      const ratio = clamp(t, 0, 1);
      const c = (x, y) => Math.round(x + (y - x) * ratio);
      return `rgb(${c(left.r, right.r)}, ${c(left.g, right.g)}, ${c(left.b, right.b)})`;
    }

    function polarPoint(cx, cy, radius, degrees) {
      const radians = (degrees - 90) * Math.PI / 180;
      return {
        x: cx + radius * Math.cos(radians),
        y: cy + radius * Math.sin(radians),
      };
    }

    function arcPath(cx, cy, radius, startDeg, spanDeg) {
      const span = clamp(spanDeg, 0.2, 359.8);
      const start = polarPoint(cx, cy, radius, startDeg);
      const end = polarPoint(cx, cy, radius, startDeg + span);
      const largeArc = span > 180 ? 1 : 0;
      return `M ${start.x.toFixed(2)} ${start.y.toFixed(2)} A ${radius} ${radius} 0 ${largeArc} 1 ${end.x.toFixed(2)} ${end.y.toFixed(2)}`;
    }

    function annularSectorPath(cx, cy, innerRadius, outerRadius, startDeg, spanDeg) {
      const span = clamp(spanDeg, 0.2, 359.8);
      const outerStart = polarPoint(cx, cy, outerRadius, startDeg);
      const outerEnd = polarPoint(cx, cy, outerRadius, startDeg + span);
      const innerEnd = polarPoint(cx, cy, innerRadius, startDeg + span);
      const innerStart = polarPoint(cx, cy, innerRadius, startDeg);
      const largeArc = span > 180 ? 1 : 0;
      return [
        `M ${outerStart.x.toFixed(2)} ${outerStart.y.toFixed(2)}`,
        `A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${outerEnd.x.toFixed(2)} ${outerEnd.y.toFixed(2)}`,
        `L ${innerEnd.x.toFixed(2)} ${innerEnd.y.toFixed(2)}`,
        `A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${innerStart.x.toFixed(2)} ${innerStart.y.toFixed(2)}`,
        "Z",
      ].join(" ");
    }

    function anatomyColors() {
      return {
        Superior: "rgba(102, 167, 214, 0.22)",
        Inferior: "rgba(165, 132, 201, 0.20)",
        Temporal: "rgba(221, 166, 94, 0.20)",
        Nasal: "rgba(106, 176, 117, 0.20)",
      };
    }

    function drawTicks(cx, cy, radius) {
      const parts = [];
      for (let deg = 0; deg < 360; deg += 10) {
        const isMajor = deg % 20 === 0;
        const inner = polarPoint(cx, cy, radius - (isMajor ? 14 : 8), deg);
        const outer = polarPoint(cx, cy, radius, deg);
        parts.push(`<line x1="${inner.x.toFixed(2)}" y1="${inner.y.toFixed(2)}" x2="${outer.x.toFixed(2)}" y2="${outer.y.toFixed(2)}" stroke="#7c877f" stroke-width="${isMajor ? 1.8 : 1}" opacity="0.85"></line>`);
        if (isMajor) {
          const text = polarPoint(cx, cy, radius - 24, deg);
          parts.push(`<text x="${text.x.toFixed(2)}" y="${text.y.toFixed(2)}" text-anchor="middle" dominant-baseline="central" class="ring-label">${deg}°</text>`);
        }
      }
      return parts.join("");
    }

    function drawAnatomyOverlay(cx, cy, innerRadius, outerRadius, frameWidth) {
      const labels = eyeLabels();
      const boundaries = [45, 135, 225, 315];
      const parts = [];
      const colors = anatomyColors();

      parts.push(`<path class="anatomy-sector" d="${annularSectorPath(cx, cy, innerRadius, outerRadius, 315, 90)}" fill="${colors.Superior}"></path>`);
      parts.push(`<path class="anatomy-sector" d="${annularSectorPath(cx, cy, innerRadius, outerRadius, 45, 90)}" fill="${colors[labels.right]}"></path>`);
      parts.push(`<path class="anatomy-sector" d="${annularSectorPath(cx, cy, innerRadius, outerRadius, 135, 90)}" fill="${colors.Inferior}"></path>`);
      parts.push(`<path class="anatomy-sector" d="${annularSectorPath(cx, cy, innerRadius, outerRadius, 225, 90)}" fill="${colors[labels.left]}"></path>`);

      boundaries.forEach((degrees) => {
        const inner = polarPoint(cx, cy, innerRadius, degrees);
        const outer = polarPoint(cx, cy, outerRadius, degrees);
        parts.push(`<line class="anatomy-divider" x1="${inner.x.toFixed(2)}" y1="${inner.y.toFixed(2)}" x2="${outer.x.toFixed(2)}" y2="${outer.y.toFixed(2)}"></line>`);
      });

      const leftX = Math.max(20, cx - outerRadius - 44);
      const rightX = Math.min(frameWidth - 20, cx + outerRadius + 44);

      parts.push(`<text x="${cx.toFixed(2)}" y="${(cy - outerRadius - 34).toFixed(2)}" text-anchor="middle" dominant-baseline="central" class="anatomy-label">Superior</text>`);
      parts.push(`<text x="${cx.toFixed(2)}" y="${(cy + outerRadius + 34).toFixed(2)}" text-anchor="middle" dominant-baseline="central" class="anatomy-label">Inferior</text>`);
      parts.push(`<text x="${leftX.toFixed(2)}" y="${cy.toFixed(2)}" text-anchor="start" dominant-baseline="central" class="anatomy-label-side">${labels.left}</text>`);
      parts.push(`<text x="${rightX.toFixed(2)}" y="${cy.toFixed(2)}" text-anchor="end" dominant-baseline="central" class="anatomy-label-side">${labels.right}</text>`);
      return parts.join("");
    }

    function anatomyAxisGuide(series) {
      if (!series || !Array.isArray(series.x) || !series.x.length) return null;
      const minX = Math.min(...series.x);
      const maxX = Math.max(...series.x);
      if (!Number.isFinite(minX) || !Number.isFinite(maxX) || maxX <= minX) return null;

      const labels = eyeLabels();
      const span = maxX - minX;
      const quarters = [0, 0.25, 0.5, 0.75, 1].map((ratio) => minX + span * ratio);
      const tickText = [
        `${fmt(minX)}<br><b>Superior</b>`,
        `${fmt(minX + span * 0.25)}<br><b>${labels.right}</b>`,
        `${fmt(minX + span * 0.5)}<br><b>Inferior</b>`,
        `${fmt(minX + span * 0.75)}<br><b>${labels.left}</b>`,
        `${fmt(maxX)}<br><b>Superior</b>`,
      ];
      const colors = anatomyColors();
      const boundaries = [0.125, 0.375, 0.625, 0.875].map((ratio) => minX + span * ratio);
      const regions = [
        { x0: minX, x1: minX + span * 0.125, name: "Superior" },
        { x0: minX + span * 0.125, x1: minX + span * 0.375, name: labels.right },
        { x0: minX + span * 0.375, x1: minX + span * 0.625, name: "Inferior" },
        { x0: minX + span * 0.625, x1: minX + span * 0.875, name: labels.left },
        { x0: minX + span * 0.875, x1: maxX, name: "Superior" },
      ];
      return {
        tickvals: quarters,
        ticktext: tickText,
        shapes: [
          ...regions.map((region) => ({
            type: "rect",
            xref: "x",
            yref: "paper",
            x0: region.x0,
            x1: region.x1,
            y0: 0,
            y1: 1,
            fillcolor: colors[region.name],
            line: { width: 0 },
            layer: "below",
          })),
          ...boundaries.map((x) => ({
            type: "line",
            xref: "x",
            yref: "paper",
            x0: x,
            x1: x,
            y0: 0,
            y1: 1,
            line: { color: "rgba(71, 82, 76, 0.15)", width: 1, dash: "dot" },
          })),
        ],
      };
    }

    function parseRangesText(text) {
      if (!text || !String(text).trim()) return [];
      const values = [];
      for (const chunk of String(text).replaceAll(";", ",").split(",")) {
        const part = chunk.trim();
        if (!part) continue;
        let start = 0;
        let end = 0;
        if (part.includes("-")) {
          const [left, right] = part.split("-", 2);
          start = Math.round(Number(left.trim()));
          end = Math.round(Number(right.trim()));
        } else if (part.includes(":")) {
          const [left, right] = part.split(":", 2);
          start = Math.round(Number(left.trim()));
          end = Math.round(Number(right.trim()));
        } else {
          start = end = Math.round(Number(part));
        }
        if (Number.isFinite(start) && Number.isFinite(end)) {
          if (end < start) [start, end] = [end, start];
          values.push({ start, end });
        }
      }
      return values;
    }

    function parseNodeListText(text) {
      if (!text || !String(text).trim()) return [];
      return String(text)
        .replaceAll(";", ",")
        .split(",")
        .map((part) => Math.round(Number(part.trim())))
        .filter((value) => Number.isFinite(value));
    }

    function parseCCsText(text) {
      if (!text || !String(text).trim()) return [];
      const ccs = [];
      for (const chunk of String(text).replaceAll(";", ",").split(",")) {
        const part = chunk.trim();
        if (!part) continue;
        let locText = part;
        let ratioText = "1";
        if (part.includes(":")) {
          [locText, ratioText] = part.split(":", 2);
        } else if (part.includes("=")) {
          [locText, ratioText] = part.split("=", 2);
        }
        const loc = Math.round(Number(locText.trim()));
        const ratio = Number(ratioText.trim());
        if (Number.isFinite(loc) && Number.isFinite(ratio)) {
          ccs.push({ loc, ratio });
        }
      }
      return ccs;
    }

    function parseProfileValues(text, expectedCount) {
      if (!text || !String(text).trim() || !expectedCount) return null;
      const chunks = String(text)
        .replaceAll(";", ",")
        .replaceAll("\\n", ",")
        .split(",")
        .map((part) => part.trim())
        .filter(Boolean);
      if (!chunks.length) return null;

      const keyed = chunks.some((part) => part.includes(":") || part.includes("="));
      if (keyed) {
        const values = Array(expectedCount).fill(null);
        for (const chunk of chunks) {
          const divider = chunk.includes(":") ? ":" : "=";
          const [indexText, valueText] = chunk.split(divider, 2);
          const index = Math.round(Number(indexText.trim())) - 1;
          const value = Number(valueText.trim());
          if (index >= 0 && index < expectedCount && Number.isFinite(value)) {
            values[index] = value;
          }
        }
        return values.every((value) => Number.isFinite(value)) ? values : null;
      }

      const raw = chunks.map((chunk) => Number(chunk)).filter((value) => Number.isFinite(value));
      if (!raw.length) return null;
      if (raw.length === 1) return Array(expectedCount).fill(raw[0]);
      if (raw.length === expectedCount) return raw;
      return null;
    }

    function defaultTrabeculotomies(hours) {
      if (hours === 1) return [{ start: 550, end: 650 }];
      if (hours === 4) return [{ start: 100, end: 200 }, { start: 400, end: 500 }, { start: 700, end: 800 }, { start: 1000, end: 1100 }];
      if (hours === 12) return [{ start: 0, end: 1199 }];
      return [];
    }

    function defaultYagHoles(count) {
      const defaults = {
        0: [],
        1: [600],
        2: [300, 900],
        3: [200, 600, 1000],
        4: [150, 450, 750, 1050],
        5: [120, 360, 600, 840, 1080],
        6: [100, 300, 500, 700, 900, 1100],
      };
      return defaults[count] || [];
    }

    function normalizeNode(node, totalNodes) {
      if (!totalNodes) return 0;
      const rounded = Math.round(Number(node) || 0);
      return ((rounded % totalNodes) + totalNodes) % totalNodes;
    }

    function inferCollectorNodes(currentPayload, result, totalNodes) {
      if (result?.meta?.ccs?.length) return result.meta.ccs.map((cc) => ({ loc: cc.loc, ratio: cc.ratio }));
      const explicit = parseCCsText(currentPayload.ccs);
      if (explicit.length) return explicit;
      const mValue = Math.max(1, Math.round(numberValue(currentPayload.m, 40) || 40));
      const count = Math.max(1, Math.round(numberValue(currentPayload.n, Math.max(1, Math.floor(totalNodes / mValue))) || 30));
      return Array.from({ length: count }, (_, idx) => ({ loc: idx * mValue, ratio: 1 }));
    }

    function estimatePendingStentSpan(currentPayload) {
      const lengthUm = Math.max(30, numberValue(currentPayload.stent_length, 1000) || 1000);
      const beforeNodes = Math.max(0, Math.round(numberValue(currentPayload.stent_l_before, 0) || 0));
      const afterNodes = Math.max(0, Math.round(numberValue(currentPayload.stent_l_after, 0) || 0));
      return Math.max(1, Math.round(lengthUm / 30)) + beforeNodes + afterNodes + 1;
    }

    function collectSetupModel(currentPayload, result) {
      const totalNodes = Math.max(1, Math.round(result?.meta?.total_nodes || result?.series?.pressure?.y?.length || ((numberValue(currentPayload.n, 30) || 30) * (numberValue(currentPayload.m, 40) || 40))));
      const ccs = inferCollectorNodes(currentPayload, result, totalNodes);
      const nSegments = Math.max(1, Math.round(numberValue(currentPayload.n, ccs.length || 30) || 30));

      let trabeculotomies = [];
      if (result?.meta?.trabeculotomies?.length) {
        trabeculotomies = result.meta.trabeculotomies;
      } else {
        trabeculotomies = parseRangesText(currentPayload.trabeculotomies);
        if (!trabeculotomies.length && currentPayload.surgery === "Trabeculotomy") {
          trabeculotomies = defaultTrabeculotomies(Math.round(numberValue(currentPayload.trab_hours, 1) || 1));
        }
      }

      let yagHoles = [];
      if (result?.meta?.yag_holes?.length) {
        yagHoles = result.meta.yag_holes;
      } else {
        yagHoles = parseNodeListText(currentPayload.yag_holes_list);
        if (!yagHoles.length && currentPayload.surgery === "YAG holes") {
          yagHoles = defaultYagHoles(Math.round(numberValue(currentPayload.yag_holes, 2) || 2));
        }
      }

      let stents = [];
      if (result?.meta?.stents?.length) {
        stents = result.meta.stents;
      } else {
        let nodesText = currentPayload.stent_nodes;
        if (!nodesText && currentPayload.surgery === "iStent") nodesText = currentPayload.stent_node || "0";
        const nodes = parseNodeListText(nodesText);
        const span = estimatePendingStentSpan(currentPayload);
        stents = nodes.map((loc) => ({
          loc,
          name: currentPayload.stent_name || "Custom iStent",
          span_nodes: span,
          inlet_index: Math.max(0, Math.round(numberValue(currentPayload.stent_l_before, 0) || 0)),
          two_way: !!currentPayload.stent_two_way,
        }));
      }

      return {
        totalNodes,
        ccs,
        trabeculotomies,
        sinusotomies: result?.meta?.sinusotomies || parseRangesText(currentPayload.sinusotomies),
        yagHoles,
        stents,
        tmProfile: parseProfileValues(currentPayload.rtm_node_values, totalNodes) || parseProfileValues(currentPayload.rtm_profile, 12),
        scProfile: parseProfileValues(currentPayload.h0_node_values, totalNodes) || parseProfileValues(currentPayload.h0_profile, nSegments),
        hasGscControl: !!(String(currentPayload.gsc_multiplier || "").trim() || String(currentPayload.gsc_override || "").trim()),
        surgery: currentPayload.surgery,
      };
    }

    function rangeSpanNodes(range) {
      return Math.max(1, (range.end - range.start + 1));
    }

    function buildSetupSummary(model) {
      const labels = eyeLabels();
      const lines = [];
      lines.push(`<div><b>${model.ccs.length}</b> collector channels across <b>${model.totalNodes}</b> SC nodes.</div>`);
      lines.push(`<div>Interventions: trab <b>${model.trabeculotomies.length}</b>, sinus <b>${model.sinusotomies.length}</b>, YAG <b>${model.yagHoles.length}</b>, stents <b>${model.stents.length}</b>.</div>`);
      lines.push(`<div>Profiles: TM ${model.tmProfile ? "<b>variable</b>" : "scalar"} | SC height ${model.scProfile ? "<b>variable</b>" : "scalar"}.</div>`);
      if (model.hasGscControl) lines.push(`<div>SC circumferential conductance: <b>customized</b>.</div>`);
      lines.push(`<div>Eye orientation: <b>${labels.eye}</b> with <b>${labels.left}</b> on the left and <b>${labels.right}</b> on the right.</div>`);
      $("setup_summary").innerHTML = lines.join("");
    }

    function renderSetupRing(currentPayload, result) {
      const svg = $("setup_svg");
      const model = collectSetupModel(currentPayload, result);
      buildSetupSummary(model);

      const cx = 210;
      const cy = 210;
      const ccRadius = 166;
      const scRadius = 132;
      const tmRadius = 98;
      const parts = [];

      parts.push(`<rect x="0" y="0" width="420" height="420" rx="22" fill="rgba(245,248,244,0.96)"></rect>`);
      parts.push(drawTicks(cx, cy, 184));
      parts.push(`<circle cx="${cx}" cy="${cy}" r="${ccRadius}" fill="none" stroke="rgba(20,124,114,0.08)" stroke-width="16"></circle>`);
      parts.push(`<circle cx="${cx}" cy="${cy}" r="${scRadius}" fill="none" stroke="rgba(20,124,114,0.12)" stroke-width="22"></circle>`);
      parts.push(`<circle cx="${cx}" cy="${cy}" r="${tmRadius}" fill="none" stroke="rgba(154,79,24,0.10)" stroke-width="18"></circle>`);
      parts.push(drawAnatomyOverlay(cx, cy, tmRadius - 8, ccRadius + 4, 420));

      if (model.scProfile) {
        const minValue = Math.min(...model.scProfile);
        const maxValue = Math.max(...model.scProfile);
        model.scProfile.forEach((value, idx) => {
          const start = 360 * idx / model.scProfile.length;
          const span = 360 / model.scProfile.length - 0.9;
          const color = mixColors("#eff5ea", "#147c72", maxValue === minValue ? 0.5 : (value - minValue) / (maxValue - minValue));
          parts.push(`<path d="${arcPath(cx, cy, scRadius, start, span)}" stroke="${color}" stroke-width="22" fill="none" opacity="0.95"></path>`);
        });
      }

      if (model.tmProfile) {
        const minValue = Math.min(...model.tmProfile);
        const maxValue = Math.max(...model.tmProfile);
        model.tmProfile.forEach((value, idx) => {
          const start = 360 * idx / model.tmProfile.length;
          const span = 360 / model.tmProfile.length - 1.2;
          const color = mixColors("#f1dece", "#9a4f18", maxValue === minValue ? 0.5 : (value - minValue) / (maxValue - minValue));
          parts.push(`<path d="${arcPath(cx, cy, tmRadius, start, span)}" stroke="${color}" stroke-width="18" fill="none" opacity="0.96"></path>`);
        });
      }

      model.trabeculotomies.forEach((range) => {
        const start = 360 * normalizeNode(range.start, model.totalNodes) / model.totalNodes;
        const span = 360 * rangeSpanNodes(range) / model.totalNodes;
        if (span >= 359.5) {
          parts.push(`<circle cx="${cx}" cy="${cy}" r="${scRadius}" fill="none" stroke="#1a9b73" stroke-width="12"></circle>`);
        } else {
          parts.push(`<path d="${arcPath(cx, cy, scRadius, start, span)}" stroke="#1a9b73" stroke-width="12" stroke-linecap="round" fill="none"></path>`);
        }
      });

      model.sinusotomies.forEach((range) => {
        const start = 360 * normalizeNode(range.start, model.totalNodes) / model.totalNodes;
        const span = 360 * rangeSpanNodes(range) / model.totalNodes;
        if (span >= 359.5) {
          parts.push(`<circle cx="${cx}" cy="${cy}" r="${ccRadius - 8}" fill="none" stroke="#d9782b" stroke-width="8" stroke-dasharray="3 5"></circle>`);
        } else {
          parts.push(`<path d="${arcPath(cx, cy, ccRadius - 8, start, span)}" stroke="#d9782b" stroke-width="8" stroke-linecap="round" stroke-dasharray="3 5" fill="none"></path>`);
        }
      });

      model.stents.forEach((stent) => {
        const start = 360 * normalizeNode(stent.loc, model.totalNodes) / model.totalNodes;
        const span = 360 * Math.max(1, stent.span_nodes || 1) / model.totalNodes;
        parts.push(`<path d="${arcPath(cx, cy, scRadius - 2, start, span)}" stroke="#2075b8" stroke-width="10" stroke-linecap="round" fill="none"></path>`);
        const inletNode = normalizeNode(stent.loc + (stent.inlet_index || 0), model.totalNodes);
        const inlet = polarPoint(cx, cy, scRadius - 2, 360 * inletNode / model.totalNodes);
        parts.push(`<circle cx="${inlet.x.toFixed(2)}" cy="${inlet.y.toFixed(2)}" r="4.5" fill="white" stroke="#2075b8" stroke-width="2"></circle>`);
      });

      model.yagHoles.forEach((node) => {
        const point = polarPoint(cx, cy, tmRadius + 18, 360 * normalizeNode(node, model.totalNodes) / model.totalNodes);
        parts.push(`<circle cx="${point.x.toFixed(2)}" cy="${point.y.toFixed(2)}" r="5.5" fill="white" stroke="#bf3f6d" stroke-width="3"></circle>`);
      });

      model.ccs.forEach((cc) => {
        const angle = 360 * normalizeNode(cc.loc, model.totalNodes) / model.totalNodes;
        const inner = polarPoint(cx, cy, ccRadius - 3, angle);
        const outer = polarPoint(cx, cy, ccRadius + 22, angle);
        const width = clamp(1.2 + (Number(cc.ratio) || 1) * 0.8, 1.4, 6.5);
        parts.push(`<line x1="${inner.x.toFixed(2)}" y1="${inner.y.toFixed(2)}" x2="${outer.x.toFixed(2)}" y2="${outer.y.toFixed(2)}" stroke="#1f6fb4" stroke-width="${width.toFixed(2)}" opacity="0.86"></line>`);
      });

      parts.push(`<text x="${cx}" y="${cy - 10}" text-anchor="middle" class="ring-title">Anterior Chamber</text>`);
      parts.push(`<text x="${cx}" y="${cy + 14}" text-anchor="middle" class="ring-label">Schlemm's canal / TM / CC map</text>`);
      svg.innerHTML = parts.join("");
    }

    function updateMetrics(metrics) {
      $("m_iop").textContent = fmt(metrics.iop);
      $("m_flowrate").textContent = fmt(metrics.flowrate);
      $("m_resistance").textContent = fmt(metrics.resistance);
      $("m_facility").textContent = fmt(metrics.facility);
    }

    function updateModeUI() {
      const isConstantPressure = $("mode").value === "constant pressure";
      const hasVariableRtmProfile = $("rtm_profile").value.trim().length > 0;
      const hasFullRtmArray = $("rtm_node_values").value.trim().length > 0;
      const autoRtmEnabled = $("auto_rtm").checked && !isConstantPressure && !hasVariableRtmProfile && !hasFullRtmArray;
      $("iop_label").textContent = isConstantPressure ? "IOP" : "Baseline IOP";
      $("iop").value = $("iop").value || (isConstantPressure ? "7.0" : "15.09");
      $("iop_hint").textContent = isConstantPressure
        ? "In constant pressure mode, IOP is the target pressure for the solve."
        : hasFullRtmArray
          ? "Baseline IOP and scalar RTM are ignored while a full TM node array is present. Clear the node array to re-enable auto RTM."
          : hasVariableRtmProfile
          ? "Baseline IOP is not used while a TM resistance profile is present. Clear the profile to re-enable auto RTM."
          : "In constant flow mode, this is used to estimate baseline TM resistance when Auto RTM is enabled. The estimate assumes a baseline eye with no surgeries and default collector channels.";
      $("auto_rtm").disabled = isConstantPressure || hasVariableRtmProfile || hasFullRtmArray;
      $("rtm").disabled = autoRtmEnabled || hasVariableRtmProfile || hasFullRtmArray;
      $("rtm").placeholder = hasFullRtmArray ? "overridden by full TM node array" : (hasVariableRtmProfile ? "overridden by TM profile" : (autoRtmEnabled ? "derived automatically" : "default"));
    }

    function updateInterventionUI() {
      const surgery = $("surgery").value;
      const hasTrabRanges = $("trabeculotomies").value.trim().length > 0;
      const hasYagNodes = $("yag_holes_list").value.trim().length > 0;
      const hasStentNodes = $("stent_nodes").value.trim().length > 0;

      $("trab_hours_wrap").classList.toggle("hidden", surgery !== "Trabeculotomy");
      $("yag_count_wrap").classList.toggle("hidden", surgery !== "YAG holes");

      $("trabeculotomy_hint").textContent = surgery === "Trabeculotomy"
        ? (hasTrabRanges
            ? "Explicit ranges will override the preset clock-hour trabeculotomy."
            : "Leave blank to use the selected Trab hours preset.")
        : "Optional SC node ranges. This stays available even if Surgery is not set to Trabeculotomy.";

      $("yag_nodes_hint").textContent = surgery === "YAG holes"
        ? (hasYagNodes
            ? "Explicit YAG node locations will override the YAG hole count preset."
            : "Leave blank to use the YAG hole count above.")
        : "Optional explicit YAG node locations.";

      $("stent_nodes_hint").textContent = surgery === "iStent"
        ? (hasStentNodes
            ? "All listed nodes will receive the stent model from the editor below."
            : "If left blank, node 0 will receive one stent.")
        : "Optional explicit stent nodes. If you fill these, the stent editor below is used even without selecting iStent surgery.";

      if (surgery === "iStent" || hasStentNodes) {
        $("panel_stent").open = true;
      }
    }

    function statusFromMeta(meta) {
      if (!meta) return "";
      let parts = [];
      if (meta.rtm_source === "baseline_iop") {
        parts.push(`Auto RTM enabled: baseline IOP ${fmt(meta.baseline_iop)} -> Rtm ${fmt(meta.rtm_used)}.`);
      }
      if (meta.rtm_source === "manual") {
        parts.push(`Manual Rtm used: ${fmt(meta.rtm_used)}.`);
      }
      if (meta.rtm_source === "tm_profile") {
        parts.push(`Variable TM profile used: ${meta.tm_profile_segments || 12} segments.`);
      }
      if (meta.rtm_source === "tm_node_array") {
        parts.push(`Full TM node array used: ${meta.tm_node_count || $("n").value * $("m").value} nodes.`);
      }
      if (meta.h0_source === "sc_profile") {
        parts.push(`Variable SC profile used: ${meta.sc_profile_segments || $("n").value || 30} segments.`);
      }
      if (meta.h0_source === "sc_node_array") {
        parts.push(`Full SC node array used: ${meta.sc_node_count || $("n").value * $("m").value} nodes.`);
      }
      if (meta.rtm_override_count) {
        parts.push(`TM node overrides applied: ${meta.rtm_override_count}.`);
      }
      if (meta.h0_override_count) {
        parts.push(`SC node height overrides applied: ${meta.h0_override_count}.`);
      }
      if (meta.gsc_multiplier_count) {
        parts.push(`Full SC conductance multiplier array used: ${meta.gsc_multiplier_count} segments.`);
      } else if (meta.gsc_multiplier_override_count) {
        parts.push(`SC conductance multiplier overrides applied: ${meta.gsc_multiplier_override_count}.`);
      }
      if (meta.gsc_override_count) {
        parts.push(`Full SC conductance override array used: ${meta.gsc_override_count} segments.`);
      } else if (meta.gsc_override_range_count) {
        parts.push(`SC conductance overrides applied: ${meta.gsc_override_range_count}.`);
      }
      return parts.join(" ");
    }

    function renderSolutionInfo(result, details = null) {
      const labels = eyeLabels();
      const rows = [
        `<div class="solution-row"><span>IOP</span><b>${fmt(result.metrics.iop)} mmHg</b></div>`,
        `<div class="solution-row"><span>Flow rate</span><b>${fmt(result.metrics.flowrate)} uL/min</b></div>`,
        `<div class="solution-row"><span>Resistance</span><b>${fmt(result.metrics.resistance)}</b></div>`,
        `<div class="solution-row"><span>Eye</span><b>${labels.eye}</b></div>`,
      ];
      if (details?.kind === "node") {
        rows.push(`<div class="solution-row"><span>θ</span><b>${fmt(details.theta)}°</b></div>`);
        rows.push(`<div class="solution-row"><span>Psc</span><b>${fmt(details.pressure)} mmHg</b></div>`);
        rows.push(`<div class="solution-row"><span>Canal height</span><b>${fmt(details.height)} um</b></div>`);
      } else if (details?.kind === "cc") {
        rows.push(`<div class="solution-row"><span>CC node</span><b>${details.loc}</b></div>`);
        rows.push(`<div class="solution-row"><span>Jcc</span><b>${fmt(details.flow)} uL/min</b></div>`);
      } else {
        rows.push(`<div>Hover the pressure ring to inspect local pressure and canal height, or hover a collector channel to inspect its flow.</div>`);
      }
      $("solution_info").innerHTML = rows.join("");
    }

    function renderSolutionRing(result, solvedPayload) {
      const svg = $("solution_svg");
      const note = $("solution_note");
      if (!result) {
        svg.innerHTML = `<rect x="0" y="0" width="520" height="420" rx="22" fill="rgba(245,248,244,0.96)"></rect><text x="260" y="208" text-anchor="middle" class="ring-title">No solution yet</text><text x="260" y="232" text-anchor="middle" class="ring-label">Run Solve locally to render the pressure and flow map.</text>`;
        $("solution_info").textContent = "Hover the pressure ring or a collector channel to inspect local values.";
        note.textContent = "Waiting for the first solve.";
        return;
      }

      const pressure = result.series.pressure.y;
      const heights = result.series.height.y;
      const jcc = result.series.jcc.y;
      const totalNodes = Math.max(1, Math.round(result.meta?.total_nodes || pressure.length));
      const ccs = inferCollectorNodes(solvedPayload, result, totalNodes);
      const pev = numberValue(solvedPayload?.pev, 8.0) || 8.0;
      const iop = numberValue(result.metrics.iop, 0) || 0;
      const pLow = Math.min(pev, ...pressure);
      const pHigh = Math.max(iop, ...pressure);
      const hLow = Math.min(...heights);
      const hHigh = Math.max(...heights);
      const maxFlow = Math.max(...jcc, 1e-9);
      const parts = [];
      const cx = 300;
      const cy = 210;
      const pressureRadius = 126;
      const heightRadius = 92;
      const ccRadius = 142;

      parts.push(`<defs><linearGradient id="pressureScale" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="#e04b3f"></stop><stop offset="100%" stop-color="#1f6fb4"></stop></linearGradient></defs>`);
      parts.push(`<rect x="0" y="0" width="520" height="420" rx="22" fill="rgba(245,248,244,0.96)"></rect>`);
      parts.push(`<rect x="18" y="44" width="18" height="248" rx="4" fill="url(#pressureScale)"></rect>`);
      parts.push(`<text x="48" y="54" class="ring-label">${fmt(pHigh)} mmHg</text>`);
      parts.push(`<text x="48" y="292" class="ring-label">${fmt(pLow)} mmHg</text>`);
      parts.push(`<text x="18" y="26" class="ring-label">Pressure</text>`);
      parts.push(drawTicks(cx, cy, 182));
      parts.push(drawAnatomyOverlay(cx, cy, heightRadius - 10, ccRadius + 18, 520));

      pressure.forEach((value, idx) => {
        const start = 360 * idx / totalNodes;
        const span = 360 / totalNodes + 0.12;
        const color = mixColors("#1f6fb4", "#e04b3f", pHigh === pLow ? 0.5 : (value - pLow) / (pHigh - pLow));
        parts.push(`<path class="hoverable" data-kind="node" data-theta="${(360 * idx / totalNodes).toFixed(2)}" data-pressure="${value}" data-height="${heights[idx]}" d="${arcPath(cx, cy, pressureRadius, start, span)}" stroke="${color}" stroke-width="20" fill="none"></path>`);
      });

      heights.forEach((value, idx) => {
        const start = 360 * idx / totalNodes;
        const span = 360 / totalNodes + 0.12;
        const color = mixColors("#f0e5b9", "#147c72", hHigh === hLow ? 0.5 : (value - hLow) / (hHigh - hLow));
        parts.push(`<path d="${arcPath(cx, cy, heightRadius, start, span)}" stroke="${color}" stroke-width="16" fill="none" opacity="0.96"></path>`);
      });

      ccs.slice(0, jcc.length).forEach((cc, idx) => {
        const angle = 360 * normalizeNode(cc.loc, totalNodes) / totalNodes;
        const inner = polarPoint(cx, cy, ccRadius, angle);
        const outer = polarPoint(cx, cy, ccRadius + 10 + 22 * (jcc[idx] / maxFlow), angle);
        const color = mixColors("#a7d1f2", "#1f6fb4", jcc[idx] / maxFlow);
        parts.push(`<line class="hoverable" data-kind="cc" data-loc="${cc.loc}" data-flow="${jcc[idx]}" x1="${inner.x.toFixed(2)}" y1="${inner.y.toFixed(2)}" x2="${outer.x.toFixed(2)}" y2="${outer.y.toFixed(2)}" stroke="${color}" stroke-width="4" stroke-linecap="round"></line>`);
      });

      parts.push(`<text x="${cx}" y="${cy - 8}" text-anchor="middle" class="ring-title">Solution Map</text>`);
      parts.push(`<text x="${cx}" y="${cy + 15}" text-anchor="middle" class="ring-label">Outer ring: pressure | Inner ring: canal height</text>`);
      svg.innerHTML = parts.join("");

      svg.querySelectorAll("[data-kind='node']").forEach((node) => {
        node.addEventListener("mouseenter", () => {
          renderSolutionInfo(result, {
            kind: "node",
            theta: Number(node.dataset.theta),
            pressure: Number(node.dataset.pressure),
            height: Number(node.dataset.height),
          });
        });
      });

      svg.querySelectorAll("[data-kind='cc']").forEach((line) => {
        line.addEventListener("mouseenter", () => {
          renderSolutionInfo(result, {
            kind: "cc",
            loc: line.dataset.loc,
            flow: Number(line.dataset.flow),
          });
        });
      });

      svg.onmouseleave = () => renderSolutionInfo(result);
      renderSolutionInfo(result);
      note.textContent = resultDirty
        ? "Showing the latest solved field. Inputs changed afterward, so the setup preview is newer than this solution map."
        : "Showing the latest local solve.";
    }

    function plotSeries(result) {
      const kind = $("plot_type").value;
      const series = result.series[kind];
      const labels = {
        pressure: ["Schlemm's Canal Pressure", "Circumferential position (mm)", "Psc (mmHg)"],
        height: ["Schlemm's Canal Height", "Circumferential position (mm)", "hsc (um)"],
        jcc: ["Collector Channel Flow", series.x_title || "Collector channel index", "Jcc (uL/min)"],
      };
      const [title, xTitle, yTitle] = labels[kind];
      const trace = {
        type: "scatter",
        mode: kind === "jcc" ? "lines+markers" : "lines",
        x: series.x,
        y: series.y,
        line: { color: "#147c72", width: 2 },
        marker: { color: "#147c72", size: 6 },
      };
      const layout = {
        title,
        paper_bgcolor: "#ffffff",
        plot_bgcolor: "#ffffff",
        font: { color: "#1e2521" },
        margin: { l: 70, r: 24, t: 56, b: kind === "jcc" ? 58 : 92 },
        xaxis: { title: xTitle, gridcolor: "#e6ebe5" },
        yaxis: { title: yTitle, gridcolor: "#e6ebe5", rangemode: "tozero" },
      };
      if (kind !== "jcc") {
        const axisGuide = anatomyAxisGuide(series);
        if (axisGuide) {
          layout.xaxis.tickmode = "array";
          layout.xaxis.tickvals = axisGuide.tickvals;
          layout.xaxis.ticktext = axisGuide.ticktext;
          layout.xaxis.tickfont = { size: 11, color: "#47524c" };
          layout.shapes = axisGuide.shapes;
        }
      }
      Plotly.react("plot", [trace], layout, { responsive: true, displaylogo: false, scrollZoom: true });
    }

    function refreshVisuals() {
      renderSetupRing(payload(), lastResult);
      renderSolutionRing(lastResult, lastSolvedPayload || payload());
    }

    function markResultDirty() {
      resultDirty = !!lastResult;
      refreshVisuals();
    }

    async function solve() {
      const currentPayload = payload();
      $("status").textContent = "Solving locally...";
      $("solveBtn").disabled = true;
      try {
        const response = await fetch("/api/solve", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(currentPayload),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Solve failed");
        lastResult = data;
        lastSolvedPayload = currentPayload;
        resultDirty = false;
        updateMetrics(data.metrics);
        plotSeries(data);
        refreshVisuals();
        $("status").textContent = statusFromMeta(data.meta);
      } catch (err) {
        $("status").textContent = err.message || String(err);
      } finally {
        $("solveBtn").disabled = false;
      }
    }

    $("solveBtn").addEventListener("click", solve);
    $("plot_type").addEventListener("change", () => {
      if (lastResult) {
        plotSeries(lastResult);
      } else {
        solve();
      }
    });
    $("mode").addEventListener("change", () => {
      updateModeUI();
      markResultDirty();
    });
    $("eye_side").addEventListener("change", () => {
      refreshVisuals();
      if (lastResult) {
        plotSeries(lastResult);
      }
    });
    $("surgery").addEventListener("change", () => {
      updateInterventionUI();
      markResultDirty();
    });
    $("auto_rtm").addEventListener("change", () => {
      updateModeUI();
      markResultDirty();
    });
    $("rtm_profile").addEventListener("input", () => {
      updateModeUI();
      markResultDirty();
    });
    $("rtm_node_values").addEventListener("input", () => {
      updateModeUI();
      markResultDirty();
    });
    $("trabeculotomies").addEventListener("input", updateInterventionUI);
    $("yag_holes_list").addEventListener("input", updateInterventionUI);
    $("stent_nodes").addEventListener("input", updateInterventionUI);
    document.querySelectorAll("input, select, textarea").forEach((element) => {
      if (["mode", "eye_side", "surgery", "auto_rtm", "rtm_profile", "rtm_node_values", "plot_type", "trabeculotomies", "yag_holes_list", "stent_nodes"].includes(element.id)) return;
      element.addEventListener("input", markResultDirty);
      element.addEventListener("change", markResultDirty);
    });
    updateModeUI();
    updateInterventionUI();
    refreshVisuals();
    window.addEventListener("load", solve);
  </script>
</body>
</html>
"""


def guess_lan_ips() -> list[str]:
    ips: list[str] = []
    try:
        host_name = socket.gethostname()
        for _family, _stype, _proto, _canon, sockaddr in socket.getaddrinfo(host_name, None, socket.AF_INET):
            ip = sockaddr[0]
            if ip and not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    return ips


def serve(host: str = "127.0.0.1", port: int = 0) -> int:
    html = build_html().encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)
                return
            if parsed.path == "/favicon.ico":
                self.send_response(HTTPStatus.NO_CONTENT)
                self.end_headers()
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

        def do_POST(self):
            parsed = urlparse(self.path)
            if parsed.path != "/api/solve":
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                result = solve_payload(payload)
                body = json.dumps(result).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as exc:
                body = json.dumps({"error": str(exc)}).encode("utf-8")
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        def log_message(self, format: str, *args):
            return

    server = ThreadingHTTPServer((host, port), Handler)
    local_url = f"http://127.0.0.1:{server.server_port}/"
    print(f"Local URL: {local_url}")
    if host == "0.0.0.0":
        for ip in guess_lan_ips():
            print(f"LAN URL: http://{ip}:{server.server_port}/")
    print("Local calculator running. Press Ctrl+C to stop.")

    threading.Timer(0.4, lambda: webbrowser.open(local_url, new=1)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main() -> int:
    host = "127.0.0.1"
    port = 0
    if "--share" in sys.argv:
        host = "0.0.0.0"
    for arg in sys.argv[1:]:
        if arg.isdigit():
            port = int(arg)
    return serve(host=host, port=port)


if __name__ == "__main__":
    raise SystemExit(main())
