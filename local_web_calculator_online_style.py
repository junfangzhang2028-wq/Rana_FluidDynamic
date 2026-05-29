from __future__ import annotations

import json
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from local_web_calculator import guess_lan_ips, solve_payload


def build_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Aqueous Humor Outflow Model</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      --bg: #f3f3f6;
      --panel: #ffffff;
      --ink: #1e1f25;
      --muted: #666b77;
      --line: #d7d9e1;
      --purple: #552d89;
      --purple-dark: #45216f;
      --purple-soft: #ece4f8;
      --danger: #d43f4d;
      --blue: #1d84e8;
      --trab: #ef3932;
      --canal: #b8b8b8;
      --tm-label: #121212;
      --soft: #f8f8fb;
    }
    * { box-sizing: border-box; }
    html, body {
      margin: 0;
      min-height: 100%;
      font-family: "Segoe UI", "Aptos", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }
    button, input, select, textarea {
      font: inherit;
    }
    .shell {
      display: grid;
      grid-template-columns: 200px minmax(0, 1fr);
      min-height: 100vh;
    }
    .sidebar {
      background: #fafafd;
      border-right: 1px solid #d9d9df;
      display: flex;
      flex-direction: column;
    }
    .sidebar-head {
      height: 72px;
      display: flex;
      align-items: center;
      padding: 0 16px;
      background: var(--purple);
      color: white;
      font-size: 18px;
      font-weight: 700;
    }
    .menu {
      padding: 10px 0;
    }
    .menu a {
      display: block;
      padding: 12px 16px;
      color: #22242d;
      text-decoration: none;
      font-size: 15px;
    }
    .menu a.active {
      background: #dedee5;
    }
    .work {
      min-width: 0;
      display: grid;
      grid-template-rows: 72px 1fr;
    }
    .topbar {
      display: flex;
      align-items: center;
      padding: 0 18px;
      background: var(--purple);
      color: white;
      font-size: 17px;
      font-weight: 700;
      box-shadow: 0 1px 0 rgba(0,0,0,0.08);
    }
    .page {
      padding: 18px;
    }
    .sim-card {
      border: 1px solid #d3d4db;
      background: var(--panel);
      box-shadow: 0 2px 8px rgba(33, 34, 41, 0.12);
      min-height: 560px;
      display: grid;
      grid-template-columns: minmax(420px, 1fr) 540px;
    }
    .stage-pane {
      padding: 20px 22px 18px;
      border-right: 1px solid #ececf2;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .stage-wrap {
      flex: 1 1 auto;
      display: grid;
      place-items: center;
      min-height: 380px;
      background:
        radial-gradient(circle at 50% 36%, rgba(247,247,247,0.86), rgba(255,255,255,0.96));
    }
    .ring {
      width: min(100%, 520px);
      height: auto;
      display: block;
    }
    .stage-meta,
    .solution-note,
    .solution-info {
      border: 1px solid var(--line);
      border-radius: 4px;
      background: #fbfbfd;
      padding: 10px 12px;
      font-size: 13px;
      line-height: 1.45;
    }
    .solution-info {
      display: grid;
      gap: 5px;
    }
    .solution-row {
      display: flex;
      justify-content: space-between;
      gap: 12px;
    }
    .solution-row span:first-child {
      color: var(--muted);
    }
    .control-pane {
      padding: 18px 22px 8px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .field {
      display: grid;
      gap: 6px;
    }
    .field label {
      font-size: 13px;
      color: #757985;
    }
    .field input,
    .field select,
    textarea {
      width: 100%;
      border: 0;
      border-bottom: 1px solid #9fa3af;
      padding: 4px 0 6px;
      background: transparent;
      outline: none;
      font-size: 15px;
    }
    textarea {
      min-height: 96px;
      border: 1px solid #cfd3dd;
      border-radius: 4px;
      padding: 8px 10px;
      resize: vertical;
      background: white;
    }
    .checkline {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 15px;
      margin-top: 2px;
    }
    .checkline input {
      width: 18px;
      height: 18px;
    }
    .hint {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
    }
    .primary-chip {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 0;
      border-radius: 2px;
      background: var(--purple);
      color: white;
      padding: 10px 14px;
      font-weight: 700;
      cursor: pointer;
    }
    .primary-chip:hover {
      background: var(--purple-dark);
    }
    .plus {
      font-size: 30px;
      line-height: 1;
      font-weight: 300;
      transform: translateY(-1px);
    }
    .surgery-block {
      display: grid;
      gap: 10px;
    }
    .surgery-title {
      margin: 0;
      font-size: 18px;
      font-weight: 700;
    }
    .surgery-item {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      padding: 2px 0;
    }
    .surgery-copy strong {
      display: block;
      font-size: 15px;
      margin-bottom: 3px;
    }
    .surgery-copy span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }
    .icon-button {
      border: 0;
      background: transparent;
      color: #111;
      cursor: pointer;
      font-size: 36px;
      line-height: 0.9;
      padding: 0;
      width: 30px;
      text-align: center;
    }
    .icon-button:hover {
      color: var(--purple);
    }
    .bottom-actions {
      margin-top: auto;
      display: flex;
      justify-content: flex-end;
      align-items: center;
      gap: 16px;
      padding-top: 8px;
    }
    .text-action {
      border: 0;
      background: transparent;
      color: #6b6f7a;
      cursor: pointer;
      padding: 0;
      font-size: 15px;
    }
    .text-action:hover {
      color: var(--purple);
    }
    .danger {
      color: var(--danger);
    }
    .solve {
      border: 0;
      border-radius: 2px;
      background: var(--purple);
      color: white;
      min-width: 92px;
      padding: 10px 16px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 2px 4px rgba(85,45,137,0.26);
    }
    .solve:hover {
      background: var(--purple-dark);
    }
    .status {
      min-height: 18px;
      color: #95610f;
      font-size: 12px;
      line-height: 1.4;
    }
    .plot-card {
      margin-top: 18px;
      border: 1px solid #d3d4db;
      background: white;
      box-shadow: 0 2px 8px rgba(33, 34, 41, 0.07);
      padding: 14px 16px 16px;
    }
    .plot-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 10px;
    }
    .plot-head h3 {
      margin: 0;
      font-size: 15px;
    }
    .plot-head select {
      width: 240px;
      max-width: 100%;
      border: 1px solid #cfd3dd;
      border-radius: 4px;
      padding: 8px 10px;
      background: white;
    }
    #plot {
      width: 100%;
      height: 420px;
    }
    .hidden {
      display: none !important;
    }
    dialog {
      width: min(760px, calc(100vw - 32px));
      border: 0;
      border-radius: 8px;
      padding: 0;
      box-shadow: 0 16px 52px rgba(20, 22, 33, 0.30);
    }
    dialog::backdrop {
      background: rgba(18, 17, 26, 0.40);
    }
    .dialog-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 16px 18px;
      border-bottom: 1px solid #ececf2;
      background: #fcfcfe;
    }
    .dialog-head h3 {
      margin: 0;
      font-size: 18px;
    }
    .dialog-head p {
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 12px;
    }
    .dialog-close {
      border: 0;
      background: transparent;
      color: #414552;
      cursor: pointer;
      font-size: 22px;
      line-height: 1;
      padding: 0 2px;
    }
    .dialog-body {
      padding: 16px 18px 18px;
      display: grid;
      gap: 14px;
      max-height: calc(100vh - 180px);
      overflow: auto;
    }
    .grid2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px 18px;
    }
    .grid3 {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px 18px;
    }
    .subsection {
      border-top: 1px solid #ececf2;
      padding-top: 12px;
    }
    .subsection h4 {
      margin: 0 0 8px;
      font-size: 15px;
    }
    .dialog-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      padding: 0 18px 18px;
    }
    .secondary {
      border: 1px solid #cfd3dd;
      border-radius: 4px;
      background: white;
      padding: 9px 14px;
      cursor: pointer;
    }
    .secondary:hover {
      border-color: #a8adc0;
    }
    .stage-label {
      font-size: 12px;
      fill: #535763;
    }
    .stage-title {
      font-size: 14px;
      font-weight: 700;
      fill: #1e1f25;
    }
    .anatomy-label {
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .04em;
      fill: #3f4350;
      text-transform: uppercase;
    }
    .anatomy-label-side {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: .04em;
      fill: #3f4350;
      text-transform: uppercase;
    }
    .anatomy-divider {
      stroke: rgba(83, 87, 99, 0.35);
      stroke-width: 1.4;
      stroke-dasharray: 4 4;
    }
    .anatomy-sector {
      opacity: 0.42;
    }
    .hoverable {
      cursor: pointer;
    }
    @media (max-width: 1100px) {
      .sim-card {
        grid-template-columns: 1fr;
      }
      .stage-pane {
        border-right: 0;
        border-bottom: 1px solid #ececf2;
      }
    }
    @media (max-width: 860px) {
      .shell {
        grid-template-columns: 1fr;
      }
      .sidebar {
        display: none;
      }
      .work {
        grid-template-rows: 64px 1fr;
      }
      .topbar {
        height: 64px;
      }
      .page {
        padding: 12px;
      }
      .grid2, .grid3 {
        grid-template-columns: 1fr;
      }
      #plot {
        height: 360px;
      }
    }
  </style>
</head>
<body>
  <form id="state_form">
    <div class="shell">
      <nav class="sidebar">
        <div class="sidebar-head">Menu</div>
        <div class="menu">
          <a class="active" href="#/simulation">Simulation</a>
          <a href="#/instructions">Instructions</a>
          <a href="#/about">About</a>
          <a href="#/disclaimer">Disclaimer</a>
        </div>
      </nav>

      <div class="work">
        <header class="topbar">Aqueous Humor Outflow Model</header>

        <div class="page">
          <section class="sim-card">
            <div class="stage-pane">
              <div class="stage-wrap">
                <svg id="setup_svg" class="ring" viewBox="0 0 520 520"></svg>
                <svg id="solution_svg" class="ring hidden" viewBox="0 0 620 520"></svg>
              </div>
              <div id="setup_summary" class="stage-meta"></div>
              <div id="solution_note" class="solution-note hidden">Waiting for the first solution.</div>
              <div id="solution_info" class="solution-info hidden">Hover the solution map to inspect local values.</div>
            </div>

            <div class="control-pane">
              <div class="field">
                <label>Mode</label>
                <select id="mode">
                  <option value="constant flow">constant flow</option>
                  <option value="constant pressure">constant pressure</option>
                </select>
              </div>

              <div class="field">
                <label>Eye</label>
                <select id="eye_side">
                  <option value="right">Right Eye (OD)</option>
                  <option value="left">Left Eye (OS)</option>
                </select>
              </div>

              <div class="field">
                <label id="qt_label">Flowrate (uL/min)</label>
                <input id="qt" type="number" step="0.1" value="2.0" />
              </div>

              <label class="checkline">
                <input id="unconventional" type="checkbox" />
                <span>Include unconventional outflow</span>
              </label>
              <div class="hint">With Auto RTM enabled, Rtm is recalibrated to keep the baseline IOP target, so this option may change Rtm/resistance more than displayed IOP.</div>

              <div class="field">
                <label id="iop_label">Baseline IOP (mmHg)</label>
                <input id="iop" type="number" step="0.1" value="15.09" />
              </div>
              <div id="iop_hint" class="hint">In constant flow mode, this controls the inferred baseline TM resistance.</div>

              <button type="button" id="open_ccs" class="primary-chip">
                <span>Collector Channel</span>
                <span class="plus">+</span>
              </button>

              <div class="surgery-block">
                <h3 class="surgery-title">Surgeries</h3>

                <div class="surgery-item">
                  <div class="surgery-copy">
                    <strong>Trabeculectomies</strong>
                    <span id="trab_summary">Use preset clock-hours or explicit SC node ranges.</span>
                  </div>
                  <button type="button" class="icon-button" id="open_trab">+</button>
                </div>

                <div class="surgery-item">
                  <div class="surgery-copy">
                    <strong>Trabecular Bypass Stents</strong>
                    <span id="stent_summary">Choose stent nodes and edit the stent geometry.</span>
                  </div>
                  <button type="button" class="icon-button" id="open_stent">+</button>
                </div>

                <div class="surgery-item">
                  <div class="surgery-copy">
                    <strong>Sinusotomies</strong>
                    <span id="sinus_summary">Optional additional SC bypass ranges.</span>
                  </div>
                  <button type="button" class="icon-button" id="open_sinus">+</button>
                </div>

                <div class="surgery-item">
                  <div class="surgery-copy">
                    <strong>YAG holes</strong>
                    <span id="yag_summary">Preset count or explicit YAG node locations.</span>
                  </div>
                  <button type="button" class="icon-button" id="open_yag">+</button>
                </div>
              </div>

              <div class="status" id="status"></div>

              <div class="bottom-actions">
                <button type="button" class="text-action" id="viewToggle">View Solution</button>
                <button type="button" class="text-action" id="open_constants">Edit Constants</button>
                <button type="button" class="text-action danger" id="resetBtn">Reset</button>
                <button type="button" class="solve" id="solveBtn">Solve</button>
              </div>
            </div>
          </section>

          <section class="plot-card">
            <div class="plot-head">
              <h3>Profiles</h3>
              <select id="plot_type">
                <option value="pressure">Pressure distribution</option>
                <option value="height">Canal height</option>
                <option value="jcc">Collector channel flow</option>
              </select>
            </div>
            <div id="plot"></div>
          </section>
        </div>
      </div>
    </div>

    <dialog id="constants_dialog">
      <div class="dialog-head">
        <div>
          <h3>Edit Constants</h3>
          <p>Advanced constants, geometry, and segment-profile settings.</p>
        </div>
        <button type="button" class="dialog-close" data-close="constants_dialog">×</button>
      </div>
      <div class="dialog-body">
        <div class="grid2">
          <div class="field">
            <label>Geometry</label>
            <select id="geometry">
              <option value="ellipse">ellipse</option>
              <option value="rectangle">rectangle</option>
            </select>
          </div>
          <div class="field">
            <label>Pev</label>
            <input id="pev" type="number" step="0.1" value="8.0" />
          </div>
        </div>
        <div class="grid2">
          <div class="field">
            <label>Rtm</label>
            <input id="rtm" type="number" step="0.1" placeholder="default" />
          </div>
          <div class="field">
            <label class="checkline"><input id="auto_rtm" type="checkbox" checked /><span>Auto RTM from baseline IOP</span></label>
            <div class="hint">Auto RTM can absorb the visible IOP effect of unconventional flow by fitting Rtm to the baseline IOP.</div>
          </div>
        </div>

        <div class="subsection">
          <h4>Model constants</h4>
          <div class="grid3">
            <div class="field"><label>N collector channels</label><input id="n" type="number" step="1" value="30" /></div>
            <div class="field"><label>M nodes per CC</label><input id="m" type="number" step="1" value="40" /></div>
            <div class="field"><label>Etm</label><input id="etm" type="number" step="0.1" value="13" /></div>
            <div class="field"><label>h0 (um)</label><input id="h0" type="number" step="0.1" value="20" /></div>
            <div class="field"><label>hs (um)</label><input id="hs" type="number" step="0.1" value="3.0" /></div>
            <div class="field"><label>Rcc override</label><input id="rcc" type="number" step="0.1" placeholder="auto (~1.5 at 15 mmHg)" /></div>
            <div class="field"><label>Qu</label><input id="qu" type="number" step="0.01" value="0.28" /></div>
            <div class="field"><label>max error</label><input id="max_error" type="number" step="0.00001" value="0.0001" /></div>
            <div class="field"><label>Stent beta</label><input id="beta" type="number" step="0.1" placeholder="1.0" /></div>
          </div>
        </div>

        <div class="subsection">
          <h4>Variable segment profiles</h4>
          <div class="field">
            <label>TM resistance profile</label>
            <textarea id="rtm_profile" placeholder="24 or 24,24,... (12 values) or 1:24, 2:30, ..., 12:24"></textarea>
            <div class="hint">Takes 12 clock-hour values. Overrides scalar RTM and auto RTM when present.</div>
          </div>
          <div class="field">
            <label>TM full node array</label>
            <textarea id="rtm_node_values" placeholder="2400 or 2400,2400,... (N*M values)"></textarea>
            <div class="hint">Direct local TM resistor values for every SC node. Use 1 value to repeat uniformly or exactly N*M values to import a fully non-uniform TM map.</div>
          </div>
          <div class="field">
            <label>SC baseline height profile</label>
            <textarea id="h0_profile" placeholder="20 or 20,20,... (N values) or 1:20, 2:18, ..., N:20"></textarea>
            <div class="hint">Takes N segment values, where N is the current collector-channel count.</div>
          </div>
          <div class="field">
            <label>SC full node array</label>
            <textarea id="h0_node_values" placeholder="20 or 20,20,... (N*M values)"></textarea>
            <div class="hint">Direct baseline SC height at every node. Use 1 value to repeat uniformly or exactly N*M values for a fully non-uniform SC baseline map.</div>
          </div>
          <div class="field">
            <label>TM node resistance overrides</label>
            <textarea id="rtm_node_overrides" placeholder="120:2400, 121-140:3200"></textarea>
            <div class="hint">Format is node:value or start-end:value. These are local per-node TM resistor values and apply after auto RTM, scalar RTM, or the 12-segment TM profile.</div>
          </div>
          <div class="field">
            <label>SC node height overrides</label>
            <textarea id="h0_node_overrides" placeholder="120:20, 121-140:14"></textarea>
            <div class="hint">Use this to locally modify baseline SC height, which is the closest direct handle on local SC circumferential resistance in the current solver.</div>
          </div>
          <div class="field">
            <label>SC conductance multiplier</label>
            <textarea id="gsc_multiplier" placeholder="1.0 or 1.0,1.0,... (N*M values) or 120:0.5, 121-140:2.0"></textarea>
            <div class="hint">Applies a multiplicative factor to each circumferential SC segment conductance between node i and i+1. Accepts either 1/exact N*M values or segment:value overrides.</div>
          </div>
          <div class="field">
            <label>SC conductance override</label>
            <textarea id="gsc_override" placeholder="0.002 or 0.002,0.002,... (N*M values) or 120:0.0, 121-140:0.003"></textarea>
            <div class="hint">Directly replaces the computed conductance of selected SC segments. Segment i means the link between node i and node i+1.</div>
          </div>
        </div>
      </div>
      <div class="dialog-actions">
        <button type="button" class="secondary" data-close="constants_dialog">Done</button>
      </div>
    </dialog>

    <dialog id="ccs_dialog">
      <div class="dialog-head">
        <div>
          <h3>Collector Channels</h3>
          <p>Manual non-uniform CC distribution.</p>
        </div>
        <button type="button" class="dialog-close" data-close="ccs_dialog">×</button>
      </div>
      <div class="dialog-body">
        <div class="field">
          <label>Manual CC distribution</label>
          <textarea id="ccs" placeholder="0:1, 40:1, 80:0.5, 120:2"></textarea>
          <div class="hint">Format is node:per-channel conductance multiplier. A multiplier changes only that collector channel; leave blank for the uniform default from N and M.</div>
        </div>
      </div>
      <div class="dialog-actions">
        <button type="button" class="secondary" data-close="ccs_dialog">Done</button>
      </div>
    </dialog>

    <dialog id="trab_dialog">
      <div class="dialog-head">
        <div>
          <h3>Trabeculectomies</h3>
          <p>Use clock-hour presets or explicit SC node ranges.</p>
        </div>
        <button type="button" class="dialog-close" data-close="trab_dialog">×</button>
      </div>
      <div class="dialog-body">
        <input id="stent_node" type="hidden" value="0" />
        <select id="surgery" class="hidden">
          <option>None</option>
          <option>Trabeculotomy</option>
          <option>YAG holes</option>
          <option>iStent</option>
        </select>

        <div class="field">
          <label>Trab hours</label>
          <select id="trab_hours">
            <option>1</option>
            <option>4</option>
            <option>12</option>
          </select>
        </div>
        <div class="field">
          <label>Trabeculotomy ranges</label>
          <textarea id="trabeculotomies" placeholder="0-99, 300-399"></textarea>
          <div id="trabeculotomy_hint" class="hint">Leave blank to use the selected clock-hour preset.</div>
        </div>
      </div>
      <div class="dialog-actions">
        <button type="button" class="secondary" data-close="trab_dialog">Done</button>
      </div>
    </dialog>

    <dialog id="sinus_dialog">
      <div class="dialog-head">
        <div>
          <h3>Sinusotomies</h3>
          <p>Optional SC bypass ranges, independent of the primary surgery preset.</p>
        </div>
        <button type="button" class="dialog-close" data-close="sinus_dialog">×</button>
      </div>
      <div class="dialog-body">
        <div class="field">
          <label>Sinusotomy ranges</label>
          <textarea id="sinusotomies" placeholder="120-180, 620-700"></textarea>
          <div class="hint">Ranges are SC node indexes and can be combined with other interventions.</div>
        </div>
      </div>
      <div class="dialog-actions">
        <button type="button" class="secondary" data-close="sinus_dialog">Done</button>
      </div>
    </dialog>

    <dialog id="yag_dialog">
      <div class="dialog-head">
        <div>
          <h3>YAG Holes</h3>
          <p>Preset counts or explicit YAG node locations.</p>
        </div>
        <button type="button" class="dialog-close" data-close="yag_dialog">×</button>
      </div>
      <div class="dialog-body">
        <div class="field">
          <label>YAG hole count</label>
          <input id="yag_holes" type="number" step="1" value="2" />
        </div>
        <div class="field">
          <label>YAG hole nodes</label>
          <input id="yag_holes_list" type="text" placeholder="0, 200, 400" />
          <div id="yag_nodes_hint" class="hint">Leave blank to use the preset count above.</div>
        </div>
      </div>
      <div class="dialog-actions">
        <button type="button" class="secondary" data-close="yag_dialog">Done</button>
      </div>
    </dialog>

    <dialog id="stent_dialog">
      <div class="dialog-head">
        <div>
          <h3>Trabecular Bypass Stents</h3>
          <p>Choose nodes and edit the stent geometry that will be applied there.</p>
        </div>
        <button type="button" class="dialog-close" data-close="stent_dialog">×</button>
      </div>
      <div class="dialog-body">
        <div class="field">
          <label>iStent nodes</label>
          <input id="stent_nodes" type="text" placeholder="0, 300, 600" />
          <div id="stent_nodes_hint" class="hint">If the primary surgery is iStent and this is blank, node 0 is used.</div>
        </div>

        <div class="subsection">
          <h4>Stent editor</h4>
          <div class="hint">iStent inject example: length 230 um, inlet offset 115 um, width 50 um, height 50 um, after height 150 um, inlet conductance 42.15, two-way checked, ellipse geometry.</div>
          <div class="grid2">
            <div class="field"><label>Name</label><input id="stent_name" type="text" value="Custom iStent" /></div>
            <div class="field"><label>Stent geometry</label>
              <select id="stent_geometry">
                <option value="">same as solver</option>
                <option value="ellipse">ellipse</option>
                <option value="rectangle">rectangle</option>
              </select>
            </div>
          </div>
          <div class="grid3">
            <div class="field"><label>Length (um)</label><input id="stent_length" type="number" step="10" value="1000" /></div>
            <div class="field"><label>Inlet offset (um)</label><input id="stent_loc_inlet" type="number" step="10" value="0" /></div>
            <div class="field"><label>Width (um)</label><input id="stent_width" type="number" step="1" value="120" /></div>
            <div class="field"><label>Height (um)</label><input id="stent_height" type="number" step="1" value="60" /></div>
            <div class="field"><label>After height (um)</label><input id="stent_h_after" type="number" step="1" placeholder="same as height" /></div>
            <div class="field"><label>Inlet conductance</label><input id="stent_g_inlet" type="number" step="0.001" value="0" /></div>
            <div class="field"><label>Before dilation nodes</label><input id="stent_l_before" type="number" step="1" value="0" /></div>
            <div class="field"><label>After dilation nodes</label><input id="stent_l_after" type="number" step="1" value="0" /></div>
            <div class="field"><label class="checkline"><input id="stent_two_way" type="checkbox" checked /><span>Two-way inlet</span></label></div>
          </div>
          <div class="subsection">
            <h4>Windowed stent options</h4>
            <div class="grid3">
              <div class="field"><label>Number of windows</label><input id="stent_n_windows" type="number" step="1" value="0" /></div>
              <div class="field"><label>Window length (um)</label><input id="stent_l_window" type="number" step="10" placeholder="required if windows > 0" /></div>
              <div class="field"><label>Window height (um)</label><input id="stent_h_window" type="number" step="1" placeholder="required if windows > 0" /></div>
              <div class="field"><label>Spine length (um)</label><input id="stent_l_spine" type="number" step="10" placeholder="required if windows > 0" /></div>
              <div class="field"><label>Spine height (um)</label><input id="stent_h_spine" type="number" step="1" placeholder="required if windows > 0" /></div>
            </div>
          </div>
        </div>
      </div>
      <div class="dialog-actions">
        <button type="button" class="secondary" data-close="stent_dialog">Done</button>
      </div>
    </dialog>
  </form>

  <script>
    const $ = (id) => document.getElementById(id);
    let lastResult = null;
    let lastSolvedPayload = null;
    let resultDirty = false;
    let viewSolution = false;

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
        Superior: "rgba(102, 167, 214, 0.20)",
        Inferior: "rgba(165, 132, 201, 0.18)",
        Temporal: "rgba(221, 166, 94, 0.18)",
        Nasal: "rgba(106, 176, 117, 0.18)",
      };
    }

    function drawTicks(cx, cy, radius) {
      const parts = [];
      for (let deg = 0; deg < 360; deg += 10) {
        const major = deg % 20 === 0;
        const inner = polarPoint(cx, cy, radius - (major ? 20 : 12), deg);
        const outer = polarPoint(cx, cy, radius, deg);
        parts.push(`<line x1="${inner.x.toFixed(2)}" y1="${inner.y.toFixed(2)}" x2="${outer.x.toFixed(2)}" y2="${outer.y.toFixed(2)}" stroke="${major ? '#1d84e8' : '#80858f'}" stroke-width="${major ? 2.4 : 1.2}" opacity="0.92"></line>`);
        if (major) {
          const text = polarPoint(cx, cy, radius - 30, deg);
          parts.push(`<text x="${text.x.toFixed(2)}" y="${text.y.toFixed(2)}" text-anchor="middle" dominant-baseline="central" class="stage-label">${deg}°</text>`);
        }
      }
      return parts.join("");
    }

    function drawAnatomyOverlay(cx, cy, innerRadius, outerRadius, frameWidth, options = {}) {
      const labels = eyeLabels();
      const colors = anatomyColors();
      const boundaries = [45, 135, 225, 315];
      const parts = [];
      const includeSectors = options.includeSectors !== false;
      const includeLabels = options.includeLabels !== false;
      const includeDividers = options.includeDividers !== false;

      if (includeSectors) {
        parts.push(`<path class="anatomy-sector" d="${annularSectorPath(cx, cy, innerRadius, outerRadius, 315, 90)}" fill="${colors.Superior}"></path>`);
        parts.push(`<path class="anatomy-sector" d="${annularSectorPath(cx, cy, innerRadius, outerRadius, 45, 90)}" fill="${colors[labels.right]}"></path>`);
        parts.push(`<path class="anatomy-sector" d="${annularSectorPath(cx, cy, innerRadius, outerRadius, 135, 90)}" fill="${colors.Inferior}"></path>`);
        parts.push(`<path class="anatomy-sector" d="${annularSectorPath(cx, cy, innerRadius, outerRadius, 225, 90)}" fill="${colors[labels.left]}"></path>`);
      }

      if (includeDividers) {
        boundaries.forEach((degrees) => {
          const inner = polarPoint(cx, cy, innerRadius, degrees);
          const outer = polarPoint(cx, cy, outerRadius, degrees);
          parts.push(`<line class="anatomy-divider" x1="${inner.x.toFixed(2)}" y1="${inner.y.toFixed(2)}" x2="${outer.x.toFixed(2)}" y2="${outer.y.toFixed(2)}"></line>`);
        });
      }

      if (includeLabels) {
        const leftX = Math.max(24, cx - outerRadius - 50);
        const rightX = Math.min(frameWidth - 24, cx + outerRadius + 50);
        parts.push(`<text x="${cx.toFixed(2)}" y="${(cy - outerRadius - 34).toFixed(2)}" text-anchor="middle" dominant-baseline="central" class="anatomy-label">Superior</text>`);
        parts.push(`<text x="${cx.toFixed(2)}" y="${(cy + outerRadius + 34).toFixed(2)}" text-anchor="middle" dominant-baseline="central" class="anatomy-label">Inferior</text>`);
        parts.push(`<text x="${leftX.toFixed(2)}" y="${cy.toFixed(2)}" text-anchor="start" dominant-baseline="central" class="anatomy-label-side">${labels.left}</text>`);
        parts.push(`<text x="${rightX.toFixed(2)}" y="${cy.toFixed(2)}" text-anchor="end" dominant-baseline="central" class="anatomy-label-side">${labels.right}</text>`);
      }
      return parts.join("");
    }

    function anatomyAxisGuide(series) {
      if (!series || !Array.isArray(series.x) || !series.x.length) return null;
      const minX = Math.min(...series.x);
      const maxX = Math.max(...series.x);
      if (!Number.isFinite(minX) || !Number.isFinite(maxX) || maxX <= minX) return null;

      const labels = eyeLabels();
      const colors = anatomyColors();
      const span = maxX - minX;
      const quarters = [0, 0.25, 0.5, 0.75, 1].map((ratio) => minX + span * ratio);
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
        ticktext: [
          `${fmt(minX)}<br><b>Superior</b>`,
          `${fmt(minX + span * 0.25)}<br><b>${labels.right}</b>`,
          `${fmt(minX + span * 0.5)}<br><b>Inferior</b>`,
          `${fmt(minX + span * 0.75)}<br><b>${labels.left}</b>`,
          `${fmt(maxX)}<br><b>Superior</b>`,
        ],
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
            line: { color: "rgba(83, 87, 99, 0.18)", width: 1, dash: "dot" },
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
      return Math.max(1, range.end - range.start + 1);
    }

    function renderSetupRing(currentPayload, result) {
      const svg = $("setup_svg");
      const model = collectSetupModel(currentPayload, result);
      const labels = eyeLabels();
      const cx = 260;
      const cy = 260;
      const ccRadius = 188;
      const canalRadius = 154;
      const tmRadius = 118;
      const parts = [];

      parts.push(`<rect x="0" y="0" width="520" height="520" fill="transparent"></rect>`);
      parts.push(drawTicks(cx, cy, 222));
      parts.push(drawAnatomyOverlay(cx, cy, tmRadius - 20, ccRadius + 24, 520, { includeLabels: false, includeDividers: false }));
      parts.push(`<circle cx="${cx}" cy="${cy}" r="${ccRadius}" fill="none" stroke="#c4c4c4" stroke-width="52"></circle>`);
      parts.push(`<circle cx="${cx}" cy="${cy}" r="${tmRadius}" fill="none" stroke="#ef3932" stroke-width="28"></circle>`);

      model.ccs.forEach((cc) => {
        const angle = 360 * normalizeNode(cc.loc, model.totalNodes) / model.totalNodes;
        const inner = polarPoint(cx, cy, ccRadius - 28, angle);
        const outer = polarPoint(cx, cy, ccRadius + 32, angle);
        parts.push(`<line x1="${inner.x.toFixed(2)}" y1="${inner.y.toFixed(2)}" x2="${outer.x.toFixed(2)}" y2="${outer.y.toFixed(2)}" stroke="#1d84e8" stroke-width="3"></line>`);
      });

      if (model.scProfile) {
        const minValue = Math.min(...model.scProfile);
        const maxValue = Math.max(...model.scProfile);
        model.scProfile.forEach((value, idx) => {
          const start = 360 * idx / model.scProfile.length;
          const span = 360 / model.scProfile.length - 0.9;
          const color = mixColors("#d7d7d7", "#7f7f7f", maxValue === minValue ? 0.5 : (value - minValue) / (maxValue - minValue));
          parts.push(`<path d="${arcPath(cx, cy, canalRadius, start, span)}" stroke="${color}" stroke-width="50" fill="none" opacity="0.52"></path>`);
        });
      }

      model.tmProfile?.forEach((value, idx, arr) => {
        const start = 360 * idx / arr.length;
        const span = 360 / arr.length - 1;
        const minValue = Math.min(...arr);
        const maxValue = Math.max(...arr);
        const color = mixColors("#ff8179", "#b90f0a", maxValue === minValue ? 0.45 : (value - minValue) / (maxValue - minValue));
        parts.push(`<path d="${arcPath(cx, cy, tmRadius, start, span)}" stroke="${color}" stroke-width="28" fill="none" opacity="0.95"></path>`);
      });

      model.trabeculotomies.forEach((range) => {
        const start = 360 * normalizeNode(range.start, model.totalNodes) / model.totalNodes;
        const span = 360 * rangeSpanNodes(range) / model.totalNodes;
        parts.push(`<path d="${arcPath(cx, cy, tmRadius, start, span)}" stroke="#14a062" stroke-width="32" fill="none" stroke-linecap="round"></path>`);
      });

      model.sinusotomies.forEach((range) => {
        const start = 360 * normalizeNode(range.start, model.totalNodes) / model.totalNodes;
        const span = 360 * rangeSpanNodes(range) / model.totalNodes;
        parts.push(`<path d="${arcPath(cx, cy, canalRadius, start, span)}" stroke="#d9782b" stroke-width="14" fill="none" stroke-dasharray="3 6" stroke-linecap="round"></path>`);
      });

      model.stents.forEach((stent) => {
        const start = 360 * normalizeNode(stent.loc, model.totalNodes) / model.totalNodes;
        const span = 360 * Math.max(1, stent.span_nodes || 1) / model.totalNodes;
        parts.push(`<path d="${arcPath(cx, cy, canalRadius - 10, start, span)}" stroke="#2075b8" stroke-width="14" fill="none" stroke-linecap="round"></path>`);
      });

      model.yagHoles.forEach((node) => {
        const point = polarPoint(cx, cy, tmRadius - 20, 360 * normalizeNode(node, model.totalNodes) / model.totalNodes);
        parts.push(`<circle cx="${point.x.toFixed(2)}" cy="${point.y.toFixed(2)}" r="6" fill="white" stroke="#bf3f6d" stroke-width="3"></circle>`);
      });

      parts.push(drawAnatomyOverlay(cx, cy, tmRadius - 20, ccRadius + 24, 520, { includeSectors: false }));
      parts.push(`<text x="${cx}" y="${cy - 4}" text-anchor="middle" class="stage-title">Anterior Chamber</text>`);
      parts.push(`<text x="${cx - 92}" y="${cy - 178}" transform="rotate(-12 ${cx - 92} ${cy - 178})" class="stage-title">Collector Channels</text>`);
      parts.push(`<text x="${cx - 76}" y="${cy - 128}" transform="rotate(-12 ${cx - 76} ${cy - 128})" class="stage-title">Schlemm's Canal</text>`);
      parts.push(`<text x="${cx - 62}" y="${cy - 82}" transform="rotate(-14 ${cx - 62} ${cy - 82})" class="stage-title">Trabecular Meshwork</text>`);
      svg.innerHTML = parts.join("");

      $("setup_summary").innerHTML = `
        <div><b>${model.ccs.length}</b> collector channels across <b>${model.totalNodes}</b> SC nodes.</div>
        <div>Interventions: trab <b>${model.trabeculotomies.length}</b>, sinus <b>${model.sinusotomies.length}</b>, YAG <b>${model.yagHoles.length}</b>, stents <b>${model.stents.length}</b>.</div>
        <div>Profiles: TM ${model.tmProfile ? "<b>variable</b>" : "scalar"} | SC height ${model.scProfile ? "<b>variable</b>" : "scalar"}.</div>
        ${model.hasGscControl ? "<div>SC circumferential conductance: <b>customized</b>.</div>" : ""}
        <div>Eye orientation: <b>${labels.eye}</b> with <b>${labels.left}</b> on the left and <b>${labels.right}</b> on the right.</div>
      `;
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
        rows.push(`<div>Hover the solution map or a collector channel to inspect local values.</div>`);
      }
      $("solution_info").innerHTML = rows.join("");
    }

    function renderSolutionRing(result, solvedPayload) {
      const svg = $("solution_svg");
      const note = $("solution_note");
      if (!result) {
        svg.innerHTML = `<rect x="0" y="0" width="620" height="520" fill="transparent"></rect><text x="310" y="250" text-anchor="middle" class="stage-title">No solution yet</text><text x="310" y="276" text-anchor="middle" class="stage-label">Press Solve to render the local solution map.</text>`;
        note.textContent = "Waiting for the first solution.";
        renderSolutionInfo({ metrics: { iop: NaN, flowrate: NaN, resistance: NaN } });
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
      const cx = 340;
      const cy = 260;
      const pressureRadius = 166;
      const heightRadius = 124;
      const ccRadius = 192;

      parts.push(`<defs><linearGradient id="pressureScale" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="#ef3932"></stop><stop offset="100%" stop-color="#1d84e8"></stop></linearGradient></defs>`);
      parts.push(`<rect x="0" y="0" width="620" height="520" fill="transparent"></rect>`);
      parts.push(`<rect x="28" y="62" width="20" height="280" rx="3" fill="url(#pressureScale)"></rect>`);
      parts.push(`<text x="58" y="72" class="stage-label">${fmt(pHigh)} mmHg</text>`);
      parts.push(`<text x="58" y="342" class="stage-label">${fmt(pLow)} mmHg</text>`);
      parts.push(drawTicks(cx, cy, 226));
      parts.push(drawAnatomyOverlay(cx, cy, heightRadius - 18, ccRadius + 18, 620, { includeLabels: false, includeDividers: false }));

      pressure.forEach((value, idx) => {
        const start = 360 * idx / totalNodes;
        const span = 360 / totalNodes + 0.12;
        const color = mixColors("#1d84e8", "#ef3932", pHigh === pLow ? 0.5 : (value - pLow) / (pHigh - pLow));
        parts.push(`<path class="hoverable" data-kind="node" data-theta="${(360 * idx / totalNodes).toFixed(2)}" data-pressure="${value}" data-height="${heights[idx]}" d="${arcPath(cx, cy, pressureRadius, start, span)}" stroke="${color}" stroke-width="28" fill="none"></path>`);
      });

      heights.forEach((value, idx) => {
        const start = 360 * idx / totalNodes;
        const span = 360 / totalNodes + 0.12;
        const color = mixColors("#efe7cd", "#147c72", hHigh === hLow ? 0.5 : (value - hLow) / (hHigh - hLow));
        parts.push(`<path d="${arcPath(cx, cy, heightRadius, start, span)}" stroke="${color}" stroke-width="18" fill="none" opacity="0.96"></path>`);
      });

      ccs.slice(0, jcc.length).forEach((cc, idx) => {
        const angle = 360 * normalizeNode(cc.loc, totalNodes) / totalNodes;
        const inner = polarPoint(cx, cy, ccRadius, angle);
        const outer = polarPoint(cx, cy, ccRadius + 10 + 24 * (jcc[idx] / maxFlow), angle);
        const color = mixColors("#9bccfb", "#1d84e8", jcc[idx] / maxFlow);
        parts.push(`<line class="hoverable" data-kind="cc" data-loc="${cc.loc}" data-flow="${jcc[idx]}" x1="${inner.x.toFixed(2)}" y1="${inner.y.toFixed(2)}" x2="${outer.x.toFixed(2)}" y2="${outer.y.toFixed(2)}" stroke="${color}" stroke-width="4" stroke-linecap="round"></line>`);
      });

      parts.push(drawAnatomyOverlay(cx, cy, heightRadius - 18, ccRadius + 18, 620, { includeSectors: false }));
      parts.push(`<text x="${cx}" y="${cy - 8}" text-anchor="middle" class="stage-title">Solution Map</text>`);
      parts.push(`<text x="${cx}" y="${cy + 16}" text-anchor="middle" class="stage-label">Outer ring: pressure | Inner ring: canal height</text>`);
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
        ? "Showing the latest solved field. Some inputs have changed since that solve."
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
        font: { color: "#1e1f25" },
        margin: { l: 70, r: 22, t: 56, b: kind === "jcc" ? 58 : 92 },
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

    function statusFromMeta(meta) {
      if (!meta) return "";
      const parts = [];
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

    function updateModeUI() {
      const isConstantPressure = $("mode").value === "constant pressure";
      const hasVariableRtmProfile = $("rtm_profile").value.trim().length > 0;
      const hasFullRtmArray = $("rtm_node_values").value.trim().length > 0;
      const autoRtmEnabled = $("auto_rtm").checked && !isConstantPressure && !hasVariableRtmProfile && !hasFullRtmArray;
      $("iop_label").textContent = isConstantPressure ? "IOP (mmHg)" : "Baseline IOP (mmHg)";
      $("qt_label").textContent = isConstantPressure ? "Flowrate reference (uL/min)" : "Flowrate (uL/min)";
      $("iop_hint").textContent = isConstantPressure
        ? "In constant pressure mode, this is the target IOP for the solve."
        : hasFullRtmArray
          ? "Baseline IOP and scalar RTM are ignored while a full TM node array is present."
          : hasVariableRtmProfile
          ? "Baseline IOP is ignored while a TM resistance profile is present."
          : "In constant flow mode, this is used to estimate baseline TM resistance.";
      $("auto_rtm").disabled = isConstantPressure || hasVariableRtmProfile || hasFullRtmArray;
      $("rtm").disabled = autoRtmEnabled || hasVariableRtmProfile || hasFullRtmArray;
      $("rtm").placeholder = hasFullRtmArray ? "overridden by full TM node array" : (hasVariableRtmProfile ? "overridden by TM profile" : (autoRtmEnabled ? "derived automatically" : "default"));
    }

    function summarizeRanges(text) {
      const ranges = parseRangesText(text);
      return ranges.length ? `${ranges.length} range${ranges.length === 1 ? "" : "s"}` : "none added";
    }

    function updateInterventionUI() {
      const surgery = $("surgery").value;
      const trabRanges = parseRangesText($("trabeculotomies").value);
      const sinusRanges = parseRangesText($("sinusotomies").value);
      const stentNodes = parseNodeListText($("stent_nodes").value);
      const yagNodes = parseNodeListText($("yag_holes_list").value);
      const yagCount = Math.max(0, Math.round(numberValue($("yag_holes").value, 2) || 0));

      $("trab_summary").textContent = trabRanges.length
        ? `${trabRanges.length} explicit range${trabRanges.length === 1 ? "" : "s"}`
        : surgery === "Trabeculotomy"
          ? `${$("trab_hours").value}-hour preset selected`
          : "Use preset clock-hours or explicit SC node ranges.";
      $("sinus_summary").textContent = sinusRanges.length
        ? `${sinusRanges.length} sinusotomy range${sinusRanges.length === 1 ? "" : "s"}`
        : "Optional additional SC bypass ranges.";
      $("stent_summary").textContent = stentNodes.length
        ? `${stentNodes.length} stent node${stentNodes.length === 1 ? "" : "s"}`
        : surgery === "iStent"
          ? "Primary stent preset active; blank nodes default to node 0."
          : "Choose stent nodes and edit the stent geometry.";
      $("yag_summary").textContent = yagNodes.length
        ? `${yagNodes.length} explicit YAG node${yagNodes.length === 1 ? "" : "s"}`
        : surgery === "YAG holes"
          ? `${yagCount} preset YAG hole${yagCount === 1 ? "" : "s"}`
          : "Preset count or explicit YAG node locations.";

      $("trabeculotomy_hint").textContent = surgery === "Trabeculotomy"
        ? "Leave blank to use the selected clock-hour preset."
        : "Optional SC node ranges; explicit values can be combined with other interventions.";
      $("yag_nodes_hint").textContent = surgery === "YAG holes"
        ? "Leave blank to use the preset count above."
        : "Optional explicit YAG node locations.";
      $("stent_nodes_hint").textContent = surgery === "iStent"
        ? "If left blank, node 0 will receive one stent."
        : "Optional explicit stent nodes for the geometry below.";
    }

    function refreshViewToggle() {
      $("viewToggle").textContent = viewSolution ? "View Setup" : "View Solution";
      $("setup_svg").classList.toggle("hidden", viewSolution);
      $("setup_summary").classList.toggle("hidden", viewSolution);
      $("solution_svg").classList.toggle("hidden", !viewSolution);
      $("solution_note").classList.toggle("hidden", !viewSolution);
      $("solution_info").classList.toggle("hidden", !viewSolution);
    }

    function refreshVisuals() {
      const currentPayload = payload();
      renderSetupRing(currentPayload, lastResult);
      renderSolutionRing(lastResult, lastSolvedPayload || currentPayload);
      refreshViewToggle();
    }

    function markResultDirty() {
      resultDirty = !!lastResult;
      refreshVisuals();
    }

    function openDialog(id) {
      $(id).showModal();
    }

    function setPrimarySurgery(value) {
      $("surgery").value = value;
      updateInterventionUI();
    }

    function resetState() {
      $("state_form").reset();
      $("surgery").value = "None";
      viewSolution = false;
      lastResult = null;
      lastSolvedPayload = null;
      resultDirty = false;
      $("status").textContent = "";
      updateModeUI();
      updateInterventionUI();
      refreshVisuals();
      Plotly.purge("plot");
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
        viewSolution = true;
        plotSeries(data);
        refreshVisuals();
        $("status").textContent = statusFromMeta(data.meta);
      } catch (err) {
        $("status").textContent = err.message || String(err);
      } finally {
        $("solveBtn").disabled = false;
      }
    }

    document.querySelectorAll("[data-close]").forEach((button) => {
      button.addEventListener("click", () => {
        $(button.dataset.close).close();
      });
    });

    $("open_constants").addEventListener("click", () => openDialog("constants_dialog"));
    $("open_ccs").addEventListener("click", () => openDialog("ccs_dialog"));
    $("open_trab").addEventListener("click", () => {
      setPrimarySurgery("Trabeculotomy");
      openDialog("trab_dialog");
    });
    $("open_sinus").addEventListener("click", () => openDialog("sinus_dialog"));
    $("open_yag").addEventListener("click", () => {
      setPrimarySurgery("YAG holes");
      openDialog("yag_dialog");
    });
    $("open_stent").addEventListener("click", () => {
      setPrimarySurgery("iStent");
      openDialog("stent_dialog");
    });

    $("solveBtn").addEventListener("click", solve);
    $("viewToggle").addEventListener("click", () => {
      viewSolution = !viewSolution;
      refreshViewToggle();
    });
    $("resetBtn").addEventListener("click", resetState);
    $("plot_type").addEventListener("change", () => {
      if (lastResult) plotSeries(lastResult);
    });
    $("eye_side").addEventListener("change", () => {
      refreshVisuals();
      if (lastResult) plotSeries(lastResult);
    });

    $("mode").addEventListener("change", () => {
      updateModeUI();
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

    ["trabeculotomies", "trab_hours", "sinusotomies", "stent_nodes", "yag_holes", "yag_holes_list"].forEach((id) => {
      $(id).addEventListener("input", updateInterventionUI);
      $(id).addEventListener("change", updateInterventionUI);
    });

    document.querySelectorAll("input, select, textarea").forEach((element) => {
      if (["mode", "auto_rtm", "rtm_profile", "rtm_node_values", "plot_type", "eye_side", "trabeculotomies", "trab_hours", "sinusotomies", "stent_nodes", "yag_holes", "yag_holes_list"].includes(element.id)) return;
      element.addEventListener("input", markResultDirty);
      element.addEventListener("change", markResultDirty);
    });

    updateModeUI();
    updateInterventionUI();
    refreshVisuals();
  </script>
</body>
</html>
"""


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
    print("Northwestern-style local calculator running. Press Ctrl+C to stop.")

    threading.Timer(0.4, lambda: webbrowser.open(local_url, new=1)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main() -> int:
    import sys

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
