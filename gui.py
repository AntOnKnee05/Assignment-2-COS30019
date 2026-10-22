"""Graphical viewer that animates the search methods on a problem file.

Usage:
    python gui.py [filename] [method]

Draws the graph (nodes at their coordinates, directed weighted edges), marks
the origin and destinations, then replays the search one expansion at a time
and finally highlights the path found. Standard library only (tkinter).

The viewer works with any method in METHODS without changing the algorithms:
route_finding.trace records each call to expand(), so every logged step is
one real node expansion in the order the algorithm made it.
"""

import glob
import math
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from route_finding import ParseError, parse_problem
from route_finding.algorithms import METHODS
from route_finding.trace import trace_search

CASES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests", "cases")

NODE_RADIUS = 15
MARGIN = 50

# Colours: fill shows search progress, outline shows the node's role.
COLOURS = {
    "background": "#ffffff",
    "grid": "#e4e4e4",
    "axis": "#888888",
    "edge": "#9aa5b1",
    "edge_text": "#52606d",
    "path": "#d64545",
    "node": "#ffffff",
    "generated": "#ffe08a",
    "expanded": "#9fc5f8",
    "current": "#f0883e",
    "origin": "#2f9e44",
    "destination": "#c92a2a",
    "text": "#1f2933",
}




class SearchViewer:
    def __init__(self, root, filename=None, method="BFS"):
        self.root = root
        self.root.title("Route Finding - Search Visualiser")
        self.root.geometry("1150x720")
        self.root.minsize(800, 500)

        self.problem = None
        self.edges = []          # (src, dst, cost)
        self.result = None
        self.steps = []
        self.step_index = 0      # number of expansions currently shown
        self.playing = False
        self.after_id = None

        self._build_widgets()

        cases = sorted(glob.glob(os.path.join(CASES_DIR, "*.txt")))
        self.file_box["values"] = [os.path.basename(p) for p in cases]
        self.method_var.set(method.upper() if method.upper() in METHODS else "BFS")
        if filename:
            self.load_file(filename)
        elif cases:
            self.load_file(cases[0])

    # ------------------------------------------------------------------ layout
    def _build_widgets(self):
        self.canvas = tk.Canvas(self.root, bg=COLOURS["background"], highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda _e: self.redraw())

        panel = ttk.Frame(self.root, padding=10, width=330)
        panel.pack(side=tk.RIGHT, fill=tk.Y)
        panel.pack_propagate(False)

        ttk.Label(panel, text="Problem file").pack(anchor=tk.W)
        file_row = ttk.Frame(panel)
        file_row.pack(fill=tk.X, pady=(0, 8))
        self.file_var = tk.StringVar()
        self.file_box = ttk.Combobox(file_row, textvariable=self.file_var, state="readonly")
        self.file_box.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.file_box.bind("<<ComboboxSelected>>",
                           lambda _e: self.load_file(os.path.join(CASES_DIR, self.file_var.get())))
        ttk.Button(file_row, text="Browse...", command=self.browse).pack(side=tk.LEFT, padx=(4, 0))

        ttk.Label(panel, text="Search method").pack(anchor=tk.W)
        self.method_var = tk.StringVar()
        method_box = ttk.Combobox(panel, textvariable=self.method_var,
                                  values=list(METHODS), state="readonly")
        method_box.pack(fill=tk.X, pady=(0, 8))
        method_box.bind("<<ComboboxSelected>>", lambda _e: self.run_search())

        buttons = ttk.Frame(panel)
        buttons.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(buttons, text="Run", command=self.run_search).pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.play_button = ttk.Button(buttons, text="Play", command=self.toggle_play)
        self.play_button.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(buttons, text="Step", command=self.step_forward).pack(side=tk.LEFT, expand=True, fill=tk.X)

        buttons2 = ttk.Frame(panel)
        buttons2.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(buttons2, text="Back", command=self.step_back).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(buttons2, text="Reset", command=self.reset).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(buttons2, text="Show result", command=self.skip_to_end).pack(side=tk.LEFT, expand=True, fill=tk.X)

        ttk.Label(panel, text="Speed (delay between steps)").pack(anchor=tk.W)
        self.delay_var = tk.IntVar(value=700)
        ttk.Scale(panel, from_=1500, to=100, variable=self.delay_var,
                  orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 8))

        self.status_var = tk.StringVar()
        ttk.Label(panel, textvariable=self.status_var, wraplength=300,
                  justify=tk.LEFT, font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 6))

        ttk.Label(panel, text="Expansion order").pack(anchor=tk.W)
        log_frame = ttk.Frame(panel)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log = tk.Listbox(log_frame, font=("Consolas", 9), activestyle="none")
        scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        legend = ttk.Frame(panel)
        legend.pack(fill=tk.X, pady=(8, 0))
        for colour, label, outline in [
            (COLOURS["node"], "Origin", COLOURS["origin"]),
            (COLOURS["node"], "Destination", COLOURS["destination"]),
            (COLOURS["generated"], "Generated (seen)", COLOURS["text"]),
            (COLOURS["expanded"], "Expanded", COLOURS["text"]),
            (COLOURS["current"], "Being expanded", COLOURS["text"]),
        ]:
            row = ttk.Frame(legend)
            row.pack(anchor=tk.W)
            swatch = tk.Canvas(row, width=18, height=18, highlightthickness=0)
            swatch.create_oval(2, 2, 16, 16, fill=colour, outline=outline, width=3)
            swatch.pack(side=tk.LEFT)
            ttk.Label(row, text=label).pack(side=tk.LEFT, padx=4)
        row = ttk.Frame(legend)
        row.pack(anchor=tk.W)
        swatch = tk.Canvas(row, width=18, height=18, highlightthickness=0)
        swatch.create_line(1, 9, 17, 9, fill=COLOURS["path"], width=4)
        swatch.pack(side=tk.LEFT)
        ttk.Label(row, text="Path found").pack(side=tk.LEFT, padx=4)

    # --------------------------------------------------------------- loading
    def browse(self):
        path = filedialog.askopenfilename(initialdir=CASES_DIR, title="Open problem file",
                                          filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.load_file(path)

    def load_file(self, path):
        try:
            problem = parse_problem(path)
        except (OSError, ParseError) as e:
            messagebox.showerror("Cannot load file", f"{path}\n\n{e}")
            return
        self.problem = problem
        self.file_var.set(os.path.basename(path))
        self.edges = [(src, dst, cost)
                      for src in sorted(problem.nodes)
                      for dst, cost in problem.successors(src)]
        self.run_search()

    # ---------------------------------------------------------------- search
    def run_search(self):
        """Run the selected method and rewind the animation to the start."""
        self.stop()
        self.result, self.steps = None, []
        self.log.delete(0, tk.END)
        if self.problem is None:
            return
        method = self.method_var.get()
        try:
            self.result, self.steps = trace_search(self.problem, METHODS[method])
        except NotImplementedError as e:
            self.step_index = 0
            self.status_var.set(f"{method}: {e}")
            self.redraw()
            return
        except Exception as e:  # show crashes in the GUI instead of losing them
            self.step_index = 0
            self.status_var.set(f"{method} crashed: {type(e).__name__}: {e}")
            self.redraw()
            return

        for i, (state, children) in enumerate(self.steps, 1):
            kids = ", ".join(map(str, children)) or "(none)"
            self.log.insert(tk.END, f"{i:>3}. expand {state} -> {kids}")
        self.step_index = 0
        self.update_view()

    def at_end(self):
        return self.step_index >= len(self.steps)

    def step_forward(self):
        if self.result is not None and not self.at_end():
            self.step_index += 1
            self.update_view()
        elif self.playing:
            self.stop()

    def step_back(self):
        self.stop()
        if self.result is not None and self.step_index > 0:
            self.step_index -= 1
            self.update_view()

    def reset(self):
        self.stop()
        if self.result is not None:
            self.step_index = 0
            self.update_view()

    def skip_to_end(self):
        self.stop()
        if self.result is None:
            return
        self.step_index = len(self.steps)
        self.update_view()

    def toggle_play(self):
        if self.playing:
            self.stop()
            return
        if self.result is None:
            return
        if self.at_end():
            self.step_index = 0
        self.playing = True
        self.play_button.configure(text="Pause")
        self._tick()

    def _tick(self):
        if not self.playing:
            return
        self.step_forward()
        if self.at_end():
            self.stop()
        else:
            self.after_id = self.root.after(int(self.delay_var.get()), self._tick)

    def stop(self):
        self.playing = False
        self.play_button.configure(text="Play")
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    # ------------------------------------------------------------- rendering
    def update_view(self):
        self.log.selection_clear(0, tk.END)
        if self.step_index > 0:
            self.log.selection_set(self.step_index - 1)
            self.log.see(self.step_index - 1)
        self.status_var.set(self._status_text())
        self.redraw()

    def _status_text(self):
        method = self.method_var.get()
        total = len(self.steps)
        if not self.at_end():
            if self.step_index == 0:
                return f"{method}: ready - {total} expansions. Press Play or Step."
            state, _ = self.steps[self.step_index - 1]
            return f"{method}: step {self.step_index}/{total} - expanding node {state}"
        goal = self.result.goal
        if goal is None:
            return (f"{method}: no goal is reachable\n"
                    f"Nodes created: {self.result.nodes_created}")
        path = goal.path()
        return (f"{method}: reached goal {goal.state}\n"
                f"Nodes created: {self.result.nodes_created}\n"
                f"Path: {' -> '.join(map(str, path))}\n"
                f"Cost: {goal.path_cost:g}   Moves: {len(path) - 1}")

    def _search_state(self):
        """Return (expanded, generated, current, path_edges) for the current step."""
        expanded, generated = set(), set()
        current = None
        for state, children in self.steps[:self.step_index]:
            expanded.add(state)
            generated.update(children)
            current = state
        path_edges = set()
        if self.result is not None and self.at_end():
            current = None
            if self.result.goal is not None:
                path = self.result.goal.path()
                path_edges = set(zip(path, path[1:]))
                generated.update(path)
        return expanded, generated, current, path_edges

    def _make_transform(self):
        """Fit the node coordinates (and the origin of the axes) to the canvas."""
        xs = [x for x, _ in self.problem.nodes.values()] + [0]
        ys = [y for _, y in self.problem.nodes.values()] + [0]
        min_x, max_x = math.floor(min(xs)), math.ceil(max(xs)) + 1
        min_y, max_y = math.floor(min(ys)), math.ceil(max(ys)) + 1
        width = max(self.canvas.winfo_width(), 200)
        height = max(self.canvas.winfo_height(), 200)
        scale = min((width - 2 * MARGIN) / (max_x - min_x),
                    (height - 2 * MARGIN) / (max_y - min_y))

        def to_canvas(x, y):
            return (MARGIN + (x - min_x) * scale,
                    height - MARGIN - (y - min_y) * scale)  # y axis points up

        return to_canvas, (min_x, max_x, min_y, max_y), scale

    def redraw(self):
        c = self.canvas
        c.delete("all")
        if self.problem is None:
            return
        to_canvas, (min_x, max_x, min_y, max_y), scale = self._make_transform()
        expanded, generated, current, path_edges = self._search_state()

        # Grid and axes.
        tick_every = max(1, math.ceil(30 / scale))  # keep labels at least ~30px apart
        for gx in range(min_x, max_x + 1):
            x0, y0 = to_canvas(gx, min_y)
            x1, y1 = to_canvas(gx, max_y)
            c.create_line(x0, y0, x1, y1, fill=COLOURS["axis"] if gx == 0 else COLOURS["grid"])
            if gx % tick_every == 0:
                c.create_text(x0, y0 + 14, text=str(gx), fill=COLOURS["axis"])
        for gy in range(min_y, max_y + 1):
            x0, y0 = to_canvas(min_x, gy)
            x1, y1 = to_canvas(max_x, gy)
            c.create_line(x0, y0, x1, y1, fill=COLOURS["axis"] if gy == 0 else COLOURS["grid"])
            if gy % tick_every == 0:
                c.create_text(x0 - 14, y0, text=str(gy), fill=COLOURS["axis"])

        # Edges. If both directions exist, offset each arrow sideways so both show.
        edge_set = {(s, d) for s, d, _ in self.edges}
        for src, dst, cost in self.edges:
            (x1, y1), (x2, y2) = to_canvas(*self.problem.nodes[src]), to_canvas(*self.problem.nodes[dst])
            length = math.hypot(x2 - x1, y2 - y1)
            if length == 0:
                continue
            ux, uy = (x2 - x1) / length, (y2 - y1) / length
            offset = 5 if (dst, src) in edge_set else 0
            nx, ny = -uy * offset, ux * offset
            sx, sy = x1 + ux * NODE_RADIUS + nx, y1 + uy * NODE_RADIUS + ny
            ex, ey = x2 - ux * NODE_RADIUS + nx, y2 - uy * NODE_RADIUS + ny
            on_path = (src, dst) in path_edges
            c.create_line(sx, sy, ex, ey, arrow=tk.LAST, arrowshape=(10, 12, 4),
                          width=4 if on_path else 1.5,
                          fill=COLOURS["path"] if on_path else COLOURS["edge"])
            # Cost label, nudged to the arrow's side so opposite edges don't overlap.
            lx = (sx + ex) / 2 + (nx * 2.6 if offset else -uy * 10)
            ly = (sy + ey) / 2 + (ny * 2.6 if offset else ux * 10)
            c.create_text(lx, ly, text=f"{cost:g}", font=("Segoe UI", 8),
                          fill=COLOURS["path"] if on_path else COLOURS["edge_text"])

        # Nodes.
        for node_id, (x, y) in self.problem.nodes.items():
            cx, cy = to_canvas(x, y)
            if node_id == current:
                fill = COLOURS["current"]
            elif node_id in expanded:
                fill = COLOURS["expanded"]
            elif node_id in generated:
                fill = COLOURS["generated"]
            else:
                fill = COLOURS["node"]
            if node_id == self.problem.origin:
                outline, width, tag = COLOURS["origin"], 4, "START"
            elif node_id in self.problem.destinations:
                outline, width, tag = COLOURS["destination"], 4, "GOAL"
            else:
                outline, width, tag = COLOURS["text"], 1.5, None
            r = NODE_RADIUS
            c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=fill, outline=outline, width=width)
            c.create_text(cx, cy, text=str(node_id), font=("Segoe UI", 10, "bold"), fill=COLOURS["text"])
            if tag:
                c.create_text(cx, cy - r - 10, text=tag, font=("Segoe UI", 8, "bold"), fill=outline)


def main(argv):
    filename = argv[1] if len(argv) > 1 else None
    method = argv[2] if len(argv) > 2 else "BFS"
    root = tk.Tk()
    SearchViewer(root, filename, method)
    root.mainloop()


if __name__ == "__main__":
    main(sys.argv)
