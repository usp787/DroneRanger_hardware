#!/usr/bin/env python
"""Pass/fail checks for the wind smoke test, from the ground-truth log written by WindDrag.

    python check_smoke.py $RUN_DIR/sim_log.csv          # prints a table, writes <log>.summary.json

The checks assume the `smoke` profile (wind_publisher.SMOKE_SCHEDULE) and a vehicle that took off and held
position. The thresholds are loose: they ask "does the wind reach the vehicle with the right sign and does PX4
react sensibly?", not "is the response quantitatively right" (that needs real flight data later).
"""
import argparse
import json
import pathlib
import sys

import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from wind_publisher import SMOKE_SCHEDULE, Schedule  # noqa: E402


def window(df, a, b):
    return df[(df.t_rel >= a) & (df.t_rel < b)]


def run_checks(log_path):
    df = pd.read_csv(log_path)
    checks = []

    def check(name, ok, detail):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    flown = df.dropna(subset=["t_rel"])
    check("wind clock started (vehicle climbed above the trigger height)", len(flown) > 0,
          f"{len(flown)} logged rows after the trigger")
    if flown.empty:
        return checks
    profile = Schedule(SMOKE_SCHEDULE)
    expected = np.array([profile.wind_enu(t) for t in flown.t_rel])
    err = np.abs(flown[["wind_e", "wind_n", "wind_u"]].to_numpy() - expected).max()
    check("logged wind equals the dummy profile", err < 1e-3, f"max |logged - expected| = {err:.2e} m/s")
    covered = flown.t_rel.max()
    check("whole profile simulated", covered >= profile.duration - 0.5, f"t_rel reached {covered:.1f} s")

    R = Rotation.from_quat(df[["qx", "qy", "qz", "qw"]].to_numpy())
    body_z = R.apply([0.0, 0.0, 1.0])                 # thrust axis in ENU
    df["bz_e"], df["bz_n"] = body_z[:, 0], body_z[:, 1]
    df["tilt_deg"] = np.degrees(np.arccos(np.clip(body_z[:, 2], -1, 1)))

    calm = window(df, 5, 15)
    hover = calm[["pos_e", "pos_n", "pos_u"]].mean().to_numpy()
    df["err_h"] = np.hypot(df.pos_e - hover[0], df.pos_n - hover[1])
    step_early, step_late = window(df, 15, 20), window(df, 25, 35)
    recover, gust = window(df, 45, 50), window(df, 55, 80)
    profile_rows = window(df, 0, profile.duration)

    f_e, f_h = step_late.f_e.mean(), np.hypot(step_late.f_e.mean(), step_late.f_n.mean())
    check("step wind pushes the vehicle toward +East", f_e > 0.3 and f_e / max(f_h, 1e-9) > 0.8,
          f"mean drag force E {f_e:.2f} N, N {step_late.f_n.mean():.2f} N")
    lean = (calm.bz_e.mean() - step_late.bz_e.mean())
    lean_deg = np.degrees(np.arcsin(np.clip(lean, -1, 1)))
    check("PX4 leans into the step wind (thrust axis tilts toward -East)", lean_deg > 1.0,
          f"extra lean {lean_deg:.1f} deg (calm tilt {calm.tilt_deg.mean():.1f}, step tilt {step_late.tilt_deg.mean():.1f})")
    push = (step_early.pos_e - hover[0]).max()
    check("vehicle is displaced downwind at the step onset", push > 0.02, f"peak East displacement {push:.2f} m")
    check("PX4 holds position during the step", step_late.err_h.mean() < 0.5,
          f"mean horizontal error {step_late.err_h.mean():.2f} m in the last 10 s of the step")
    check("PX4 recovers after the step", recover.err_h.mean() < 0.3,
          f"mean horizontal error {recover.err_h.mean():.2f} m, 10-15 s after the step")
    r = np.corrcoef(gust.wind_n, gust.f_n)[0, 1] if len(gust) > 10 else float("nan")
    check("drag force follows the gusty wind", r > 0.5, f"corr(wind_n, force_n) = {r:.2f}")
    check("no divergence during the profile", profile_rows.err_h.max() < 2.0 and
          (profile_rows.pos_u - hover[2]).abs().max() < 1.0,
          f"max horizontal error {profile_rows.err_h.max():.2f} m, "
          f"max altitude error {(profile_rows.pos_u - hover[2]).abs().max():.2f} m")
    return checks


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", type=pathlib.Path)
    a = ap.parse_args()
    checks = run_checks(a.log)
    ok = all(c["pass"] for c in checks)
    for c in checks:
        print(f"{'PASS' if c['pass'] else 'FAIL'}  {c['check']}: {c['detail']}")
    print("SMOKE TEST", "PASSED" if ok else "FAILED")
    pathlib.Path(str(a.log) + ".summary.json").write_text(json.dumps({"passed": ok, "checks": checks}, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
