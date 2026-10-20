"""Figures for the wind feasibility report (static PNG, light surface).

Usage:  python wind/tools/make_figures.py
Reads   wind/data/sjc_1min_diurnal.csv, wind/data/rotorpy_demo_results.csv
Writes  wind/figures/sjc_diurnal.png, wind/figures/rotorpy_demo.png
"""
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]
DATA, FIG = REPO / "wind" / "data", REPO / "wind" / "figures"
SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
S1, S2 = "#2a78d6", "#eb6834"  # categorical slots 1-2 (validated pair in the reference palette)

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 1, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 10, "axes.titlesize": 11, "axes.titlecolor": INK,
    "lines.linewidth": 2, "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
})


def diurnal():
    df = pd.read_csv(DATA / "sjc_1min_diurnal.csv")
    df = df[df.hour.between(6, 19)]
    periods = list(dict.fromkeys(df.period))
    fig, axes = plt.subplots(1, len(periods), figsize=(10, 3.8), sharey=True)
    for ax, p in zip(axes, periods):
        d = df[df.period == p]
        ax.axvspan(8, 16, color=GRID, alpha=0.45, lw=0)
        ax.text(12, 0.3, "flight hours 08–16", ha="center", color=MUTED, fontsize=8.5)
        ax.plot(d.hour, d.mean_p50, color=S1, label="median 2-min mean wind")
        ax.plot(d.hour, d.gust_p90, color=S2, label="90th-percentile 5-s gust")
        for col, c in [("mean_p50", S1), ("gust_p90", S2)]:
            last = d.iloc[-1]
            ax.plot(last.hour, last[col], "o", ms=8, color=c, mec=SURFACE, mew=2)
            ax.annotate(f"{last[col]:.1f}", (last.hour, last[col]), xytext=(7, 0), textcoords="offset points",
                        va="center", color=INK2, fontsize=9)
        ax.set_title(p.replace(" to ", " – "), loc="left")
        ax.set_xlabel("local hour (America/Los_Angeles)")
        ax.set_xticks(range(6, 20, 2))
        ax.set_xlim(5.5, 20)
    axes[0].set_ylim(0, df.gust_p90.max() * 1.1)
    axes[0].set_ylabel("wind at SJC, 10 m (m/s)")
    fig.suptitle("San Jose (SJC) wind by hour of day — ASOS 1-minute data", x=0.01, ha="left", color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.legend(*axes[0].get_legend_handles_labels(), loc="upper right", ncol=2, frameon=False,
               labelcolor=INK2, bbox_to_anchor=(0.99, 0.995))
    fig.savefig(FIG / "sjc_diurnal.png", dpi=160)


def demo():
    df = pd.read_csv(DATA / "rotorpy_demo_results.csv").sort_values("wind_mean_ms")
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    for ax, col, label in [(axes[0], "rmse_m", "position-tracking RMSE (m)"),
                           (axes[1], "max_tilt_deg", "maximum tilt (deg)")]:
        ax.plot(df.wind_mean_ms, df[col], color=S1, marker="o", ms=8, mec=SURFACE, mew=2)
        r = df.iloc[-1]
        ax.annotate(f"{r[col]:.2f}" if col == "rmse_m" else f"{r[col]:.0f}°", (r.wind_mean_ms, r[col]),
                    xytext=(-8, 6), textcoords="offset points", ha="right", color=INK2, fontsize=9)
        ax.set_xlabel("mean replayed wind at 5 m (m/s)")
        ax.set_title(label, loc="left")
        ax.set_ylim(0, None)
    fig.suptitle("RotorPy X500-like patrol loop under replayed SJC wind (SE(3) controller, not PX4)",
                 x=0.01, ha="left", color=INK)
    fig.tight_layout()
    fig.savefig(FIG / "rotorpy_demo.png", dpi=160)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    diurnal()
    demo()
    print(f"wrote {FIG}")
