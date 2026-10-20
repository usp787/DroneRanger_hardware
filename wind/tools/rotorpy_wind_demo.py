"""End-to-end check on a laptop CPU: measured San Jose wind -> simulator -> scripted patrol loop -> metrics.

This is a pipeline check, not an X500 prediction. RotorPy (pip install rotorpy) flies an X500-like quadrotor
with its own SE(3) controller (not PX4) around a garden-sized square at 5 m while a wind profile written by
make_wind_profile.py is replayed. RotorPy computes the aerodynamic wrench from the air-relative velocity,
so the replayed wind enters the physics the same way it would in Pegasus or Gazebo.

Usage:
  python wind/tools/rotorpy_wind_demo.py <profile.csv> [<profile.csv> ...] [--loops 3] [--out wind/data]

Writes <out>/rotorpy_demo_results.csv (one row per profile plus a no-wind baseline) and prints a table.
"""
import argparse
import pathlib
import sys

import numpy as np
import pandas as pd
from rotorpy.controllers.quadrotor_control import SE3Control
from rotorpy.environments import Environment
from rotorpy.trajectories.minsnap import MinSnap
from rotorpy.vehicles.multirotor import Multirotor
from rotorpy.wind.default_winds import NoWind

REPO = pathlib.Path(__file__).resolve().parents[2]
d = 0.25  # X500: 500 mm motor-to-motor diagonal

# Mass, inertia and rotor constants from PX4's Gazebo x500 model (PX4-gazebo-models, models/x500_base and
# models/x500, retrieved 2026-10-19); mass raised to 2.1 kg for the Jetson payload. Body drag is an
# assumption: 0.5 * rho * Cd * A with A = 0.04 m^2, Cd = 1.0.
X500 = {
    'mass': 2.1, 'Ixx': 0.02167, 'Iyy': 0.02167, 'Izz': 0.04, 'Ixy': 0.0, 'Iyz': 0.0, 'Ixz': 0.0,
    'num_rotors': 4, 'rotor_radius': 0.127,
    'rotor_pos': {'r1': d * np.array([0.70710678118, 0.70710678118, 0]),
                  'r2': d * np.array([0.70710678118, -0.70710678118, 0]),
                  'r3': d * np.array([-0.70710678118, -0.70710678118, 0]),
                  'r4': d * np.array([-0.70710678118, 0.70710678118, 0])},
    'rotor_directions': np.array([1, -1, 1, -1]), 'rI': np.array([0, 0, 0]),
    'c_Dx': 0.024, 'c_Dy': 0.024, 'c_Dz': 0.048,
    'k_eta': 8.54858e-06, 'k_m': 8.54858e-06 * 0.016, 'k_d': 8.06428e-05, 'k_z': 0.0, 'k_h': 0.0,
    'k_flap': 0.0,
    'tau_m': 0.0125, 'rotor_speed_min': 0, 'rotor_speed_max': 1000, 'motor_noise_std': 0.0,
    'k_w': 1, 'k_v': 10, 'kp_att': 544, 'kd_att': 46.64,
}


class ReplayWind:
    """RotorPy wind profile that replays a make_wind_profile.py CSV (ENU = RotorPy x, y, z)."""

    def __init__(self, path):
        df = pd.read_csv(path)
        self.t, self.w = df.t_s.to_numpy(), df[["wind_e", "wind_n", "wind_u"]].to_numpy()

    def update(self, t, position):
        return np.array([np.interp(t, self.t, self.w[:, i]) for i in range(3)])


def patrol(loops, side=8.0, alt=5.0, speed=1.0):
    corners = [(0, 0), (side, 0), (side, side), (0, side)]
    pts = [(x, y, alt) for _ in range(loops) for x, y in corners] + [(0, 0, alt)]
    return MinSnap(points=np.array(pts, dtype=float), v_avg=speed, verbose=False)


def fly(wind, loops):
    traj = patrol(loops)
    hover = np.sqrt(X500['mass'] * 9.81 / (4 * X500['k_eta']))
    x0 = {'x': np.array([0.0, 0.0, 5.0]), 'v': np.zeros(3), 'q': np.array([0, 0, 0, 1.0]), 'w': np.zeros(3),
          'wind': np.zeros(3), 'rotor_speeds': np.full(4, hover)}
    env = Environment(vehicle=Multirotor(X500, initial_state=x0), controller=SE3Control(X500),
                      trajectory=traj, wind_profile=wind, sim_rate=200)
    r = env.run(t_final=traj.t_keyframes[-1] + 2.0, plot=False, animate_bool=False, verbose=False)
    err = np.linalg.norm(r['state']['x'] - r['flat']['x'], axis=1)
    q = r['state']['q']                                   # [i, j, k, w]
    tilt = np.degrees(np.arccos(np.clip(1 - 2 * (q[:, 0] ** 2 + q[:, 1] ** 2), -1, 1)))
    rs = r['control']['cmd_motor_speeds']
    air = np.linalg.norm(r['state']['wind'], axis=1)
    return dict(duration_s=round(float(r['time'][-1]), 1), wind_mean_ms=air.mean(), wind_max_ms=air.max(),
                rmse_m=float(np.sqrt((err ** 2).mean())), max_err_m=float(err.max()),
                p95_err_m=float(np.percentile(err, 95)), mean_tilt_deg=float(tilt.mean()),
                max_tilt_deg=float(tilt.max()),
                rotor_saturation_pct=float(100 * (rs >= 0.999 * X500['rotor_speed_max']).any(axis=1).mean()),
                mean_rotor_frac=float(rs.mean() / X500['rotor_speed_max']), exit=str(r['exit'].value))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("profiles", nargs="+", type=pathlib.Path)
    ap.add_argument("--loops", type=int, default=3)
    ap.add_argument("--out", type=pathlib.Path, default=REPO / "wind" / "data")
    a = ap.parse_args()
    rows = [dict(profile="no wind", **fly(NoWind(), a.loops))]
    for p in a.profiles:
        rows.append(dict(profile=p.stem, **fly(ReplayWind(p), a.loops)))
    df = pd.DataFrame(rows)
    a.out.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.out / "rotorpy_demo_results.csv", index=False, float_format="%.3f")
    sys.stdout.reconfigure(encoding="utf-8")
    print(df.to_markdown(index=False, floatfmt=".2f"))


if __name__ == "__main__":
    main()
