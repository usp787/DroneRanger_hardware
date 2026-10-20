"""Flight-relevant wind statistics from the CSVs written by fetch_wind.py.

Usage:
  python wind/tools/wind_stats.py                     # all periods found in the data folder
  python wind/tools/wind_stats.py --data <folder> --out wind/data

Writes  <out>/sj_wind_summary.md  (tables quoted in the feasibility report) and
        <out>/sjc_1min_diurnal.csv (per local hour: median / p90 mean wind and gust, per period).
Flight hours are 08:00-16:00 local (America/Los_Angeles), which fits daylight in every month of the project.
"""
import argparse
import pathlib
import re
import sys

import numpy as np
import pandas as pd

REPO = pathlib.Path(__file__).resolve().parents[2]
TZ = "America/Los_Angeles"
FLIGHT_HOURS = range(8, 16)
MORNING, AFTERNOON = range(8, 11), range(13, 16)
MEAN_LIMITS = [3, 5, 8]      # m/s, 2-minute mean wind
GUST_LIMITS = [5, 8, 10]     # m/s, peak 5-second gust in the minute


def load(path):
    df = pd.read_csv(path, parse_dates=["time_utc"])
    df["local"] = df["time_utc"].dt.tz_convert(TZ)
    df["hour"] = df["local"].dt.hour
    return df


def pct(x, q):
    return float(np.nanpercentile(x, q)) if len(x) else float("nan")


def uv(speed, direction):
    """Wind vector (east, north) the air moves TOWARD; direction is the meteorological FROM angle."""
    th = np.deg2rad(direction)
    return -speed * np.sin(th), -speed * np.cos(th)


def sector(d):
    names = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return names[int(((d + 22.5) % 360) // 45)]


def one_min_section(df, label, start, end):
    expected = int((pd.Timestamp(end) - pd.Timestamp(start)).total_seconds() // 60) + 1440
    fl = df[df.hour.isin(FLIGHT_HOURS)].dropna(subset=["speed_ms"])
    out = [f"### SJC 1-minute ASOS, {label}", "",
           f"Rows {len(df):,} of ~{expected:,} possible minutes ({len(df) / expected:.0%} coverage); "
           f"{len(fl):,} minutes inside flight hours 08-16 local.", ""]

    out += ["| Window | median mean (m/s) | p90 mean | median 5-s gust | p90 gust | p99 gust | max gust |",
            "|---|---|---|---|---|---|---|"]
    for name, hrs in [("08-16 all", FLIGHT_HOURS), ("08-11 morning", MORNING), ("13-16 afternoon", AFTERNOON)]:
        w = df[df.hour.isin(hrs)]
        out.append(f"| {name} | {pct(w.speed_ms, 50):.1f} | {pct(w.speed_ms, 90):.1f} | "
                   f"{pct(w.gust_ms, 50):.1f} | {pct(w.gust_ms, 90):.1f} | {pct(w.gust_ms, 99):.1f} | "
                   f"{np.nanmax(w.gust_ms):.1f} |")
    out.append("")

    out += ["Share of flight-hour minutes at or under a limit (mean = 2-min mean, gust = peak 5-s gust of the "
            "minute):", "",
            "| Window | " + " | ".join(f"mean ≤ {m}" for m in MEAN_LIMITS) + " | "
            + " | ".join(f"gust ≤ {g}" for g in GUST_LIMITS) + " |",
            "|---|" + "---|" * (len(MEAN_LIMITS) + len(GUST_LIMITS))]
    for name, hrs in [("08-16 all", FLIGHT_HOURS), ("08-11 morning", MORNING), ("13-16 afternoon", AFTERNOON)]:
        w = df[df.hour.isin(hrs)].dropna(subset=["speed_ms"])
        g = w.gust_ms.fillna(w.speed_ms)
        out.append(f"| {name} | " + " | ".join(f"{(w.speed_ms <= m).mean():.0%}" for m in MEAN_LIMITS) + " | "
                   + " | ".join(f"{(g <= x).mean():.0%}" for x in GUST_LIMITS) + " |")
    out.append("")

    # gust factor and a turbulence-intensity proxy
    g = fl[(fl.speed_ms >= 2) & fl.gust_ms.notna()]
    gf = g.gust_ms / g.speed_ms
    roll = (fl.set_index("time_utc").speed_ms.resample("10min").agg(["mean", "std", "count"]))
    roll = roll[(roll["count"] >= 8) & (roll["mean"] >= 2)]
    ti = roll["std"] / roll["mean"]
    out += [f"- Gust factor (5-s gust ÷ 2-min mean, mean ≥ 2 m/s, n = {len(gf):,}): median {gf.median():.2f}, "
            f"p90 {gf.quantile(.9):.2f}.",
            f"- Turbulence proxy (std ÷ mean of the 1-min values in 10-min blocks, n = {len(ti):,}): median "
            f"{ti.median():.2f}, p90 {ti.quantile(.9):.2f}. This understates true turbulence intensity because "
            f"each value is already a 2-minute average.",
            ]
    # prevailing direction in the afternoon
    aft = df[df.hour.isin(AFTERNOON) & (df.speed_ms >= 2)].dropna(subset=["dir_deg"])
    sect = aft.dir_deg.map(sector).value_counts(normalize=True)
    out.append("- Afternoon (13-16) direction when mean ≥ 2 m/s: " +
               ", ".join(f"{k} {v:.0%}" for k, v in sect.head(3).items()) + ".")
    calm = (fl.speed_ms < 0.5).mean()
    out += [f"- Flight-hour minutes reporting 0 kt (calm): {calm:.1%}. The 1-minute archive reports speeds "
            f"down to 1 kt, unlike METAR, which rounds light winds to calm.", ""]

    diurnal = (df.groupby("hour").agg(mean_p50=("speed_ms", "median"),
                                      mean_p90=("speed_ms", lambda x: pct(x, 90)),
                                      gust_p50=("gust_ms", "median"),
                                      gust_p90=("gust_ms", lambda x: pct(x, 90)),
                                      n=("speed_ms", "count")).reset_index())
    diurnal.insert(0, "period", label)
    return out, diurnal


def compare(a, b, la, lb, tol="10min"):
    """Match two hourly-ish series by nearest time and compare speeds and vectors (flight hours only)."""
    a = a.dropna(subset=["speed_ms"]).sort_values("time_utc")
    b = b.dropna(subset=["speed_ms"]).sort_values("time_utc")
    m = pd.merge_asof(a, b, on="time_utc", tolerance=pd.Timedelta(tol), direction="nearest",
                      suffixes=("_a", "_b")).dropna(subset=["speed_ms_b"])
    m = m[m.hour_a.isin(FLIGHT_HOURS)]
    r = np.corrcoef(m.speed_ms_a, m.speed_ms_b)[0, 1]
    bias = (m.speed_ms_b - m.speed_ms_a).mean()
    rmse = np.sqrt(((m.speed_ms_b - m.speed_ms_a) ** 2).mean())
    ratio = m.speed_ms_b.mean() / m.speed_ms_a.mean()
    both = m[(m.speed_ms_a >= 2) & (m.speed_ms_b >= 2)].dropna(subset=["dir_deg_a", "dir_deg_b"])
    dd = ((both.dir_deg_b - both.dir_deg_a + 180) % 360 - 180).abs()
    return (f"| {la} vs {lb} | {len(m):,} | {r:.2f} | {ratio:.2f} | {bias:+.2f} | {rmse:.2f} | "
            f"{dd.median():.0f}° |")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=pathlib.Path, default=REPO / "reference" / "08_wind_simulation" / "data")
    ap.add_argument("--out", type=pathlib.Path, default=REPO / "wind" / "data")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)

    lines = ["# San Jose wind statistics for DroneRanger flight planning", "",
             f"Generated by `wind/tools/wind_stats.py` from the CSVs in `{a.data.relative_to(REPO).as_posix()}/`. "
             "All speeds are at the station anemometer (10 m, open airport terrain) unless stated otherwise; "
             "local time is America/Los_Angeles; flight hours are 08-16 local.", ""]
    diurnals = []
    for f in sorted(a.data.glob("iem_1min_SJC_*.csv")):
        s, e = re.findall(r"(\d{8})_(\d{8})", f.name)[0]
        label = f"{s[:4]}-{s[4:6]}-{s[6:]} to {e[:4]}-{e[4:6]}-{e[6:]}"
        sec, di = one_min_section(load(f), label, s, e)
        lines += sec
        diurnals.append(di)

    for tag in sorted({re.findall(r"(\d{8}_\d{8})", f.name)[0] for f in a.data.glob("iem_metar_SJC_*.csv")}):
        sjc = load(a.data / f"iem_metar_SJC_{tag}.csv")
        lines += [f"### Station and model agreement, {tag[:8]} to {tag[9:]} (flight hours)", "",
                  "Matched by nearest report within 10 min. Ratio = mean speed B ÷ mean speed A; bias = B − A.", "",
                  "| A vs B | n | r (speed) | ratio | bias (m/s) | RMSE (m/s) | median direction diff (both ≥ 2 m/s) |",
                  "|---|---|---|---|---|---|---|"]
        for st in ["RHV", "NUQ", "PAO"]:
            p = a.data / f"iem_metar_{st}_{tag}.csv"
            if p.exists():
                lines.append(compare(sjc, load(p), "SJC", st))
        p = a.data / f"openmeteo_campus_{tag}.csv"
        if p.exists():
            lines.append(compare(sjc, load(p), "SJC", "Open-Meteo campus"))
        lines.append("")

    (a.out / "sj_wind_summary.md").write_text("\n".join(lines), encoding="utf-8")
    pd.concat(diurnals).to_csv(a.out / "sjc_1min_diurnal.csv", index=False, float_format="%.2f")
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles may default to a legacy code page
    print("\n".join(lines))


if __name__ == "__main__":
    main()
