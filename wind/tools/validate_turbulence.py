"""Check the Dryden / MIL-F-8785C turbulence model against SJC's measured 5-second gusts.

The comparison is made at the anemometer itself (10 m, open terrain, height factor 1), so it tests only the
turbulence model, not the airport-to-garden extrapolation. For every 15-minute flight-hour window with
>= 13 valid minutes and a mean >= 2 m/s, it replays the measured 1-minute means, adds MIL turbulence and
compares the synthetic per-minute gust factor with the measured one.

Usage:  python wind/tools/validate_turbulence.py [--max-windows 600]
Writes  wind/data/turbulence_validation.csv  and prints a summary (quoted in the feasibility report).
"""
import argparse
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from make_wind_profile import DATA, FT, REPO, TZ, dryden, gust_factor, height_factor  # noqa: E402

FS, WIN = 10.0, 900  # Hz, s


def windows(df):
    df = df.dropna(subset=["speed_ms", "dir_deg"]).set_index("time_utc")
    local = df.index.tz_convert(TZ)
    df = df[(local.hour >= 8) & (local.hour < 16)]
    for t0, w in df.groupby(pd.Grouper(freq=f"{WIN}s")):
        if len(w) >= 13 and w.speed_ms.mean() >= 2.0 and (w.speed_ms >= 2).sum() >= 3:
            yield t0, w


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-windows", type=int, default=600, help="per data file, sampled at random")
    a = ap.parse_args()
    rows = []
    for path in sorted(DATA.glob("iem_1min_SJC_*.csv")):
        df = pd.read_csv(path, parse_dates=["time_utc"])
        ws = list(windows(df))
        rng = np.random.default_rng(1)
        for i in rng.permutation(len(ws))[:a.max_windows]:
            t0, w = ws[i]
            th = np.deg2rad(w.dir_deg.to_numpy())
            tm = (w.index - t0).total_seconds().to_numpy()
            n = int(WIN * FS)
            t = np.arange(n) / FS
            me = np.interp(t, tm, -w.speed_ms * np.sin(th))
            mn = np.interp(t, tm, -w.speed_ms * np.cos(th))
            U = float(np.hypot(me, mn).mean())
            psi = np.arctan2(mn.mean(), me.mean())
            h_ft = 10.0 / FT
            w20 = height_factor(20 * FT, z0_site=0.03) * U  # log law at the airport (z0 = 0.03 m)
            sig_w = 0.1 * w20
            sig_u = sig_w / (0.177 + 0.000823 * h_ft) ** 0.4
            L = np.array([h_ft / (0.177 + 0.000823 * h_ft) ** 1.2] * 2 + [h_ft]) * FT
            tb = dryden(n, FS, max(U, 1.0), np.array([sig_u, sig_u, sig_w]), L, np.random.default_rng(int(i)))
            spd = np.hypot(me + np.cos(psi) * tb[0] - np.sin(psi) * tb[1],
                           mn + np.sin(psi) * tb[0] + np.cos(psi) * tb[1])
            g = w[w.speed_ms >= 2]
            rows.append(dict(period=path.stem[-17:], t0_utc=t0, mean_ms=U,
                             gf_measured=float(np.median(g.gust_ms / g.speed_ms)),
                             gf_mil=gust_factor(spd, FS)))
    r = pd.DataFrame(rows).dropna()
    r["scale_needed"] = (r.gf_measured - 1) / (r.gf_mil - 1)
    out = REPO / "wind" / "data" / "turbulence_validation.csv"
    r.to_csv(out, index=False, float_format="%.3f")

    sys.stdout.reconfigure(encoding="utf-8")
    print("| Period | windows | mean wind (m/s) | measured GF median | MIL synthetic GF median | "
          "sigma scale needed: median (p25-p75) |")
    print("|---|---|---|---|---|---|")
    for p, g in r.groupby("period"):
        q = g.scale_needed.quantile([.25, .5, .75])
        print(f"| {p[:8]}-{p[9:]} | {len(g)} | {g.mean_ms.median():.1f} | {g.gf_measured.median():.2f} | "
              f"{g.gf_mil.median():.2f} | {q[.5]:.2f} ({q[.25]:.2f}-{q[.75]:.2f}) |")
    for lo, hi in [(2, 4), (4, 6), (6, 20)]:
        g = r[(r.mean_ms >= lo) & (r.mean_ms < hi)]
        if len(g):
            print(f"mean {lo}-{hi} m/s: n={len(g)}, measured GF {g.gf_measured.median():.2f}, "
                  f"MIL GF {g.gf_mil.median():.2f}, scale {g.scale_needed.median():.2f}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
