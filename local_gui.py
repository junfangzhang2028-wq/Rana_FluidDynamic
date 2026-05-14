from __future__ import annotations

import contextlib
import io
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

import matplotlib


matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


REPO_ROOT = Path(__file__).resolve().parent
PROJECT_DIR = REPO_ROOT / "m-johnson2-aqueous-outflow-8fb729748300_Modified"

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

os.chdir(PROJECT_DIR)

from offline import outputs_trial as ot
from offline import solver as md


def build_istent() -> md.Stent:
    return md.Stent(
        name="iStent (R)",
        length=1000.0,
        loc_inlet=0.0,
        w=120.0,
        hd=60.0,
        two_way=True,
        l_before=0,
        l_after=0,
    )


class LocalAqueousOutflowApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Aqueous Outflow Model - Local Calculator")
        self.geometry("1120x760")
        self.minsize(980, 660)

        self.vars = {
            "mode": tk.StringVar(value="constant flow"),
            "geometry": tk.StringVar(value="ellipse"),
            "iop": tk.StringVar(value="7.0"),
            "qt": tk.StringVar(value="2.0"),
            "pev": tk.StringVar(value="8.0"),
            "rtm": tk.StringVar(value=""),
            "surgery": tk.StringVar(value="None"),
            "trab_hours": tk.StringVar(value="1"),
            "yag_holes": tk.StringVar(value="2"),
            "stent_node": tk.StringVar(value="0"),
            "plot_type": tk.StringVar(value="Pressure distribution"),
        }

        self._build_layout()

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        controls = ttk.Frame(root, padding=(0, 0, 12, 0))
        controls.grid(row=0, column=0, sticky="ns")

        output = ttk.Frame(root)
        output.grid(row=0, column=1, sticky="nsew")
        output.columnconfigure(0, weight=1)
        output.rowconfigure(1, weight=1)

        self._build_controls(controls)
        self._build_output(output)

    def _build_controls(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Solve Settings", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

        row = 1
        row = self._combo(parent, row, "Mode", "mode", ["constant flow", "constant pressure"])
        row = self._combo(parent, row, "Geometry", "geometry", ["ellipse", "rectangle"])
        row = self._entry(parent, row, "IOP (mmHg)", "iop")
        row = self._entry(parent, row, "Flow rate Qt (uL/min)", "qt")
        row = self._entry(parent, row, "Pev (mmHg)", "pev")
        row = self._entry(parent, row, "Rtm override", "rtm")

        ttk.Separator(parent).grid(row=row, column=0, columnspan=2, sticky="ew", pady=12)
        row += 1
        ttk.Label(parent, text="Intervention", font=("Segoe UI", 12, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )
        row += 1

        row = self._combo(parent, row, "Surgery", "surgery", ["None", "Trabeculotomy", "YAG holes", "iStent"])
        row = self._combo(parent, row, "Trab hours", "trab_hours", ["1", "4", "12"])
        row = self._entry(parent, row, "YAG holes", "yag_holes")
        row = self._entry(parent, row, "Stent node", "stent_node")

        ttk.Separator(parent).grid(row=row, column=0, columnspan=2, sticky="ew", pady=12)
        row += 1
        row = self._combo(
            parent,
            row,
            "Plot",
            "plot_type",
            ["Pressure distribution", "Canal height", "Collector channel flow"],
        )

        run_button = ttk.Button(parent, text="Solve Locally", command=self.solve)
        run_button.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(14, 6))
        row += 1

        ttk.Button(parent, text="Reset Defaults", command=self.reset_defaults).grid(
            row=row, column=0, columnspan=2, sticky="ew"
        )

        parent.columnconfigure(1, minsize=170)

    def _build_output(self, parent: ttk.Frame) -> None:
        self.summary = tk.Text(parent, height=8, wrap="word")
        self.summary.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.summary.insert(
            "1.0",
            "Set parameters, choose an intervention, then click Solve Locally.\n"
            "This GUI calls the local offline model directly and does not use the online API.",
        )
        self.summary.configure(state="disabled")

        self.figure = Figure(figsize=(7.2, 4.8), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("No solution yet")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("value")
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")

    def _entry(self, parent: ttk.Frame, row: int, label: str, key: str) -> int:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(parent, textvariable=self.vars[key]).grid(row=row, column=1, sticky="ew", pady=4)
        return row + 1

    def _combo(self, parent: ttk.Frame, row: int, label: str, key: str, values: list[str]) -> int:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        box = ttk.Combobox(parent, textvariable=self.vars[key], values=values, state="readonly")
        box.grid(row=row, column=1, sticky="ew", pady=4)
        return row + 1

    def reset_defaults(self) -> None:
        defaults = {
            "mode": "constant flow",
            "geometry": "ellipse",
            "iop": "7.0",
            "qt": "2.0",
            "pev": "8.0",
            "rtm": "",
            "surgery": "None",
            "trab_hours": "1",
            "yag_holes": "2",
            "stent_node": "0",
            "plot_type": "Pressure distribution",
        }
        for key, value in defaults.items():
            self.vars[key].set(value)

    def solve(self) -> None:
        try:
            kwargs = self._collect_kwargs()
            with contextlib.redirect_stdout(io.StringIO()):
                solution = self._run_solution(kwargs)
            self._update_summary(solution)
            self._update_plot(solution, kwargs)
        except Exception as exc:
            messagebox.showerror("Solve failed", str(exc))

    def _collect_kwargs(self) -> dict:
        kwargs = {
            "geometry": self.vars["geometry"].get(),
            "pev": self._float("pev"),
        }

        rtm = self.vars["rtm"].get().strip()
        if rtm:
            kwargs["rtm"] = float(rtm)

        surgery = self.vars["surgery"].get()
        if surgery == "Trabeculotomy":
            kwargs["hours"] = int(self.vars["trab_hours"].get())
        elif surgery == "YAG holes":
            kwargs["n"] = int(self.vars["yag_holes"].get())
        elif surgery == "iStent":
            node = int(self.vars["stent_node"].get())
            kwargs["stents"] = [(node, build_istent())]

        return kwargs

    def _run_solution(self, kwargs: dict) -> dict:
        mode = self.vars["mode"].get()
        surgery = self.vars["surgery"].get()

        if surgery == "Trabeculotomy":
            return ot.solve_trabeculotomy(
                iop=self._float("iop"),
                qt=self._float("qt"),
                mode=mode,
                show_height=False,
                **kwargs,
            )

        if surgery == "YAG holes":
            return ot.solve_yag_holes(
                iop=self._float("iop"),
                qt=self._float("qt"),
                mode=mode,
                **kwargs,
            )

        if mode == "constant pressure":
            return ot.solve_cp(iop=self._float("iop"), **kwargs)

        return ot.solve_cf(qt=self._float("qt"), **kwargs)

    def _update_summary(self, solution: dict) -> None:
        lines = [
            f"Mode: {self.vars['mode'].get()}",
            f"Surgery: {self.vars['surgery'].get()}",
            "",
            f"IOP: {solution.get('iop', float('nan')):.6g} mmHg",
            f"Flow rate: {solution.get('flowrate', float('nan')):.6g} uL/min",
            f"Resistance: {solution.get('resistance', float('nan')):.6g} mmHg/uL/min",
            f"Facility: {solution.get('facility', float('nan')):.6g} uL/min/mmHg",
        ]
        self.summary.configure(state="normal")
        self.summary.delete("1.0", tk.END)
        self.summary.insert("1.0", "\n".join(lines))
        self.summary.configure(state="disabled")

    def _update_plot(self, solution: dict, kwargs: dict) -> None:
        import numpy as np

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        plot_type = self.vars["plot_type"].get()

        if plot_type == "Collector channel flow":
            y = solution["jcc"]
            x = np.arange(len(y))
            ax.plot(x, y, marker="^")
            ax.set_xlabel("Collector channel index")
            ax.set_ylabel("Jcc (uL/min)")
            ax.set_title("Collector Channel Flow")
        else:
            pressure = solution["pressure"]
            x = np.arange(len(pressure), dtype=float) * md.dx / 1000.0
            if plot_type == "Canal height":
                heights = [md.get_h(p, solution["iop"], i) for i, p in enumerate(pressure)]
                for loc, stent in kwargs.get("stents", []):
                    heights[loc : loc + len(stent) + 1] = [stent.h] * (len(stent) + 1)
                ax.plot(x, heights)
                ax.set_ylabel("hsc (um)")
                ax.set_title("Schlemm's Canal Height")
            else:
                ax.plot(x, pressure)
                ax.set_ylabel("Psc (mmHg)")
                ax.set_title("Schlemm's Canal Pressure")
            ax.set_xlabel("Circumferential position (mm)")

        ax.grid(True, alpha=0.25)
        self.figure.tight_layout()
        self.canvas.draw()

    def _float(self, key: str) -> float:
        return float(self.vars[key].get())


def main() -> None:
    app = LocalAqueousOutflowApp()
    app.mainloop()


if __name__ == "__main__":
    main()
