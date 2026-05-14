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


def solution_to_jsonable(solution: dict, stents=None, ccs=None) -> dict:
    pressure = [float(v) for v in solution.get("pressure", [])]
    jcc = [float(v) for v in solution.get("jcc", [])]
    iop = float(solution.get("iop", 0.0))

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
    }


def solve_payload(payload: dict) -> dict:
    mode = payload.get("mode", "constant flow")
    surgery = payload.get("surgery", "None")
    geometry = payload.get("geometry", "ellipse")

    kwargs = {
        "geometry": geometry,
        "pev": finite_float(payload.get("pev"), 8.0),
    }

    optional_float_keys = ("rtm", "etm", "h0", "hs", "rcc", "qu", "beta", "max_error")
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

    stents = None
    max_nodes = int(kwargs.get("n", 30)) * int(kwargs.get("m", 40))
    ccs = parse_ccs(payload.get("ccs"), max_nodes=max_nodes)
    explicit_trabeculotomies = parse_ranges(payload.get("trabeculotomies"))
    explicit_sinusotomies = parse_ranges(payload.get("sinusotomies"))
    explicit_yag_holes = parse_int_list(payload.get("yag_holes_list"))
    stent_nodes_text = payload.get("stent_nodes")
    if not stent_nodes_text and surgery == "iStent":
        stent_nodes_text = payload.get("stent_node", "0")
    explicit_stents = parse_stent_nodes(stent_nodes_text, payload)

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

    return solution_to_jsonable(solution, stents=stents, ccs=ccs)


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
      padding: 20px;
      border-right: 1px solid var(--line);
      background: rgba(255,255,255,0.84);
      overflow-y: auto;
    }
    main {
      display: grid;
      grid-template-rows: auto 1fr;
      min-width: 0;
      min-height: 0;
      padding: 18px;
      gap: 14px;
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
    .section {
      padding: 14px 0;
      border-top: 1px solid var(--line);
    }
    .section h2 {
      margin: 0 0 10px;
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: var(--muted);
    }
    label {
      display: block;
      margin: 10px 0 5px;
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
      min-height: 62px;
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
      margin-top: 12px;
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
    .grid2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
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
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      overflow: hidden;
    }
    #plot {
      width: 100%;
      height: calc(100vh - 170px);
      min-height: 480px;
    }
    .status {
      min-height: 20px;
      margin-top: 10px;
      color: var(--warn);
      font-size: 13px;
      line-height: 1.35;
    }
    @media (max-width: 900px) {
      .app { grid-template-columns: 1fr; }
      aside { border-right: 0; border-bottom: 1px solid var(--line); }
      .metrics { grid-template-columns: 1fr 1fr; }
      #plot { height: 520px; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <h1>Aqueous Outflow Model</h1>
      <p class="sub">Pure local calculator. The browser talks to this Python server, and the server calls the local solver.</p>

      <div class="section">
        <h2>Solver</h2>
        <label>Mode</label>
        <select id="mode">
          <option value="constant flow">constant flow</option>
          <option value="constant pressure">constant pressure</option>
        </select>
        <label>Geometry</label>
        <select id="geometry">
          <option value="ellipse">ellipse</option>
          <option value="rectangle">rectangle</option>
        </select>
        <div class="grid2">
          <div><label>IOP</label><input id="iop" type="number" step="0.1" value="7.0" /></div>
          <div><label>Qt</label><input id="qt" type="number" step="0.1" value="2.0" /></div>
        </div>
        <div class="grid2">
          <div><label>Pev</label><input id="pev" type="number" step="0.1" value="8.0" /></div>
          <div><label>Rtm</label><input id="rtm" type="number" step="0.1" placeholder="default" /></div>
        </div>
      </div>

      <div class="section">
        <h2>Constants</h2>
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

      <div class="section">
        <h2>Collector Channels</h2>
        <label>Manual CC distribution</label>
        <textarea id="ccs" placeholder="Example: 0:1, 40:1, 80:0.5, 120:2"></textarea>
        <div class="hint">Format is node:relative conductance. Use commas or semicolons. Leave blank for the uniform default from N and M.</div>
        <div class="hint">If only a node is provided, ratio defaults to 1; for example 0, 40, 80.</div>
      </div>

      <div class="section">
        <h2>Intervention</h2>
        <label>Surgery</label>
        <select id="surgery">
          <option>None</option>
          <option>Trabeculotomy</option>
          <option>YAG holes</option>
          <option>iStent</option>
        </select>
        <div class="grid2">
          <div>
            <label>Trab hours</label>
            <select id="trab_hours">
              <option>1</option>
              <option>4</option>
              <option>12</option>
            </select>
          </div>
          <div><label>YAG holes</label><input id="yag_holes" type="number" step="1" value="2" /></div>
        </div>
        <input id="stent_node" type="hidden" value="0" />
        <label>Trabeculotomy ranges</label>
        <textarea id="trabeculotomies" placeholder="Example: 0-99, 300-399"></textarea>
        <div class="hint">Ranges are SC node indexes. Leave blank to use Trab hours when Surgery is Trabeculotomy.</div>
        <label>Sinusotomy ranges</label>
        <textarea id="sinusotomies" placeholder="Example: 120-180, 620-700"></textarea>
        <div class="hint">Sinusotomy ranges can be combined with any selected surgery.</div>
        <label>YAG hole nodes</label>
        <input id="yag_holes_list" type="text" placeholder="Example: 0, 200, 400" />
        <div class="hint">Leave blank to use YAG holes count when Surgery is YAG holes.</div>
        <label>iStent nodes</label>
        <input id="stent_nodes" type="text" placeholder="Example: 0, 300, 600" />
        <div class="hint">Each node gets the stent model configured below. If Surgery is iStent and this is blank, node 0 is used.</div>
      </div>

      <div class="section">
        <h2>Stent Editor</h2>
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
        <label>Windowed stent options</label>
        <div class="grid2">
          <div><label>Number of windows</label><input id="stent_n_windows" type="number" step="1" value="0" /></div>
          <div><label>Window length (um)</label><input id="stent_l_window" type="number" step="10" placeholder="required if windows > 0" /></div>
        </div>
        <div class="grid2">
          <div><label>Window height (um)</label><input id="stent_h_window" type="number" step="1" placeholder="required if windows > 0" /></div>
          <div><label>Spine length (um)</label><input id="stent_l_spine" type="number" step="10" placeholder="required if windows > 0" /></div>
        </div>
        <label>Spine height (um)</label>
        <input id="stent_h_spine" type="number" step="1" placeholder="required if windows > 0" />
        <div class="hint">For a simple iStent, leave window count at 0. For devices with windows/spines, fill all windowed stent fields.</div>
      </div>

      <div class="section">
        <h2>Plot</h2>
        <label>Plot type</label>
        <select id="plot_type">
          <option value="pressure">Pressure distribution</option>
          <option value="height">Canal height</option>
          <option value="jcc">Collector channel flow</option>
        </select>
        <button id="solveBtn">Solve locally</button>
        <div id="status" class="status"></div>
      </div>
    </aside>

    <main>
      <div class="metrics">
        <div class="metric"><span>IOP</span><b id="m_iop">-</b></div>
        <div class="metric"><span>Flow rate</span><b id="m_flowrate">-</b></div>
        <div class="metric"><span>Resistance</span><b id="m_resistance">-</b></div>
        <div class="metric"><span>Facility</span><b id="m_facility">-</b></div>
      </div>
      <div class="plot-wrap"><div id="plot"></div></div>
    </main>
  </div>

  <script>
    const $ = (id) => document.getElementById(id);

    function payload() {
      return {
        mode: $("mode").value,
        geometry: $("geometry").value,
        iop: $("iop").value,
        qt: $("qt").value,
        pev: $("pev").value,
        rtm: $("rtm").value,
        n: $("n").value,
        m: $("m").value,
        etm: $("etm").value,
        h0: $("h0").value,
        hs: $("hs").value,
        rcc: $("rcc").value,
        qu: $("qu").value,
        max_error: $("max_error").value,
        beta: $("beta").value,
        unconventional: $("unconventional").checked,
        ccs: $("ccs").value,
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

    function fmt(value) {
      if (!Number.isFinite(value)) return "-";
      return Number(value).toPrecision(5);
    }

    function updateMetrics(metrics) {
      $("m_iop").textContent = fmt(metrics.iop);
      $("m_flowrate").textContent = fmt(metrics.flowrate);
      $("m_resistance").textContent = fmt(metrics.resistance);
      $("m_facility").textContent = fmt(metrics.facility);
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
        margin: { l: 70, r: 24, t: 56, b: 58 },
        xaxis: { title: xTitle, gridcolor: "#e6ebe5" },
        yaxis: { title: yTitle, gridcolor: "#e6ebe5", rangemode: "tozero" },
      };
      Plotly.react("plot", [trace], layout, { responsive: true, displaylogo: false, scrollZoom: true });
    }

    async function solve() {
      $("status").textContent = "Solving locally...";
      $("solveBtn").disabled = true;
      try {
        const response = await fetch("/api/solve", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload()),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Solve failed");
        updateMetrics(data.metrics);
        plotSeries(data);
        $("status").textContent = "";
      } catch (err) {
        $("status").textContent = err.message || String(err);
      } finally {
        $("solveBtn").disabled = false;
      }
    }

    $("solveBtn").addEventListener("click", solve);
    $("plot_type").addEventListener("change", solve);
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
