"""
California Housing Price Estimator
Dark art-deco UI built with tkinter (zero extra dependencies).

Run:
    python housing_estimator.py

To use your REAL trained model instead of the simulation, set:
    USE_REAL_MODEL = True
and ensure model.pkl + pipeline.pkl are in the same directory.
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
import math, threading, time

# ── Toggle real model ────────────────────────────────────────────────────────
USE_REAL_MODEL = False

if USE_REAL_MODEL:
    import joblib, pandas as pd, numpy as np
    _model    = joblib.load("model.pkl")
    _pipeline = joblib.load("pipeline.pkl")

# ── Palette ──────────────────────────────────────────────────────────────────
BG       = "#0A0A08"
SURFACE  = "#111110"
SURFACE2 = "#1A1A17"
GOLD     = "#C9A84C"
GOLD_LT  = "#E8C97A"
GOLD_DIM = "#7A6330"
CREAM    = "#F0E8D5"
MUTED    = "#5A5A50"
ACCENT   = "#D4622A"
GREEN    = "#4A9E6A"
BORDER   = "#2A2A24"

# ── Prediction logic ─────────────────────────────────────────────────────────
def simulate_rf(lat, lng, age, rooms, bedrooms, population, households,
                income, ocean):
    if USE_REAL_MODEL:
        row = pd.DataFrame([{
            "longitude": lng, "latitude": lat,
            "housing_median_age": age, "total_rooms": rooms,
            "total_bedrooms": bedrooms, "population": population,
            "households": households, "median_income": income,
            "ocean_proximity": ocean,
        }])
        transformed = _pipeline.transform(row)
        price = float(_model.predict(transformed)[0])
        confidence = 82
    else:
        price = 45000 + income * 38000
        price -= min(abs(lng + 118.5) * 12000, 40000)
        if 37.3 < lat < 38.2: price += 35000
        if 33.5 < lat < 34.5: price += 18000
        if lat > 38.5:         price -= 15000
        ocean_bonus = {"ISLAND":120000,"<1H OCEAN":65000,
                       "NEAR OCEAN":55000,"NEAR BAY":48000,"INLAND":0}
        price += ocean_bonus.get(ocean, 0)
        if age > 30: price += age * 200
        else:        price -= (30 - age) * 150
        rph = rooms / max(households, 1)
        if rph > 5: price += (rph - 5) * 4000
        if (bedrooms / max(rooms, 1)) < 0.25: price += 20000
        density = population / max(households, 1)
        if density > 4: price -= (density - 4) * 1500
        price = max(50000, min(500000, price))
        inc_conf = max(0, 1 - abs(income - 4) / 10)
        loc_conf = 1.0 if (33 < lat < 41 and -124 < lng < -114) else 0.4
        confidence = int(65 + inc_conf * 20 + loc_conf * 15)

    price = round(price / 100) * 100
    rph   = rooms / max(households, 1)
    ppr   = f"${round(price / max(rooms,1)):,}"
    ratio = f"{price / max(income*10000,1):.1f}x"
    tiers = {"ISLAND":"★★★★★","<1H OCEAN":"★★★★☆","NEAR OCEAN":"★★★★☆",
             "NEAR BAY":"★★★☆☆","INLAND":"★★☆☆☆"}
    dens  = f"{population/max(households,1):.1f} ppl/hh"
    band  = f"${round(price*.88/1000)}k – ${round(price*1.12/1000)}k"
    return {
        "price": price, "confidence": confidence,
        "price_per_room": ppr, "income_ratio": ratio,
        "ocean_tier": tiers.get(ocean,"—"), "density": dens,
        "rooms_per_hh": f"{rph:.1f}", "band": band,
    }

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt(n): return f"{n:,}"

# ── App ───────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("California Housing Price Estimator")
        self.configure(bg=BG)
        self.geometry("820x900")
        self.minsize(700, 700)
        self.resizable(True, True)

        # Fonts
        self.f_display = tkfont.Font(family="Georgia", size=28, weight="bold")
        self.f_title   = tkfont.Font(family="Georgia", size=16, weight="bold")
        self.f_mono    = tkfont.Font(family="Courier", size=9)
        self.f_mono_sm = tkfont.Font(family="Courier", size=8)
        self.f_mono_lg = tkfont.Font(family="Courier", size=11)
        self.f_mono_xl = tkfont.Font(family="Courier", size=13)
        self.f_btn     = tkfont.Font(family="Courier", size=10, weight="bold")

        self._build_scrollable()
        self._build_ui()

    # ── Scrollable canvas wrapper ─────────────────────────────────────────────
    def _build_scrollable(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(outer, bg=BG, bd=0, highlightthickness=0)
        vsb = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview,
                           bg=SURFACE2, troughcolor=BG, activebackground=GOLD)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=BG)
        self._win_id = self.canvas.create_window(
            (0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>",   self._on_mousewheel)
        self.canvas.bind_all("<Button-5>",   self._on_mousewheel)

    def _on_frame_configure(self, _):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self.canvas.itemconfig(self._win_id, width=e.width)

    def _on_mousewheel(self, e):
        if e.num == 4:    self.canvas.yview_scroll(-1, "units")
        elif e.num == 5:  self.canvas.yview_scroll( 1, "units")
        else:             self.canvas.yview_scroll(int(-e.delta/40), "units")

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        pad = tk.Frame(self.inner, bg=BG)
        pad.pack(fill="both", expand=True, padx=60, pady=48)

        self._header(pad)
        self._card(pad)
        self._result_area(pad)

    # ── Header ────────────────────────────────────────────────────────────────
    def _header(self, parent):
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="x", pady=(0, 40))

        tk.Label(f, text="RANDOM FOREST  ·  SCIKIT-LEARN  ·  CA HOUSING",
                 bg=BG, fg=GOLD_DIM, font=self.f_mono_sm,
                 letterSpacing=4).pack()

        tk.Label(f, text="California Home\nValue Estimator",
                 bg=BG, fg=CREAM, font=self.f_display,
                 justify="center").pack(pady=(12, 0))

        # Gold accent on "Value Estimator" — draw a canvas label
        tk.Label(f,
                 text="Enter property details to generate a predicted median value",
                 bg=BG, fg=MUTED, font=self.f_mono).pack(pady=(6, 16))

        # Divider
        c = tk.Canvas(f, bg=BG, height=2, bd=0, highlightthickness=0, width=80)
        c.pack()
        c.create_line(0, 1, 80, 1, fill=GOLD, width=1)

    # ── Card ──────────────────────────────────────────────────────────────────
    def _card(self, parent):
        card = tk.Frame(parent, bg=SURFACE,
                        highlightbackground=GOLD_DIM,
                        highlightthickness=1)
        card.pack(fill="x", pady=(0, 0))

        inner = tk.Frame(card, bg=SURFACE)
        inner.pack(fill="x", padx=40, pady=36)

        # Location
        self._section_label(inner, "Location")
        row = tk.Frame(inner, bg=SURFACE)
        row.pack(fill="x", pady=(12, 0))
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)

        self.lat_var = tk.StringVar(value="37.88")
        self.lng_var = tk.StringVar(value="-122.23")
        self._text_field(row, "LATITUDE", self.lat_var,
                         "Degrees north, CA ~32–42", 0)
        self._text_field(row, "LONGITUDE", self.lng_var,
                         "Degrees west, CA ~-114 to -124", 1)

        tk.Label(inner,
                 text="▸  California spans approx. lat 32–42 N, lon -114 to -124 W",
                 bg=SURFACE, fg=MUTED, font=self.f_mono_sm).pack(
                     anchor="w", pady=(6, 0))

        self._spacer(inner, 28)

        # Sliders
        self._section_label(inner, "Housing Characteristics")
        self._spacer(inner, 14)

        self.age_var  = tk.DoubleVar(value=28)
        self.rms_var  = tk.DoubleVar(value=2635)
        self.bed_var  = tk.DoubleVar(value=537)
        self.pop_var  = tk.DoubleVar(value=1425)
        self.hh_var   = tk.DoubleVar(value=499)
        self.inc_var  = tk.DoubleVar(value=3.87)

        self._slider(inner, "HOUSING MEDIAN AGE", self.age_var, 1, 52,
                     lambda v: f"{int(float(v))} yrs")
        self._slider(inner, "TOTAL ROOMS", self.rms_var, 100, 10000,
                     lambda v: f"{int(float(v)):,}  (block total)", res=50)
        self._slider(inner, "TOTAL BEDROOMS", self.bed_var, 50, 2500,
                     lambda v: f"{int(float(v)):,}  (block total)", res=10)
        self._slider(inner, "POPULATION", self.pop_var, 50, 10000,
                     lambda v: f"{int(float(v)):,}  people", res=50)
        self._slider(inner, "HOUSEHOLDS", self.hh_var, 10, 2000,
                     lambda v: f"{int(float(v)):,}  units", res=10)
        self._slider(inner, "MEDIAN INCOME", self.inc_var, 0.5, 15,
                     lambda v: f"${float(v)*10:.0f}k  (household median)",
                     res=0.1)

        self._spacer(inner, 28)

        # Ocean proximity
        self._section_label(inner, "Ocean Proximity")
        self._spacer(inner, 14)
        self.ocean_var = tk.StringVar(value="INLAND")
        ocean_opts = [
            ("Near Bay",    "NEAR BAY"),
            ("<1H Ocean",   "<1H OCEAN"),
            ("Inland",      "INLAND"),
            ("Near Ocean",  "NEAR OCEAN"),
            ("Island",      "ISLAND"),
        ]
        oframe = tk.Frame(inner, bg=SURFACE)
        oframe.pack(fill="x")
        for label, val in ocean_opts:
            rb = tk.Radiobutton(
                oframe, text=label, variable=self.ocean_var, value=val,
                bg=SURFACE, fg=CREAM, selectcolor=SURFACE2,
                activebackground=SURFACE, activeforeground=GOLD_LT,
                font=self.f_mono_xl,
                indicatoron=0,
                relief="flat", bd=0,
                padx=16, pady=8,
                highlightthickness=1,
                highlightbackground=GOLD_DIM,
                cursor="hand2",
            )
            rb.pack(side="left", padx=(0, 8), pady=4)
            rb.bind("<Enter>", lambda e, w=rb: w.configure(fg=GOLD_LT))
            rb.bind("<Leave>", lambda e, w=rb: w.configure(fg=CREAM))

        self._spacer(inner, 36)

        # Predict button
        self.btn = tk.Button(
            inner, text="▸   ESTIMATE PROPERTY VALUE",
            bg=GOLD, fg=BG, font=self.f_btn,
            relief="flat", bd=0, padx=20, pady=14,
            cursor="hand2", activebackground=GOLD_LT, activeforeground=BG,
            command=self._on_predict,
        )
        self.btn.pack(fill="x")

    # ── Result area ───────────────────────────────────────────────────────────
    def _result_area(self, parent):
        self.result_frame = tk.Frame(parent, bg=BG)
        self.result_frame.pack(fill="x", pady=(24, 0))

    def _show_result(self, data):
        # Clear
        for w in self.result_frame.winfo_children():
            w.destroy()

        panel = tk.Frame(self.result_frame, bg=SURFACE,
                         highlightbackground=GOLD_DIM, highlightthickness=1)
        panel.pack(fill="x")
        inner = tk.Frame(panel, bg=SURFACE)
        inner.pack(fill="x", padx=40, pady=32)

        # Top row
        top = tk.Frame(inner, bg=SURFACE)
        top.pack(fill="x")

        left = tk.Frame(top, bg=SURFACE)
        left.pack(side="left", fill="x", expand=True)

        tk.Label(left, text="PREDICTED MEDIAN VALUE",
                 bg=SURFACE, fg=MUTED, font=self.f_mono_sm).pack(anchor="w")
        tk.Label(left, text=f"${data['price']:,}",
                 bg=SURFACE, fg=GOLD_LT,
                 font=tkfont.Font(family="Georgia", size=34, weight="bold")
                 ).pack(anchor="w", pady=(4, 0))

        right = tk.Frame(top, bg=SURFACE)
        right.pack(side="right", anchor="ne")
        tk.Label(right, text="MODEL CONFIDENCE",
                 bg=SURFACE, fg=MUTED, font=self.f_mono_sm).pack(anchor="e")
        tk.Label(right, text=f"{data['confidence']}%",
                 bg=SURFACE, fg=GOLD_LT, font=self.f_mono_lg).pack(
                     anchor="e", pady=(4, 6))

        # Confidence bar (canvas)
        bar_canvas = tk.Canvas(right, bg=SURFACE2, bd=0,
                               highlightthickness=0, height=4, width=140)
        bar_canvas.pack(anchor="e")
        fill_w = int(140 * data["confidence"] / 100)
        bar_canvas.create_rectangle(0, 0, fill_w, 4, fill=GOLD_LT,
                                    outline="")

        # Divider
        self._spacer(inner, 20)
        c = tk.Canvas(inner, bg=SURFACE, height=1, bd=0,
                      highlightthickness=0)
        c.pack(fill="x")
        c.create_line(0, 0, 2000, 0, fill=GOLD_DIM)
        self._spacer(inner, 20)

        # Stats grid
        stats = [
            ("PRICE / ROOM",     data["price_per_room"]),
            ("INCOME RATIO",     data["income_ratio"]),
            ("OCEAN TIER",       data["ocean_tier"]),
            ("DENSITY",          data["density"]),
            ("ROOMS / HH",       data["rooms_per_hh"]),
            ("PREDICTION BAND",  data["band"]),
        ]
        grid = tk.Frame(inner, bg=SURFACE)
        grid.pack(fill="x")
        for i, (k, v) in enumerate(stats):
            cell = tk.Frame(grid, bg=SURFACE)
            cell.grid(row=i//3, column=i%3, sticky="w",
                      padx=(0, 32), pady=(0, 16))
            tk.Label(cell, text=k, bg=SURFACE, fg=MUTED,
                     font=self.f_mono_sm).pack(anchor="w")
            tk.Label(cell, text=v, bg=SURFACE, fg=CREAM,
                     font=self.f_mono_xl).pack(anchor="w", pady=(3, 0))

        # Animate panel appearance
        self._fade_in(panel)

    def _fade_in(self, widget):
        # Simulate fade via delayed pack + scroll-to-bottom
        self.after(50, lambda: self.canvas.yview_moveto(1.0))

    # ── Predict handler ───────────────────────────────────────────────────────
    def _on_predict(self):
        self.btn.configure(text="  Analysing…", state="disabled",
                           bg=GOLD_DIM, cursor="watch")
        self.update()

        def work():
            try:
                lat = float(self.lat_var.get())
                lng = float(self.lng_var.get())
            except ValueError:
                self.after(0, self._reset_btn)
                return

            time.sleep(0.85)
            data = simulate_rf(
                lat=lat, lng=lng,
                age=self.age_var.get(),
                rooms=self.rms_var.get(),
                bedrooms=self.bed_var.get(),
                population=self.pop_var.get(),
                households=self.hh_var.get(),
                income=self.inc_var.get(),
                ocean=self.ocean_var.get(),
            )
            self.after(0, lambda: self._show_result(data))
            self.after(0, self._reset_btn)

        threading.Thread(target=work, daemon=True).start()

    def _reset_btn(self):
        self.btn.configure(
            text="▸   ESTIMATE PROPERTY VALUE",
            state="normal", bg=GOLD, cursor="hand2")

    # ── Reusable components ───────────────────────────────────────────────────
    def _section_label(self, parent, text):
        row = tk.Frame(parent, bg=SURFACE)
        row.pack(fill="x", pady=(0, 0))
        tk.Label(row, text=text.upper(),
                 bg=SURFACE, fg=GOLD_DIM, font=self.f_mono_sm
                 ).pack(side="left")
        c = tk.Canvas(row, bg=SURFACE, height=1, bd=0,
                      highlightthickness=0)
        c.pack(side="left", fill="x", expand=True, padx=(10, 0))
        c.bind("<Configure>",
               lambda e, cv=c: cv.create_line(0, 0, e.width, 0,
                                               fill=GOLD_DIM))

    def _text_field(self, parent, label, var, tip, col):
        f = tk.Frame(parent, bg=SURFACE)
        f.grid(row=0, column=col, sticky="ew",
               padx=(0 if col == 0 else 16, 0))

        tk.Label(f, text=label, bg=SURFACE, fg=MUTED,
                 font=self.f_mono_sm).pack(anchor="w")
        self._spacer(f, 6)

        entry = tk.Entry(f, textvariable=var,
                         bg=SURFACE2, fg=CREAM,
                         insertbackground=GOLD,
                         relief="flat", bd=0,
                         font=self.f_mono_xl,
                         highlightthickness=1,
                         highlightbackground=GOLD_DIM,
                         highlightcolor=GOLD)
        entry.pack(fill="x", ipady=8, ipadx=8)

        tk.Label(f, text=tip, bg=SURFACE, fg=GOLD_DIM,
                 font=self.f_mono_sm).pack(anchor="w", pady=(4, 0))

    def _slider(self, parent, label, var, from_, to, fmt_fn,
                res=1):
        f = tk.Frame(parent, bg=SURFACE)
        f.pack(fill="x", pady=(0, 16))

        header = tk.Frame(f, bg=SURFACE)
        header.pack(fill="x")
        tk.Label(header, text=label, bg=SURFACE, fg=MUTED,
                 font=self.f_mono_sm).pack(side="left")
        val_lbl = tk.Label(header, text=fmt_fn(var.get()),
                           bg=SURFACE, fg=GOLD_LT, font=self.f_mono)
        val_lbl.pack(side="right")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Gold.Horizontal.TScale",
                        background=SURFACE,
                        troughcolor=SURFACE2,
                        sliderlength=14,
                        sliderrelief="flat")

        s = ttk.Scale(f, from_=from_, to=to, variable=var,
                      orient="horizontal",
                      style="Gold.Horizontal.TScale",
                      command=lambda v, lbl=val_lbl,
                      fn=fmt_fn: lbl.configure(text=fn(v)))
        s.pack(fill="x", pady=(4, 0))

    def _spacer(self, parent, h):
        tk.Frame(parent, bg=SURFACE if parent.cget("bg") == SURFACE else BG,
                 height=h).pack()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()