"""Turn measured San Jose wind into a time series a simulator can replay (the "data -> sim wind" step).

    wind(t) = k_h * U_1min(t)  +  R(direction) * [u_turb, v_turb, w_turb](t)

  U_1min   measured SJC 1-minute wind vector (2-minute means), interpolated to the output rate.
  k_h      height/terrain factor that moves the airport wind (10 m, open grass, z0 = 0.03 m) to the flight
           altitude over a garden (z0_site): log profile up to a 60 m blending height, then back down over
           the rougher site (Wieringa-style). Override it with --height-factor once an on-site anemometer
           gives a measured ratio.
  turb     Dryden turbulence, MIL-F-8785C low-altitude form (h < 1000 ft): sigma_w = 0.1 W20,
           sigma_u = sigma_v = sigma_w / (0.177 + 0.000823 h)^0.4, L_w = h, L_u = L_v = h / (0.177 + 0.000823 h)^1.2
           (h, L in ft), advected past the drone at the mean wind speed (Taylor's frozen turbulence).
           --turb data rescales sigma so that the synthetic per-minute 5-s gust factor matches the one SJC
           measured in the same window (the airport value: a lower bound for a garden among houses).

Usage:
  python wind/tools/make_wind_profile.py --start "2026-10-12 14:00" --duration 900 --alt 5
  python wind/tools/make_wind_profile.py --start "2025-12-03 09:30" --turb data --ti-scale 2

Output: <name>.csv with t_s, wind_e, wind_n, wind_u (ENU, m/s, velocity of the air; PX4 NED is n, e, -u),
speed, from_deg; and <name>.json with every input, the derived sigmas and the gust-factor check.
"""
import argparse
import json
import pathlib
import sys

import numpy as np
import pandas as pd
from scipy import signal

REPO = pathlib.Path(__file__).resolve().parents[2]
DATA = REPO / "reference" / "08_wind_simulation" / "data"
TZ = "America/Los_Angeles"
FT = 0.3048


def height_factor(z, z0_site, d_site=0.0, z_ref=10.0, z0_ref=0.03, z_blend=60.0):
    up = np.log(z_blend / z0_ref) / np.log(z_ref / z0_ref)
    down = np.log((z - d_site) / z0_site) / np.log((z_blend - d_site) / z0_site)
    return up * down


def load_window(path, t0, t1):
    df = pd.read_csv(path, parse_dates=["time_utc"]).dropna(subset=["speed_ms", "dir_deg"])
    df = df[(df.time_utc >= t0 - pd.Timedelta("3min")) & (df.time_utc <= t1 + pd.Timedelta("3min"))]
    if len(df) < 0.7 * (t1 - t0).total_seconds() / 60:
        sys.exit(f"too few 1-minute records between {t0} and {t1} ({len(df)}); pick another window")
    th = np.deg2rad(df.dir_deg.to_numpy())
    df["e"] = -df.speed_ms * np.sin(th)  # air moves toward dir + 180 deg
    df["n"] = -df.speed_ms * np.cos(th)
    return df


def dryden(n, fs, V, sigma, L, rng):
    """Unit-shaped Dryden u, v, w series (ENU-free, longitudinal/lateral/vertical), each scaled to its sigma."""
    out = []
    for comp, s, l in zip("uvw", sigma, L):
        T = l / V
        if comp == "u":
            b, a = [1.0], [T, 1.0]
        else:
            b, a = [np.sqrt(3) * T, 1.0], np.polymul([T, 1.0], [T, 1.0])
        bd, ad = signal.bilinear(b, a, fs)
        x = signal.lfilter(bd, ad, rng.standard_normal(n + int(20 * T * fs)))[-n:]  # drop the start-up
        out.append(s * (x - x.mean()) / x.std())
    return np.array(out)


def gust_factor(speed, fs, minute_len=60, gust_len=5, mean_len=120):
    """Median over minutes of (peak 5-s mean in the minute) / (2-min mean ending at that minute), like ASOS."""
    s = pd.Series(speed)
    g5 = s.rolling(int(gust_len * fs)).mean()
    m2 = s.rolling(int(mean_len * fs)).mean()
    per = int(minute_len * fs)
    idx = np.arange(int(mean_len * fs), len(s), per)
    gf = [g5.iloc[i - per:i].max() / m2.iloc[i] for i in idx if m2.iloc[i] >= 1.0]
    return float(np.median(gf)) if gf else float("nan")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", required=True, help='local time, e.g. "2026-10-12 14:00"')
    ap.add_argument("--duration", type=float, default=900, help="seconds")
    ap.add_argument("--alt", type=float, default=5.0, help="flight altitude AGL, m")
    ap.add_argument("--z0-site", type=float, default=0.5, help="site roughness length, m (suburban 0.3-1.0)")
    ap.add_argument("--d-site", type=float, default=0.0, help="site displacement height, m")
    ap.add_argument("--height-factor", type=float, help="measured site/SJC mean-wind ratio (overrides log law)")
    ap.add_argument("--turb", choices=["mil", "data", "none"], default="mil")
    ap.add_argument("--ti-scale", type=float, default=1.0, help="multiply turbulence sigmas (sensitivity sweeps)")
    ap.add_argument("--rate", type=float, default=50.0, help="output rate, Hz")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--data", type=pathlib.Path, help="SJC 1-minute CSV (default: newest that covers --start)")
    ap.add_argument("--out", type=pathlib.Path, default=DATA / "profiles")
    a = ap.parse_args()

    t0 = pd.Timestamp(a.start, tz=TZ).tz_convert("UTC")
    t1 = t0 + pd.Timedelta(seconds=a.duration)
    if a.data is None:
        for p in sorted(DATA.glob("iem_1min_SJC_*.csv"), reverse=True):
            s, e = p.stem.split("_")[-2:]
            if pd.Timestamp(s, tz="UTC") <= t0 and t1 <= pd.Timestamp(e, tz="UTC") + pd.Timedelta("1D"):
                a.data = p
                break
        else:
            sys.exit("no SJC 1-minute file covers that window; run fetch_wind.py first")
    df = load_window(a.data, t0, t1)

    fs, n = a.rate, int(a.duration * a.rate)
    t = np.arange(n) / fs
    tm = (df.time_utc - t0).dt.total_seconds().to_numpy()
    kh = a.height_factor or height_factor(a.alt, a.z0_site, a.d_site)
    mean_e, mean_n = kh * np.interp(t, tm, df.e), kh * np.interp(t, tm, df.n)

    U = float(np.hypot(mean_e.mean(), mean_n.mean()))           # vector-mean speed at altitude
    U_scalar = float(np.hypot(mean_e, mean_n).mean())
    psi = np.arctan2(mean_n.mean(), mean_e.mean())             # direction the air moves toward (ENU angle)
    h_ft = max(a.alt, 3.0) / FT                                # spec is not meant for the first few metres
    w20 = height_factor(20 * FT, a.z0_site, a.d_site) / kh * U_scalar if a.height_factor is None else U_scalar
    sig_w = 0.1 * w20
    sig_u = sig_w / (0.177 + 0.000823 * h_ft) ** 0.4
    L_u = h_ft / (0.177 + 0.000823 * h_ft) ** 1.2 * FT
    L_w = h_ft * FT
    sigma = np.array([sig_u, sig_u, sig_w]) * a.ti_scale
    L = np.array([L_u, L_u, L_w])
    V = max(U_scalar, 1.0)

    wnd = (df.set_index("time_utc").loc[t0:t1])
    gf_meas = float(np.median(wnd.gust_ms[wnd.speed_ms >= 2] / wnd.speed_ms[wnd.speed_ms >= 2])) \
        if (wnd.speed_ms >= 2).sum() >= 3 else float("nan")

    def build(sig):
        if a.turb == "none":
            return np.zeros((3, n))
        return dryden(n, fs, V, sig, L, rng=np.random.default_rng(a.seed))

    turb = build(sigma)
    speed_of = lambda tb: np.hypot(mean_e + np.cos(psi) * tb[0] - np.sin(psi) * tb[1],
                                   mean_n + np.sin(psi) * tb[0] + np.cos(psi) * tb[1])
    gf_mil = gust_factor(speed_of(turb), fs)
    if a.turb == "data":
        if not np.isfinite(gf_meas) or not np.isfinite(gf_mil) or gf_mil <= 1.0:
            sys.exit("cannot calibrate: window too calm (needs >= 3 minutes with mean >= 2 m/s)")
        sigma = sigma * (gf_meas - 1.0) / (gf_mil - 1.0)
        turb = build(sigma)
    gf_out = gust_factor(speed_of(turb), fs)

    we = mean_e + np.cos(psi) * turb[0] - np.sin(psi) * turb[1]
    wn = mean_n + np.sin(psi) * turb[0] + np.cos(psi) * turb[1]
    wu = turb[2]
    spd = np.hypot(we, wn)
    frm = (np.degrees(np.arctan2(-we, -wn)) + 360) % 360

    a.out.mkdir(parents=True, exist_ok=True)
    name = f"sjc_{pd.Timestamp(a.start):%Y%m%d_%H%M}_{int(a.duration)}s_{a.alt:g}m_{a.turb}"
    pd.DataFrame({"t_s": t, "wind_e": we, "wind_n": wn, "wind_u": wu, "speed": spd, "from_deg": frm}) \
        .to_csv(a.out / f"{name}.csv", index=False, float_format="%.3f")
    meta = {
        "source_file": a.data.name, "start_local": a.start, "start_utc": str(t0), "duration_s": a.duration,
        "rate_hz": fs, "frame": "ENU, velocity of the air (m/s); PX4 NED = (n, e, -u)",
        "alt_m": a.alt, "z0_site_m": a.z0_site, "d_site_m": a.d_site,
        "height_factor": round(kh, 3), "height_factor_source": "measured" if a.height_factor else "log law",
        "sjc_10m_mean_speed_ms": round(float(wnd.speed_ms.mean()), 2),
        "sjc_10m_max_gust_ms": round(float(wnd.gust_ms.max()), 2),
        "sjc_from_deg_vector_mean": round(float((np.degrees(np.arctan2(-wnd.e.mean(), -wnd.n.mean())) + 360)
                                                % 360), 0),
        "site_mean_speed_ms": round(U_scalar, 2), "W20_ms": round(float(w20), 2),
        "turbulence": a.turb, "ti_scale": a.ti_scale,
        "sigma_uvw_ms": [round(float(s), 3) for s in sigma], "L_uvw_m": [round(float(x), 1) for x in L],
        "advection_speed_ms": round(V, 2),
        "surface_layer_TI_estimate": round(0.96 / np.log((a.alt - a.d_site) / a.z0_site), 2),
        "gust_factor": {k: round(v, 3) if np.isfinite(v) else None for k, v in
                        [("sjc_measured_median", gf_meas), ("synthetic_mil", gf_mil), ("synthetic_output", gf_out)]},
        "seed": a.seed,
    }
    (a.out / f"{name}.json").write_text(json.dumps(meta, indent=2))
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(meta, indent=2))
    print(f"wrote {a.out / name}.csv ({n} rows)")


if __name__ == "__main__":
    main()
